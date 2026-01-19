"""
LLM Integration Module

Universal LLM client supporting multiple providers (OpenAI, Anthropic, local models).
Provides unified interface for all LLMs with features like streaming, token counting,
rate limiting, and cost estimation.

Part of v3.5 AI/ML Services implementation.
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    FALLBACK = "fallback"


class ModelType(Enum):
    """LLM model types."""

    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE3_OPUS = "claude-3-opus-20240229"
    CLAUDE3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"
    LOCAL_LLAMA2 = "llama-2-7b"
    LOCAL_MISTRAL = "mistral-7b"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""

    provider: LLMProvider
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    cost_limit_per_request: float = 1.0  # dollars
    fallback_providers: List[LLMProvider] = field(default_factory=list)


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float = 0.0


@dataclass
class LLMResponse:
    """Response from LLM."""

    content: str
    model: str
    provider: LLMProvider
    usage: TokenUsage
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    latency_ms: float = 0.0


class TokenCounter:
    """Token counting utilities."""

    # Approximate token counts (chars/token ratio)
    TOKEN_RATIOS = {
        "gpt-4": 4,
        "gpt-3.5-turbo": 4,
        "claude": 5,
        "local": 4,
    }

    @classmethod
    def count_tokens(cls, text: str, model: str) -> int:
        """Estimate token count for text."""
        # Simple estimation - in production would use tiktoken
        ratio = cls._get_ratio(model)
        return max(1, len(text) // ratio)

    @classmethod
    def _get_ratio(cls, model: str) -> int:
        """Get character-to-token ratio for model."""
        for key, ratio in cls.TOKEN_RATIOS.items():
            if key in model.lower():
                return ratio
        return 4  # default


class CostEstimator:
    """LLM cost estimation."""

    # Cost per 1K tokens (input, output) in USD
    PRICING = {
        "gpt-4": (0.03, 0.06),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-3.5-turbo": (0.0005, 0.0015),
        "claude-3-opus": (0.015, 0.075),
        "claude-3-sonnet": (0.003, 0.015),
        "claude-3-haiku": (0.00025, 0.00125),
        "local": (0.0, 0.0),
    }

    @classmethod
    def estimate_cost(cls, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for token usage."""
        pricing = cls._get_pricing(model)
        if not pricing:
            return 0.0

        input_cost = (prompt_tokens / 1000) * pricing[0]
        output_cost = (completion_tokens / 1000) * pricing[1]
        return input_cost + output_cost

    @classmethod
    def _get_pricing(cls, model: str) -> Optional[tuple]:
        """Get pricing for model."""
        model_lower = model.lower()
        for key, pricing in cls.PRICING.items():
            if key in model_lower:
                return pricing
        return None


