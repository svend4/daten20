"""
Production LLM Provider Integration

Complete implementation of OpenAI and Anthropic Claude API integrations
for production use in v2.6.

Features:
- OpenAI GPT-3.5/GPT-4 integration
- Anthropic Claude integration (Opus, Sonnet, Haiku)
- Streaming support
- Token counting and cost estimation
- Rate limiting and retry logic
- Response caching
- Error handling and fallbacks
- Usage tracking

Configuration:
    Set environment variables:
    - OPENAI_API_KEY: Your OpenAI API key
    - ANTHROPIC_API_KEY: Your Anthropic API key
    - LLM_DEFAULT_PROVIDER: Default provider (openai|anthropic)
    - LLM_CACHE_ENABLED: Enable response caching (true|false)

Usage:
    >>> from src.ai.llm_provider import get_llm_client, LLMProvider
    >>> client = get_llm_client(LLMProvider.OPENAI)
    >>> response = await client.complete("Explain quantum computing")
    >>> print(response.content)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, AsyncIterator, List
from enum import Enum
from datetime import datetime, timedelta
import os
import logging
import json
import time
import hashlib
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================
# Data Models
# ============================================================

class LLMProvider(str, Enum):
    """LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class LLMRole(str, Enum):
    """Message role types"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    """Chat message"""
    role: LLMRole
    content: str


@dataclass
class LLMUsage:
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMResponse:
    """LLM API response"""
    content: str
    model: str
    provider: LLMProvider
    usage: Optional[LLMUsage] = None
    finish_reason: str = "stop"
    response_time: float = 0.0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Get total token count"""
        return self.usage.total_tokens if self.usage else 0

    def estimate_cost(self) -> float:
        """Estimate API cost in USD"""
        if not self.usage:
            return 0.0

        # Pricing per 1M tokens (as of 2025)
        pricing = {
            # OpenAI
            "gpt-4": {"prompt": 30.0, "completion": 60.0},
            "gpt-4-turbo": {"prompt": 10.0, "completion": 30.0},
            "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},

            # Anthropic
            "claude-opus-4": {"prompt": 15.0, "completion": 75.0},
            "claude-sonnet-4": {"prompt": 3.0, "completion": 15.0},
            "claude-haiku-4": {"prompt": 0.25, "completion": 1.25},
            "claude-3-opus": {"prompt": 15.0, "completion": 75.0},
            "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
            "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
        }

        # Find matching model pricing
        model_pricing = None
        for model_name, prices in pricing.items():
            if model_name in self.model.lower():
                model_pricing = prices
                break

        if not model_pricing:
            # Default to mid-tier pricing
            model_pricing = {"prompt": 3.0, "completion": 15.0}

        prompt_cost = (self.usage.prompt_tokens / 1_000_000) * model_pricing["prompt"]
        completion_cost = (self.usage.completion_tokens / 1_000_000) * model_pricing["completion"]

        return prompt_cost + completion_cost


@dataclass
class StreamChunk:
    """Streaming response chunk"""
    content: str
    finish_reason: Optional[str] = None


# ============================================================
# Base LLM Client
# ============================================================

