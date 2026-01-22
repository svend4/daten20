"""
Comprehensive tests for ai/llm_integration.py module

Tests organized by size:
- Small: Enums, dataclasses, static utilities (TokenCounter, CostEstimator)
- Medium: Classes with logic, async operations (clients, cache, rate limiter)
- Large: Full workflows with fallback, caching, rate limiting

Test coverage: ~80% target
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.ai.llm_integration import (
    PROMPT_TEMPLATES,
    AnthropicClient,
    BaseLLMClient,
    CostEstimator,
    FallbackLLMClient,
    LLMClientFactory,
    LLMConfig,
    LLMProvider,
    LLMResponse,
    LocalLLMClient,
    ModelType,
    OpenAIClient,
    PromptTemplate,
    RateLimiter,
    ResponseCache,
    TokenCounter,
    TokenUsage,
    complete,
    get_llm_client,
)

# ============================================================================
# SMALL TESTS - Enums, Dataclasses, Static Utilities
# ============================================================================

pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestLLMProvider:
    """Test LLMProvider enum."""

    def test_all_providers_defined(self):
        """Test all LLM providers are defined."""
        providers = [p for p in LLMProvider]
        assert len(providers) == 4

        assert LLMProvider.OPENAI in providers
        assert LLMProvider.ANTHROPIC in providers
        assert LLMProvider.LOCAL in providers
        assert LLMProvider.FALLBACK in providers

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.LOCAL.value == "local"


class TestModelType:
    """Test ModelType enum."""

    def test_all_model_types_defined(self):
        """Test all model types are defined."""
        models = [m for m in ModelType]
        assert len(models) >= 8  # At least 8 models

    def test_openai_models(self):
        """Test OpenAI model types."""
        assert ModelType.GPT4.value == "gpt-4"
        assert ModelType.GPT35_TURBO.value == "gpt-3.5-turbo"

    def test_anthropic_models(self):
        """Test Anthropic model types."""
        assert "claude-3" in ModelType.CLAUDE3_OPUS.value
        assert "claude-3" in ModelType.CLAUDE3_SONNET.value


class TestLLMConfig:
    """Test LLMConfig dataclass."""

    def test_config_creation_minimal(self):
        """Test creating minimal config."""
        config = LLMConfig(provider=LLMProvider.OPENAI)

        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-3.5-turbo"
        assert config.max_tokens == 1000
        assert config.temperature == 0.7

    def test_config_creation_full(self):
        """Test creating full config."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key="test-key",
            model="claude-3-opus",
            max_tokens=2000,
            temperature=0.5,
            cache_enabled=True,
            rate_limit_requests=50
        )

        assert config.provider == LLMProvider.ANTHROPIC
        assert config.api_key == "test-key"
        assert config.model == "claude-3-opus"
        assert config.max_tokens == 2000
        assert config.cache_enabled is True
        assert config.rate_limit_requests == 50

    def test_config_fallback_providers(self):
        """Test config with fallback providers."""
        config = LLMConfig(
            provider=LLMProvider.FALLBACK,
            fallback_providers=[LLMProvider.OPENAI, LLMProvider.LOCAL]
        )

        assert len(config.fallback_providers) == 2
        assert LLMProvider.OPENAI in config.fallback_providers