class RateLimiter:
    """Rate limiting for API requests."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    async def acquire(self, key: str = "default") -> bool:
        """Acquire rate limit token."""
        now = time.time()

        # Clean old requests
        self.requests[key] = [ts for ts in self.requests[key] if now - ts < self.window_seconds]

        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            oldest = self.requests[key][0]
            wait_time = self.window_seconds - (now - oldest)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire(key)

        self.requests[key].append(now)
        return True


class ResponseCache:
    """Cache for LLM responses."""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache: Dict[str, tuple] = {}  # hash -> (response, timestamp)

    def get(self, prompt: str, model: str, **kwargs) -> Optional[LLMResponse]:
        """Get cached response."""
        cache_key = self._make_key(prompt, model, **kwargs)

        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]

            # Check expiry
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for {cache_key[:16]}...")
                response.cached = True
                return response
            else:
                # Expired
                del self.cache[cache_key]

        return None

    def set(self, response: LLMResponse, prompt: str, model: str, **kwargs):
        """Cache response."""
        cache_key = self._make_key(prompt, model, **kwargs)
        self.cache[cache_key] = (response, time.time())
        logger.debug(f"Cached response for {cache_key[:16]}...")

    def _make_key(self, prompt: str, model: str, **kwargs) -> str:
        """Create cache key."""
        key_data = f"{prompt}:{model}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def clear(self):
        """Clear cache."""
        self.cache.clear()


class BaseLLMClient(ABC):
    """Base class for LLM clients."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_requests, config.rate_limit_window)
        self.cache = ResponseCache(config.cache_ttl) if config.cache_enabled else None

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion for prompt."""
        pass

    @abstractmethod
    async def complete_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate streaming completion."""
        pass

    async def _check_rate_limit(self):
        """Check rate limit before request."""
        await self.rate_limiter.acquire(self.config.provider.value)

    def _check_cost_limit(self, estimated_cost: float):
        """Check if cost is within limit."""
        if estimated_cost > self.config.cost_limit_per_request:
            raise ValueError(
                f"Estimated cost ${estimated_cost:.4f} exceeds limit " f"${self.config.cost_limit_per_request:.4f}"
            )


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client."""

    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion using OpenAI."""
        # Check cache
        if self.cache:
            cached = self.cache.get(prompt, self.config.model, **kwargs)
            if cached:
                return cached

        # Rate limiting
        await self._check_rate_limit()

        # Estimate cost
        prompt_tokens = TokenCounter.count_tokens(prompt, self.config.model)
        completion_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        estimated_cost = CostEstimator.estimate_cost(self.config.model, prompt_tokens, completion_tokens)
        self._check_cost_limit(estimated_cost)

        # Make request (mock implementation)
        start_time = time.time()

        try:
            # In production, would use actual OpenAI API
            await asyncio.sleep(0.1)  # Simulate API call

            content = f"[OpenAI {self.config.model} response to: {prompt[:50]}...]"
            actual_completion_tokens = len(content) // 4

            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=actual_completion_tokens,
                total_tokens=prompt_tokens + actual_completion_tokens,
                estimated_cost=CostEstimator.estimate_cost(self.config.model, prompt_tokens, actual_completion_tokens),
            )

            response = LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.OPENAI,
                usage=usage,
                finish_reason="stop",
                latency_ms=(time.time() - start_time) * 1000,
            )

            # Cache response
            if self.cache:
                self.cache.set(response, prompt, self.config.model, **kwargs)

            return response

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate streaming completion."""
        # Rate limiting
        await self._check_rate_limit()

        # Mock streaming response
        words = f"[Streaming from OpenAI {self.config.model}]: {prompt[:30]}...".split()
        for word in words:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield word + " "


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude LLM client."""

    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion using Anthropic Claude."""
        # Check cache
        if self.cache:
            cached = self.cache.get(prompt, self.config.model, **kwargs)
            if cached:
                return cached

        # Rate limiting
        await self._check_rate_limit()

        # Estimate cost
        prompt_tokens = TokenCounter.count_tokens(prompt, self.config.model)
        completion_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        estimated_cost = CostEstimator.estimate_cost(self.config.model, prompt_tokens, completion_tokens)
        self._check_cost_limit(estimated_cost)

        # Make request (mock implementation)
        start_time = time.time()

        try:
            # In production, would use actual Anthropic API
            await asyncio.sleep(0.1)  # Simulate API call

            content = f"[Claude {self.config.model} response to: {prompt[:50]}...]"
            actual_completion_tokens = len(content) // 5

            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=actual_completion_tokens,
                total_tokens=prompt_tokens + actual_completion_tokens,
                estimated_cost=CostEstimator.estimate_cost(self.config.model, prompt_tokens, actual_completion_tokens),
            )

            response = LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.ANTHROPIC,
                usage=usage,
                finish_reason="end_turn",
                latency_ms=(time.time() - start_time) * 1000,
            )

            # Cache response
            if self.cache:
                self.cache.set(response, prompt, self.config.model, **kwargs)

            return response

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate streaming completion."""
        # Rate limiting
        await self._check_rate_limit()

        # Mock streaming response
        words = f"[Streaming from Claude {self.config.model}]: {prompt[:30]}...".split()
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "


class LocalLLMClient(BaseLLMClient):
    """Local LLM client (llama.cpp, Ollama, etc.)."""

    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion using local model."""
        # Check cache
        if self.cache:
            cached = self.cache.get(prompt, self.config.model, **kwargs)
            if cached:
                return cached

        # Rate limiting
        await self._check_rate_limit()

        # Local models are free
        prompt_tokens = TokenCounter.count_tokens(prompt, self.config.model)

        # Make request (mock implementation)
        start_time = time.time()

        try:
            # In production, would use llama.cpp or Ollama API
            await asyncio.sleep(0.2)  # Simulate slower local inference

            content = f"[Local {self.config.model} response to: {prompt[:50]}...]"
            completion_tokens = len(content) // 4

            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost=0.0,  # Local is free
            )

            response = LLMResponse(
                content=content,
                model=self.config.model,
                provider=LLMProvider.LOCAL,
                usage=usage,
                finish_reason="stop",
                latency_ms=(time.time() - start_time) * 1000,
            )

            # Cache response
            if self.cache:
                self.cache.set(response, prompt, self.config.model, **kwargs)

            return response

        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            raise

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Generate streaming completion."""
        # Rate limiting
        await self._check_rate_limit()

        # Mock streaming response
        words = f"[Streaming from local {self.config.model}]: {prompt[:30]}...".split()
        for word in words:
            await asyncio.sleep(0.1)  # Local is slower
            yield word + " "