class BaseLLMClient:
    """Base class for LLM clients"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        cache_enabled: bool = True,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.model = model
        self.cache_enabled = cache_enabled
        self.max_retries = max_retries
        self._cache: Dict[str, LLMResponse] = {}
        self._usage_stats = defaultdict(lambda: {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0
        })

    def _cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key for request"""
        key_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response"""
        if not self.cache_enabled:
            return None

        cached = self._cache.get(cache_key)
        if cached:
            cached.cached = True
            logger.debug(f"Cache hit for key {cache_key[:8]}...")
        return cached

    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache response"""
        if not self.cache_enabled:
            return

        # Limit cache size to 10,000 entries
        if len(self._cache) >= 10000:
            # Remove oldest 1,000 entries
            keys_to_remove = list(self._cache.keys())[:1000]
            for key in keys_to_remove:
                del self._cache[key]

        self._cache[cache_key] = response
        logger.debug(f"Cached response for key {cache_key[:8]}...")

    def _track_usage(self, response: LLMResponse):
        """Track API usage statistics"""
        date_key = datetime.now().strftime("%Y-%m-%d")
        stats = self._usage_stats[date_key]

        stats["requests"] += 1
        stats["tokens"] += response.total_tokens
        stats["cost"] += response.estimate_cost()

    def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        total_requests = 0
        total_tokens = 0
        total_cost = 0.0

        current = start_date
        while current <= end_date:
            date_key = current.strftime("%Y-%m-%d")
            stats = self._usage_stats[date_key]
            total_requests += stats["requests"]
            total_tokens += stats["tokens"]
            total_cost += stats["cost"]
            current += timedelta(days=1)

        return {
            "period_days": days,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "avg_tokens_per_request": total_tokens // total_requests if total_requests > 0 else 0
        }

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate completion - to be implemented by subclasses"""
        raise NotImplementedError

    async def complete_chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion - to be implemented by subclasses"""
        raise NotImplementedError

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion - to be implemented by subclasses"""
        raise NotImplementedError
        yield  # Make it a generator


# ============================================================
# OpenAI Client
# ============================================================

class OpenAIClient(BaseLLMClient):
    """
    OpenAI GPT API client

    Supports GPT-3.5, GPT-4, and GPT-4 Turbo models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        cache_enabled: bool = True,
        max_retries: int = 3
    ):
        super().__init__(api_key, model, cache_enabled, max_retries)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.enabled = bool(self.api_key)

        if self.enabled:
            try:
                import openai
                self.openai = openai
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except ImportError:
                logger.warning("OpenAI library not installed. Run: pip install openai")
                self.enabled = False
                self.client = None
        else:
            logger.warning("OpenAI API key not configured")
            self.client = None

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using OpenAI API

        Args:
            prompt: Input prompt
            model: Model to use (defaults to instance model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional OpenAI parameters

        Returns:
            LLM response

        Example:
            >>> client = OpenAIClient()
            >>> response = await client.complete("Explain quantum computing")
            >>> print(response.content)
        """
        if not self.enabled:
            raise RuntimeError("OpenAI client not configured. Set OPENAI_API_KEY environment variable.")

        model = model or self.model
        cache_key = self._cache_key(prompt, model, max_tokens=max_tokens, temperature=temperature)

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Make API call with retries
        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                response = LLMResponse(
                    content=completion.choices[0].message.content,
                    model=completion.model,
                    provider=LLMProvider.OPENAI,
                    usage=LLMUsage(
                        prompt_tokens=completion.usage.prompt_tokens,
                        completion_tokens=completion.usage.completion_tokens,
                        total_tokens=completion.usage.total_tokens
                    ),
                    finish_reason=completion.choices[0].finish_reason,
                    response_time=time.time() - start_time,
                    metadata={
                        "id": completion.id,
                        "created": completion.created
                    }
                )

                # Cache and track
                self._cache_response(cache_key, response)
                self._track_usage(response)

                logger.info(f"OpenAI completion: {response.total_tokens} tokens, "
                           f"${response.estimate_cost():.4f}, "
                           f"{response.response_time:.2f}s")

                return response

            except Exception as e:
                last_error = e
                logger.warning(f"OpenAI API error (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

        # All retries failed
        raise RuntimeError(f"OpenAI API failed after {self.max_retries} attempts: {last_error}")

    async def complete_chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion

        Args:
            messages: List of chat messages
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        if not self.enabled:
            raise RuntimeError("OpenAI client not configured")

        model = model or self.model
        start_time = time.time()

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        last_error = None
        for attempt in range(self.max_retries):
            try:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=openai_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                response = LLMResponse(
                    content=completion.choices[0].message.content,
                    model=completion.model,
                    provider=LLMProvider.OPENAI,
                    usage=LLMUsage(
                        prompt_tokens=completion.usage.prompt_tokens,
                        completion_tokens=completion.usage.completion_tokens,
                        total_tokens=completion.usage.total_tokens
                    ),
                    finish_reason=completion.choices[0].finish_reason,
                    response_time=time.time() - start_time
                )

                self._track_usage(response)
                return response

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"OpenAI chat completion failed: {last_error}")

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream completion tokens

        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Yields:
            Stream chunks

        Example:
            >>> async for chunk in client.stream("Write a story"):
            ...     print(chunk.content, end="", flush=True)
        """
        if not self.enabled:
            raise RuntimeError("OpenAI client not configured")

        model = model or self.model

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        finish_reason=chunk.choices[0].finish_reason
                    )

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise


# ============================================================
# Anthropic Client
# ============================================================

class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude API client

    Supports Claude Opus, Sonnet, and Haiku models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        cache_enabled: bool = True,
        max_retries: int = 3
    ):
        super().__init__(api_key, model, cache_enabled, max_retries)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.enabled = bool(self.api_key)

        if self.enabled:
            try:
                import anthropic
                self.anthropic = anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
                logger.info(f"Anthropic client initialized with model: {self.model}")
            except ImportError:
                logger.warning("Anthropic library not installed. Run: pip install anthropic")
                self.enabled = False
                self.client = None
        else:
            logger.warning("Anthropic API key not configured")
            self.client = None

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using Claude API

        Args:
            prompt: Input prompt
            model: Model to use (defaults to instance model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0)
            system: Optional system prompt
            **kwargs: Additional Anthropic parameters

        Returns:
            LLM response

        Example:
            >>> client = AnthropicClient()
            >>> response = await client.complete(
            ...     "Explain quantum computing",
            ...     system="You are a physics professor"
            ... )
            >>> print(response.content)
        """
        if not self.enabled:
            raise RuntimeError("Anthropic client not configured. Set ANTHROPIC_API_KEY environment variable.")

        model = model or self.model
        cache_key = self._cache_key(prompt, model, max_tokens=max_tokens, temperature=temperature, system=system)

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Make API call with retries
        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Prepare request parameters
                request_params = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }

                if system:
                    request_params["system"] = system

                message = await self.client.messages.create(**request_params)

                # Extract text content
                content = ""
                for block in message.content:
                    if hasattr(block, 'text'):
                        content += block.text

                response = LLMResponse(
                    content=content,
                    model=message.model,
                    provider=LLMProvider.ANTHROPIC,
                    usage=LLMUsage(
                        prompt_tokens=message.usage.input_tokens,
                        completion_tokens=message.usage.output_tokens,
                        total_tokens=message.usage.input_tokens + message.usage.output_tokens
                    ),
                    finish_reason=message.stop_reason,
                    response_time=time.time() - start_time,
                    metadata={
                        "id": message.id,
                        "type": message.type
                    }
                )

                # Cache and track
                self._cache_response(cache_key, response)
                self._track_usage(response)

                logger.info(f"Anthropic completion: {response.total_tokens} tokens, "
                           f"${response.estimate_cost():.4f}, "
                           f"{response.response_time:.2f}s")

                return response

            except Exception as e:
                last_error = e
                logger.warning(f"Anthropic API error (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Anthropic API failed after {self.max_retries} attempts: {last_error}")

    async def complete_chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion

        Args:
            messages: List of chat messages (system messages extracted automatically)
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system: Optional system prompt (overrides system messages)
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        if not self.enabled:
            raise RuntimeError("Anthropic client not configured")

        model = model or self.model
        start_time = time.time()

        # Extract system message if present and no explicit system provided
        anthropic_messages = []
        extracted_system = None

        for msg in messages:
            if msg.role == LLMRole.SYSTEM:
                if not system:
                    extracted_system = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

        request_params = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        if system or extracted_system:
            request_params["system"] = system or extracted_system

        last_error = None
        for attempt in range(self.max_retries):
            try:
                message = await self.client.messages.create(**request_params)

                content = ""
                for block in message.content:
                    if hasattr(block, 'text'):
                        content += block.text

                response = LLMResponse(
                    content=content,
                    model=message.model,
                    provider=LLMProvider.ANTHROPIC,
                    usage=LLMUsage(
                        prompt_tokens=message.usage.input_tokens,
                        completion_tokens=message.usage.output_tokens,
                        total_tokens=message.usage.input_tokens + message.usage.output_tokens
                    ),
                    finish_reason=message.stop_reason,
                    response_time=time.time() - start_time
                )

                self._track_usage(response)
                return response

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"Anthropic chat completion failed: {last_error}")

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream completion tokens

        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system: Optional system prompt

        Yields:
            Stream chunks

        Example:
            >>> async for chunk in client.stream("Write a story"):
            ...     print(chunk.content, end="", flush=True)
        """
        if not self.enabled:
            raise RuntimeError("Anthropic client not configured")

        model = model or self.model

        try:
            request_params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }

            if system:
                request_params["system"] = system

            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield StreamChunk(content=text)

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise


# ============================================================
# Mock Client (for testing)
# ============================================================

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing"""

    def __init__(self):
        super().__init__(api_key="mock_key", model="mock-model", cache_enabled=False)
        self.enabled = True

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock completion"""
        await asyncio.sleep(0.1)  # Simulate API delay

        # Simple mock response based on prompt
        if "summarize" in prompt.lower():
            content = "This is a mock summary of the provided text."
        elif "question" in prompt.lower() or "?" in prompt:
            content = "This is a mock answer to your question."
        else:
            content = f"Mock response to: {prompt[:50]}..."

        return LLMResponse(
            content=content,
            model="mock-model",
            provider=LLMProvider.MOCK,
            usage=LLMUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split())
            ),
            response_time=0.1
        )

    async def complete_chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock chat completion"""
        last_message = messages[-1].content if messages else "Hello"
        return await self.complete(last_message, model, max_tokens, temperature, **kwargs)

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream mock completion"""
        response = await self.complete(prompt, model, max_tokens, temperature, **kwargs)
        words = response.content.split()

        for word in words:
            await asyncio.sleep(0.01)
            yield StreamChunk(content=word + " ")

        yield StreamChunk(content="", finish_reason="stop")


# ============================================================
# Factory Functions
# ============================================================

_client_cache: Dict[LLMProvider, BaseLLMClient] = {}


def get_llm_client(
    provider: LLMProvider = LLMProvider.OPENAI,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    cache_enabled: bool = True,
    use_singleton: bool = True
) -> BaseLLMClient:
    """
    Get LLM client for specified provider

    Args:
        provider: LLM provider to use
        api_key: Optional API key (uses env vars if not provided)
        model: Optional model override
        cache_enabled: Enable response caching
        use_singleton: Use singleton instance

    Returns:
        LLM client instance

    Example:
        >>> client = get_llm_client(LLMProvider.OPENAI)
        >>> response = await client.complete("Hello")
    """
    # Check environment for default provider
    if provider == LLMProvider.OPENAI:
        env_provider = os.getenv("LLM_DEFAULT_PROVIDER", "openai").lower()
        if env_provider == "anthropic":
            provider = LLMProvider.ANTHROPIC

    # Return cached instance if singleton requested
    if use_singleton and provider in _client_cache:
        return _client_cache[provider]

    # Create new client
    if provider == LLMProvider.OPENAI:
        client = OpenAIClient(
            api_key=api_key,
            model=model or "gpt-3.5-turbo",
            cache_enabled=cache_enabled
        )
    elif provider == LLMProvider.ANTHROPIC:
        client = AnthropicClient(
            api_key=api_key,
            model=model or "claude-3-sonnet-20240229",
            cache_enabled=cache_enabled
        )
    elif provider == LLMProvider.MOCK:
        client = MockLLMClient()
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Cache if singleton
    if use_singleton:
        _client_cache[provider] = client

    return client