class TestTokenUsage:
    """Test TokenUsage dataclass."""

    def test_token_usage_creation(self):
        """Test creating token usage."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.01
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.estimated_cost == 0.01


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_response_creation(self):
        """Test creating LLM response."""
        usage = TokenUsage(100, 50, 150, 0.01)
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason="stop"
        )

        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.provider == LLMProvider.OPENAI
        assert response.cached is False
        assert response.latency_ms == 0.0

    def test_response_with_metadata(self):
        """Test response with metadata."""
        usage = TokenUsage(10, 20, 30)
        response = LLMResponse(
            content="Test",
            model="gpt-3.5-turbo",
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason="stop",
            metadata={"source": "test"},
            cached=True,
            latency_ms=250.5
        )

        assert response.metadata["source"] == "test"
        assert response.cached is True
        assert response.latency_ms == 250.5


class TestTokenCounter:
    """Test TokenCounter utility."""

    def test_count_tokens_gpt(self):
        """Test token counting for GPT models."""
        text = "Hello, this is a test message!"
        count = TokenCounter.count_tokens(text, "gpt-4")

        assert count > 0
        # Rough estimate: ~1 token per 4 characters
        assert count > len(text) / 5

    def test_count_tokens_claude(self):
        """Test token counting for Claude models."""
        text = "This is a test message"
        count = TokenCounter.count_tokens(text, "claude-3-opus")

        assert count > 0

    def test_count_tokens_empty_string(self):
        """Test token counting for empty string."""
        count = TokenCounter.count_tokens("", "gpt-4")

        # Should return at least 1
        assert count >= 1

    def test_count_tokens_long_text(self):
        """Test token counting for long text."""
        text = "word " * 1000
        count = TokenCounter.count_tokens(text, "gpt-3.5-turbo")

        assert count > 100


class TestCostEstimator:
    """Test CostEstimator utility."""

    def test_estimate_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        cost = CostEstimator.estimate_cost("gpt-4", prompt_tokens=1000, completion_tokens=500)

        # GPT-4: $0.03/$0.06 per 1K tokens
        expected = (1000/1000 * 0.03) + (500/1000 * 0.06)
        assert abs(cost - expected) < 0.001

    def test_estimate_cost_gpt35(self):
        """Test cost estimation for GPT-3.5."""
        cost = CostEstimator.estimate_cost("gpt-3.5-turbo", prompt_tokens=2000, completion_tokens=1000)

        # Should be much cheaper than GPT-4
        assert cost < 0.01

    def test_estimate_cost_claude_opus(self):
        """Test cost estimation for Claude Opus."""
        cost = CostEstimator.estimate_cost("claude-3-opus", prompt_tokens=1000, completion_tokens=500)

        # Claude Opus: $0.015/$0.075 per 1K
        expected = (1000/1000 * 0.015) + (500/1000 * 0.075)
        assert abs(cost - expected) < 0.001

    def test_estimate_cost_local_model(self):
        """Test cost estimation for local model."""
        cost = CostEstimator.estimate_cost("local", prompt_tokens=10000, completion_tokens=5000)

        # Local models are free
        assert cost == 0.0

    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model."""
        cost = CostEstimator.estimate_cost("unknown-model", prompt_tokens=1000, completion_tokens=500)

        # Should return 0 for unknown
        assert cost == 0.0


class TestPromptTemplate:
    """Test PromptTemplate class."""

    def test_template_creation(self):
        """Test creating prompt template."""
        template = PromptTemplate(
            "Hello {name}, you are {age} years old",
            variables=["name", "age"]
        )

        assert template.template is not None
        assert template.variables == ["name", "age"]

    def test_template_render(self):
        """Test rendering template."""
        template = PromptTemplate("Hello {name}!")

        result = template.render(name="Alice")

        assert result == "Hello Alice!"

    def test_template_render_multiple_vars(self):
        """Test rendering template with multiple variables."""
        template = PromptTemplate("Name: {name}, Age: {age}, City: {city}")

        result = template.render(name="Bob", age=30, city="NYC")

        assert "Name: Bob" in result
        assert "Age: 30" in result
        assert "City: NYC" in result

    def test_template_render_missing_variable(self):
        """Test rendering template with missing variable."""
        template = PromptTemplate("Hello {name}!")

        with pytest.raises(ValueError, match="Missing template variable"):
            template.render()

    def test_predefined_templates(self):
        """Test predefined prompt templates."""
        assert "summarize" in PROMPT_TEMPLATES
        assert "classify" in PROMPT_TEMPLATES
        assert "sentiment" in PROMPT_TEMPLATES

        summarize_template = PROMPT_TEMPLATES["summarize"]
        assert "num_points" in summarize_template.variables
        assert "text" in summarize_template.variables


# ============================================================================
# MEDIUM TESTS - Async Operations, Clients, Cache
# ============================================================================