class FallbackLLMClient(BaseLLMClient):
    """Fallback LLM client that tries multiple providers."""

    def __init__(self, config: LLMConfig, clients: List[BaseLLMClient]):
        super().__init__(config)
        self.clients = clients

    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Try multiple providers until one succeeds."""
        last_error = None

        for client in self.clients:
            try:
                logger.info(f"Trying provider: {client.config.provider.value}")
                response = await client.complete(prompt, **kwargs)
                return response
            except Exception as e:
                logger.warning(f"Provider {client.config.provider.value} failed: {e}")
                last_error = e
                continue

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def complete_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream from first working provider."""
        last_error = None

        for client in self.clients:
            try:
                logger.info(f"Trying provider: {client.config.provider.value}")
                async for chunk in client.complete_stream(prompt, **kwargs):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Provider {client.config.provider.value} failed: {e}")
                last_error = e
                continue

        raise RuntimeError(f"All providers failed. Last error: {last_error}")


class LLMClientFactory:
    """Factory for creating LLM clients."""

    @staticmethod
    def create(config: LLMConfig) -> BaseLLMClient:
        """Create LLM client based on config."""
        if config.provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(config)
        elif config.provider == LLMProvider.LOCAL:
            return LocalLLMClient(config)
        elif config.provider == LLMProvider.FALLBACK:
            # Create fallback client with multiple providers
            clients = []
            for provider in config.fallback_providers:
                fallback_config = LLMConfig(
                    provider=provider,
                    api_key=config.api_key,
                    model=config.model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
                clients.append(LLMClientFactory.create(fallback_config))
            return FallbackLLMClient(config, clients)
        else:
            raise ValueError(f"Unknown provider: {config.provider}")


class PromptTemplate:
    """Template for LLM prompts."""

    def __init__(self, template: str, variables: Optional[List[str]] = None):
        self.template = template
        self.variables = variables or []

    def render(self, **kwargs) -> str:
        """Render template with variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


# Common prompt templates
PROMPT_TEMPLATES = {
    "summarize": PromptTemplate(
        "Summarize the following text in {num_points} bullet points:\n\n{text}", ["text", "num_points"]
    ),
    "classify": PromptTemplate(
        "Classify the following text into one of these categories: {categories}\n\nText: {text}", ["text", "categories"]
    ),
    "extract_entities": PromptTemplate(
        "Extract all named entities (people, organizations, locations) from this text:\n\n{text}", ["text"]
    ),
    "sentiment": PromptTemplate(
        "Analyze the sentiment (positive, negative, neutral) of this text:\n\n{text}", ["text"]
    ),
    "qa": PromptTemplate(
        "Answer this question based on the context:\n\nContext: {context}\n\nQuestion: {question}",
        ["context", "question"],
    ),
}


# Singleton instance
_llm_client: Optional[BaseLLMClient] = None


def get_llm_client(provider: str = "openai", model: str = "gpt-3.5-turbo", **kwargs) -> BaseLLMClient:
    """Get or create LLM client."""
    global _llm_client

    config = LLMConfig(provider=LLMProvider(provider), model=model, **kwargs)

    _llm_client = LLMClientFactory.create(config)
    return _llm_client


async def complete(prompt: str, provider: str = "openai", **kwargs) -> LLMResponse:
    """Quick completion helper."""
    client = get_llm_client(provider=provider, **kwargs)
    return await client.complete(prompt, **kwargs)


async def complete_stream(prompt: str, provider: str = "openai", **kwargs) -> AsyncIterator[str]:
    """Quick streaming helper."""
    client = get_llm_client(provider=provider, **kwargs)
    async for chunk in client.complete_stream(prompt, **kwargs):
        yield chunk