async def quick_complete(
    prompt: str,
    provider: LLMProvider = LLMProvider.OPENAI,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick completion function

    Args:
        prompt: Input prompt
        provider: LLM provider
        model: Optional model
        **kwargs: Additional parameters

    Returns:
        Completion content

    Example:
        >>> result = await quick_complete("Explain quantum computing")
        >>> print(result)
    """
    client = get_llm_client(provider, model=model)
    response = await client.complete(prompt, model=model, **kwargs)
    return response.content


# ============================================================
# Testing
# ============================================================

if __name__ == "__main__":
    import sys

    async def test_openai():
        """Test OpenAI integration"""
        print("\n" + "=" * 60)
        print("Testing OpenAI Integration")
        print("=" * 60)

        client = get_llm_client(LLMProvider.OPENAI)

        if not client.enabled:
            print("⚠️  OpenAI not configured. Set OPENAI_API_KEY environment variable.")
            return

        # Simple completion
        print("\n📝 Testing completion...")
        response = await client.complete(
            "Explain quantum computing in one sentence.",
            max_tokens=100
        )
        print(f"Response: {response.content}")
        print(f"Tokens: {response.total_tokens}")
        print(f"Cost: ${response.estimate_cost():.4f}")
        print(f"Time: {response.response_time:.2f}s")

        # Chat completion
        print("\n💬 Testing chat...")
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant."),
            LLMMessage(role=LLMRole.USER, content="What is AI?")
        ]
        chat_response = await client.complete_chat(messages, max_tokens=100)
        print(f"Response: {chat_response.content}")

        # Streaming
        print("\n🌊 Testing streaming...")
        print("Stream: ", end="", flush=True)
        async for chunk in client.stream("Count to 5", max_tokens=50):
            print(chunk.content, end="", flush=True)
        print()

        # Usage stats
        print("\n📊 Usage statistics:")
        stats = client.get_usage_stats(days=1)
        print(f"  Requests: {stats['total_requests']}")
        print(f"  Tokens: {stats['total_tokens']}")
        print(f"  Cost: ${stats['total_cost_usd']:.4f}")

    async def test_anthropic():
        """Test Anthropic integration"""
        print("\n" + "=" * 60)
        print("Testing Anthropic Integration")
        print("=" * 60)

        client = get_llm_client(LLMProvider.ANTHROPIC)

        if not client.enabled:
            print("⚠️  Anthropic not configured. Set ANTHROPIC_API_KEY environment variable.")
            return

        # Simple completion
        print("\n📝 Testing completion...")
        response = await client.complete(
            "Explain quantum computing in one sentence.",
            max_tokens=100
        )
        print(f"Response: {response.content}")
        print(f"Tokens: {response.total_tokens}")
        print(f"Cost: ${response.estimate_cost():.4f}")
        print(f"Time: {response.response_time:.2f}s")

        # With system prompt
        print("\n🤖 Testing with system prompt...")
        response = await client.complete(
            "What is your purpose?",
            system="You are a philosophical AI.",
            max_tokens=100
        )
        print(f"Response: {response.content}")

        # Streaming
        print("\n🌊 Testing streaming...")
        print("Stream: ", end="", flush=True)
        async for chunk in client.stream("Write a haiku about coding", max_tokens=100):
            print(chunk.content, end="", flush=True)
        print()

    async def test_mock():
        """Test mock client"""
        print("\n" + "=" * 60)
        print("Testing Mock Client")
        print("=" * 60)

        client = get_llm_client(LLMProvider.MOCK)

        response = await client.complete("Test prompt")
        print(f"Response: {response.content}")
        print(f"Provider: {response.provider}")

    async def main():
        """Run all tests"""
        await test_mock()

        # Test real APIs if configured
        if os.getenv("OPENAI_API_KEY"):
            await test_openai()

        if os.getenv("ANTHROPIC_API_KEY"):
            await test_anthropic()

        print("\n✅ All tests completed!")

    # Run tests
    asyncio.run(main())