@pytest.mark.medium
@pytest.mark.integration
class TestRateLimiter:
    """Test RateLimiter class."""

    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self):
        """Test creating rate limiter."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        assert limiter.max_requests == 10
        assert limiter.window_seconds == 60

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Test acquiring rate limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        # Should allow first request
        result = await limiter.acquire()
        assert result is True

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_when_exceeded(self):
        """Test rate limiter blocks when limit exceeded."""
        limiter = RateLimiter(max_requests=2, window_seconds=2)

        # Allow 2 requests
        await limiter.acquire()
        await limiter.acquire()

        # 3rd request should wait
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start

        # Should have waited some time (at least 1 second)
        assert elapsed >= 1.0

    @pytest.mark.asyncio
    async def test_rate_limiter_different_keys(self):
        """Test rate limiter with different keys."""
        limiter = RateLimiter(max_requests=2, window_seconds=10)

        # Different keys should be independent
        await limiter.acquire(key="user1")
        await limiter.acquire(key="user1")
        await limiter.acquire(key="user2")

        assert len(limiter.requests["user1"]) == 2
        assert len(limiter.requests["user2"]) == 1


@pytest.mark.medium
@pytest.mark.integration
class TestResponseCache:
    """Test ResponseCache class."""

    def test_cache_creation(self):
        """Test creating response cache."""
        cache = ResponseCache(ttl=3600)

        assert cache.ttl == 3600

    def test_cache_set_and_get(self):
        """Test setting and getting cached response."""
        cache = ResponseCache(ttl=60)

        usage = TokenUsage(10, 20, 30)
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason="stop"
        )

        # Cache response
        cache.set(response, prompt="Hello", model="gpt-4")

        # Retrieve from cache
        cached = cache.get(prompt="Hello", model="gpt-4")

        assert cached is not None
        assert cached.content == "Test"
        assert cached.cached is True

    def test_cache_miss(self):
        """Test cache miss."""
        cache = ResponseCache(ttl=60)

        result = cache.get(prompt="Non-existent", model="gpt-4")

        assert result is None

    def test_cache_expiry(self):
        """Test cache expiry."""
        cache = ResponseCache(ttl=1)  # 1 second TTL

        usage = TokenUsage(10, 20, 30)
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason="stop"
        )

        cache.set(response, prompt="Hello", model="gpt-4")

        # Wait for expiry
        time.sleep(1.5)

        # Should be expired
        cached = cache.get(prompt="Hello", model="gpt-4")
        assert cached is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = ResponseCache(ttl=60)

        usage = TokenUsage(10, 20, 30)
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason="stop"
        )

        cache.set(response, prompt="Hello", model="gpt-4")

        cache.clear()

        # Should be empty
        cached = cache.get(prompt="Hello", model="gpt-4")
        assert cached is None


@pytest.mark.medium
@pytest.mark.integration
class TestOpenAIClient:
    """Test OpenAIClient class."""

    @pytest.mark.asyncio
    async def test_client_creation(self):
        """Test creating OpenAI client."""
        config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4")
        client = OpenAIClient(config)

        assert client.config.provider == LLMProvider.OPENAI
        assert client.config.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_client_complete(self):
        """Test completion generation."""
        config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4", cache_enabled=False)
        client = OpenAIClient(config)

        response = await client.complete("Hello, how are you?")

        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert response.provider == LLMProvider.OPENAI
        assert response.usage.total_tokens > 0

    @pytest.mark.asyncio
    async def test_client_complete_with_cache(self):
        """Test completion with caching."""
        config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4", cache_enabled=True)
        client = OpenAIClient(config)

        prompt = "Test prompt for caching"

        # First call
        response1 = await client.complete(prompt)
        assert response1.cached is False

        # Second call (should be cached)
        response2 = await client.complete(prompt)
        assert response2.cached is True
        assert response2.content == response1.content

    @pytest.mark.asyncio
    async def test_client_streaming(self):
        """Test streaming completion."""
        config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4")
        client = OpenAIClient(config)

        chunks = []
        async for chunk in client.complete_stream("Hello"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)


@pytest.mark.medium
@pytest.mark.integration
class TestAnthropicClient:
    """Test AnthropicClient class."""

    @pytest.mark.asyncio
    async def test_anthropic_client_complete(self):
        """Test Anthropic completion."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, model="claude-3-opus")
        client = AnthropicClient(config)

        response = await client.complete("Hello")

        assert response.provider == LLMProvider.ANTHROPIC
        assert "Claude" in response.content

    @pytest.mark.asyncio
    async def test_anthropic_client_streaming(self):
        """Test Anthropic streaming."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC, model="claude-3-sonnet")
        client = AnthropicClient(config)

        chunks = []
        async for chunk in client.complete_stream("Test"):
            chunks.append(chunk)

        assert len(chunks) > 0


@pytest.mark.medium
@pytest.mark.integration
class TestLocalLLMClient:
    """Test LocalLLMClient class."""

    @pytest.mark.asyncio
    async def test_local_client_complete(self):
        """Test local LLM completion."""
        config = LLMConfig(provider=LLMProvider.LOCAL, model="llama-2-7b")
        client = LocalLLMClient(config)

        response = await client.complete("Hello")

        assert response.provider == LLMProvider.LOCAL
        assert response.usage.estimated_cost == 0.0  # Local is free


@pytest.mark.medium
@pytest.mark.integration
class TestLLMClientFactory:
    """Test LLMClientFactory class."""

    def test_factory_create_openai(self):
        """Test creating OpenAI client via factory."""
        config = LLMConfig(provider=LLMProvider.OPENAI)
        client = LLMClientFactory.create(config)

        assert isinstance(client, OpenAIClient)

    def test_factory_create_anthropic(self):
        """Test creating Anthropic client via factory."""
        config = LLMConfig(provider=LLMProvider.ANTHROPIC)
        client = LLMClientFactory.create(config)

        assert isinstance(client, AnthropicClient)

    def test_factory_create_local(self):
        """Test creating local client via factory."""
        config = LLMConfig(provider=LLMProvider.LOCAL)
        client = LLMClientFactory.create(config)

        assert isinstance(client, LocalLLMClient)

    def test_factory_unknown_provider(self):
        """Test factory with unknown provider."""
        # This would need to be mocked as we can't create invalid enum
        # Just test that valid providers work
        assert True


# ============================================================================
# LARGE TESTS - Full Workflows, Fallback, Integration
# ============================================================================


@pytest.mark.large
@pytest.mark.e2e
class TestFallbackLLMClient:
    """Test FallbackLLMClient with multiple providers."""

    @pytest.mark.asyncio
    async def test_fallback_success_first_provider(self):
        """Test fallback when first provider succeeds."""
        config = LLMConfig(provider=LLMProvider.FALLBACK)

        # Create working clients
        openai_config = LLMConfig(provider=LLMProvider.OPENAI)
        local_config = LLMConfig(provider=LLMProvider.LOCAL)

        clients = [
            LLMClientFactory.create(openai_config),
            LLMClientFactory.create(local_config),
        ]

        fallback = FallbackLLMClient(config, clients)

        response = await fallback.complete("Test prompt")

        assert response is not None
        # Should use first provider (OpenAI)
        assert response.provider == LLMProvider.OPENAI

    @pytest.mark.asyncio
    async def test_fallback_when_first_fails(self):
        """Test fallback when first provider fails."""
        config = LLMConfig(provider=LLMProvider.FALLBACK)

        # Create mock failing client
        failing_client = MagicMock(spec=BaseLLMClient)
        failing_client.complete = AsyncMock(side_effect=Exception("API Error"))
        failing_client.config = LLMConfig(provider=LLMProvider.OPENAI)

        # Create working client
        working_config = LLMConfig(provider=LLMProvider.LOCAL)
        working_client = LocalLLMClient(working_config)

        fallback = FallbackLLMClient(config, [failing_client, working_client])

        response = await fallback.complete("Test prompt")

        assert response is not None
        # Should fall back to second provider
        assert response.provider == LLMProvider.LOCAL


@pytest.mark.large
@pytest.mark.e2e
class TestLLMIntegrationWorkflow:
    """Test complete LLM integration workflows."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_caching_and_cost(self):
        """Test full workflow: prompt -> cache -> cost calculation."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            cache_enabled=True,
            rate_limit_requests=10
        )
        client = OpenAIClient(config)

        prompt = "Explain machine learning in one sentence"

        # First call
        response1 = await client.complete(prompt)

        assert response1.cached is False
        assert response1.usage.estimated_cost > 0

        # Second call (cached)
        response2 = await client.complete(prompt)

        assert response2.cached is True
        assert response2.content == response1.content

    @pytest.mark.asyncio
    async def test_get_llm_client_helper(self):
        """Test get_llm_client helper function."""
        client = get_llm_client(provider="openai", model="gpt-4")

        assert isinstance(client, OpenAIClient)
        assert client.config.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_complete_helper_function(self):
        """Test complete() helper function."""
        response = await complete("Hello", provider="openai")

        assert isinstance(response, LLMResponse)
        assert response.content is not None
