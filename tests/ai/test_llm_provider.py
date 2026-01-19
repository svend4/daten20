"""
Tests for Production LLM Provider Integration

Tests cover:
- OpenAI integration
- Anthropic integration
- Mock client
- Response caching
- Usage tracking
- Error handling and retries
- Streaming
- Cost estimation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import asyncio

from src.ai.llm_provider import (
    OpenAIClient,
    AnthropicClient,
    MockLLMClient,
    LLMProvider,
    LLMMessage,
    LLMRole,
    LLMResponse,
    LLMUsage,
    StreamChunk,
    get_llm_client,
    quick_complete
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_choice = Mock()
    mock_choice.message.content = "This is a test response from OpenAI."
    mock_choice.finish_reason = "stop"

    mock_usage = Mock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 20
    mock_usage.total_tokens = 30

    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_response.model = "gpt-3.5-turbo-0125"
    mock_response.usage = mock_usage
    mock_response.id = "chatcmpl-test123"
    mock_response.created = 1234567890

    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_text_block = Mock()
    mock_text_block.text = "This is a test response from Claude."

    mock_usage = Mock()
    mock_usage.input_tokens = 15
    mock_usage.output_tokens = 25

    mock_response = Mock()
    mock_response.content = [mock_text_block]
    mock_response.model = "claude-3-sonnet-20240229"
    mock_response.usage = mock_usage
    mock_response.stop_reason = "end_turn"
    mock_response.id = "msg_test123"
    mock_response.type = "message"

    return mock_response


# ============================================================
# OpenAI Client Tests
# ============================================================

def test_openai_client_initialization():
    """Test OpenAI client initialization"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient()
            assert client.api_key == 'test_key'
            assert client.model == 'gpt-3.5-turbo'
            assert client.enabled is True


def test_openai_client_no_api_key():
    """Test OpenAI client without API key"""
    with patch.dict('os.environ', {}, clear=True):
        client = OpenAIClient()
        assert client.enabled is False
        assert client.api_key is None


def test_openai_client_custom_model():
    """Test OpenAI client with custom model"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient(model='gpt-4')
            assert client.model == 'gpt-4'


@pytest.mark.asyncio
async def test_openai_complete_success(mock_openai_response):
    """Test successful OpenAI completion"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient()
            client.enabled = True

            # Mock the API call
            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            client.client = mock_client

            response = await client.complete("Test prompt")

            assert response.content == "This is a test response from OpenAI."
            assert response.provider == LLMProvider.OPENAI
            assert response.usage.total_tokens == 30
            assert response.finish_reason == "stop"
            assert not response.cached  # First call not cached


@pytest.mark.asyncio
async def test_openai_complete_caching(mock_openai_response):
    """Test response caching"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient(cache_enabled=True)
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            client.client = mock_client

            # First call
            response1 = await client.complete("Test prompt")
            assert not response1.cached

            # Second call with same prompt should be cached
            response2 = await client.complete("Test prompt")
            assert response2.cached
            assert response2.content == response1.content

            # API should only be called once
            assert mock_client.chat.completions.create.call_count == 1


@pytest.mark.asyncio
async def test_openai_complete_not_configured():
    """Test completion when client not configured"""
    client = OpenAIClient()
    client.enabled = False

    with pytest.raises(RuntimeError, match="not configured"):
        await client.complete("Test prompt")


@pytest.mark.asyncio
async def test_openai_complete_with_retries():
    """Test retry logic on API errors"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient(max_retries=3)
            client.enabled = True

            mock_client = AsyncMock()
            # First two calls fail, third succeeds
            mock_client.chat.completions.create = AsyncMock(
                side_effect=[
                    Exception("Rate limit"),
                    Exception("Server error"),
                    Mock(
                        choices=[Mock(message=Mock(content="Success"), finish_reason="stop")],
                        model="gpt-3.5-turbo",
                        usage=Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
                        id="test",
                        created=123
                    )
                ]
            )
            client.client = mock_client

            response = await client.complete("Test prompt")
            assert response.content == "Success"
            assert mock_client.chat.completions.create.call_count == 3


@pytest.mark.asyncio
async def test_openai_complete_all_retries_fail():
    """Test when all retries fail"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient(max_retries=2)
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Persistent error"))
            client.client = mock_client

            with pytest.raises(RuntimeError, match="failed after 2 attempts"):
                await client.complete("Test prompt")


@pytest.mark.asyncio
async def test_openai_chat_completion(mock_openai_response):
    """Test chat completion with message history"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient()
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
            client.client = mock_client

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content="You are helpful."),
                LLMMessage(role=LLMRole.USER, content="Hello!")
            ]

            response = await client.complete_chat(messages)

            assert response.content is not None
            assert response.provider == LLMProvider.OPENAI

            # Verify messages were converted correctly
            call_args = mock_client.chat.completions.create.call_args
            assert len(call_args.kwargs['messages']) == 2
            assert call_args.kwargs['messages'][0]['role'] == 'system'
            assert call_args.kwargs['messages'][1]['role'] == 'user'


# ============================================================
# Anthropic Client Tests
# ============================================================

def test_anthropic_client_initialization():
    """Test Anthropic client initialization"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient()
            assert client.api_key == 'test_key'
            assert 'claude' in client.model.lower()
            assert client.enabled is True


def test_anthropic_client_no_api_key():
    """Test Anthropic client without API key"""
    with patch.dict('os.environ', {}, clear=True):
        client = AnthropicClient()
        assert client.enabled is False


@pytest.mark.asyncio
async def test_anthropic_complete_success(mock_anthropic_response):
    """Test successful Anthropic completion"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient()
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            client.client = mock_client

            response = await client.complete("Test prompt")

            assert response.content == "This is a test response from Claude."
            assert response.provider == LLMProvider.ANTHROPIC
            assert response.usage.total_tokens == 40  # 15 + 25
            assert response.finish_reason == "end_turn"


@pytest.mark.asyncio
async def test_anthropic_complete_with_system_prompt(mock_anthropic_response):
    """Test completion with system prompt"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient()
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            client.client = mock_client

            response = await client.complete(
                "What is AI?",
                system="You are a computer science professor."
            )

            assert response.content is not None

            # Verify system prompt was passed
            call_args = mock_client.messages.create.call_args
            assert 'system' in call_args.kwargs
            assert call_args.kwargs['system'] == "You are a computer science professor."


@pytest.mark.asyncio
async def test_anthropic_chat_completion(mock_anthropic_response):
    """Test chat completion with Anthropic"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient()
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            client.client = mock_client

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content="Be helpful."),
                LLMMessage(role=LLMRole.USER, content="Hello!"),
                LLMMessage(role=LLMRole.ASSISTANT, content="Hi there!"),
                LLMMessage(role=LLMRole.USER, content="How are you?")
            ]

            response = await client.complete_chat(messages)

            assert response.content is not None

            # Verify system message was extracted
            call_args = mock_client.messages.create.call_args
            assert 'system' in call_args.kwargs
            assert call_args.kwargs['system'] == "Be helpful."

            # Verify other messages don't include system role
            messages_sent = call_args.kwargs['messages']
            assert all(msg['role'] != 'system' for msg in messages_sent)


@pytest.mark.asyncio
async def test_anthropic_complete_caching(mock_anthropic_response):
    """Test Anthropic response caching"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient(cache_enabled=True)
            client.enabled = True

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            client.client = mock_client

            # First call
            response1 = await client.complete("Test prompt")
            assert not response1.cached

            # Second call should be cached
            response2 = await client.complete("Test prompt")
            assert response2.cached

            # API called only once
            assert mock_client.messages.create.call_count == 1


# ============================================================
# Mock Client Tests
# ============================================================

@pytest.mark.asyncio
async def test_mock_client_complete():
    """Test mock client completion"""
    client = MockLLMClient()

    response = await client.complete("Test prompt")

    assert response.content is not None
    assert response.provider == LLMProvider.MOCK
    assert response.usage is not None
    assert response.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_mock_client_summarize():
    """Test mock client recognizes summarize request"""
    client = MockLLMClient()

    response = await client.complete("Please summarize this text")

    assert "summary" in response.content.lower()


@pytest.mark.asyncio
async def test_mock_client_question():
    """Test mock client recognizes questions"""
    client = MockLLMClient()

    response = await client.complete("What is quantum computing?")

    assert "answer" in response.content.lower()


@pytest.mark.asyncio
async def test_mock_client_chat():
    """Test mock client chat completion"""
    client = MockLLMClient()

    messages = [
        LLMMessage(role=LLMRole.USER, content="Hello!")
    ]

    response = await client.complete_chat(messages)

    assert response.content is not None
    assert response.provider == LLMProvider.MOCK


@pytest.mark.asyncio
async def test_mock_client_streaming():
    """Test mock client streaming"""
    client = MockLLMClient()

    chunks = []
    async for chunk in client.stream("Test prompt"):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert chunks[-1].finish_reason == "stop"


# ============================================================
# Response Model Tests
# ============================================================

def test_llm_response_cost_estimation():
    """Test cost estimation for different models"""
    # GPT-4 response
    gpt4_response = LLMResponse(
        content="Test",
        model="gpt-4",
        provider=LLMProvider.OPENAI,
        usage=LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    )

    cost = gpt4_response.estimate_cost()
    # 1000 tokens * $30/1M + 500 tokens * $60/1M = $0.03 + $0.03 = $0.06
    assert 0.055 < cost < 0.065

    # GPT-3.5 response
    gpt35_response = LLMResponse(
        content="Test",
        model="gpt-3.5-turbo",
        provider=LLMProvider.OPENAI,
        usage=LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    )

    cost = gpt35_response.estimate_cost()
    # Much cheaper: 1000 * $0.5/1M + 500 * $1.5/1M = $0.0005 + $0.00075 = $0.00125
    assert 0.001 < cost < 0.002


def test_llm_response_total_tokens():
    """Test total tokens property"""
    response = LLMResponse(
        content="Test",
        model="test",
        provider=LLMProvider.MOCK,
        usage=LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    )

    assert response.total_tokens == 150


def test_llm_response_no_usage():
    """Test response without usage info"""
    response = LLMResponse(
        content="Test",
        model="test",
        provider=LLMProvider.MOCK
    )

    assert response.total_tokens == 0
    assert response.estimate_cost() == 0.0


# ============================================================
# Usage Tracking Tests
# ============================================================

@pytest.mark.asyncio
async def test_usage_tracking():
    """Test usage statistics tracking"""
    client = MockLLMClient()

    # Make several requests
    for i in range(5):
        await client.complete(f"Test prompt {i}")

    stats = client.get_usage_stats(days=1)

    assert stats['total_requests'] == 5
    assert stats['total_tokens'] > 0
    assert stats['total_cost_usd'] >= 0


@pytest.mark.asyncio
async def test_usage_stats_multiple_days():
    """Test usage stats over multiple days"""
    client = MockLLMClient()

    # Make a request
    await client.complete("Test")

    stats = client.get_usage_stats(days=7)

    assert stats['period_days'] == 7
    assert stats['total_requests'] >= 1


# ============================================================
# Caching Tests
# ============================================================

def test_cache_key_generation():
    """Test cache key generation"""
    client = MockLLMClient()

    key1 = client._cache_key("test prompt", "model1")
    key2 = client._cache_key("test prompt", "model1")
    key3 = client._cache_key("different prompt", "model1")

    # Same inputs produce same key
    assert key1 == key2

    # Different inputs produce different keys
    assert key1 != key3


@pytest.mark.asyncio
async def test_cache_disabled():
    """Test with caching disabled"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient(cache_enabled=False)
            client.enabled = True

            mock_client = AsyncMock()
            mock_response = Mock(
                choices=[Mock(message=Mock(content="Test"), finish_reason="stop")],
                model="gpt-3.5-turbo",
                usage=Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30),
                id="test",
                created=123
            )
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            client.client = mock_client

            # Make same request twice
            await client.complete("Test")
            await client.complete("Test")

            # Should call API both times (no caching)
            assert mock_client.chat.completions.create.call_count == 2


# ============================================================
# Factory Function Tests
# ============================================================

def test_get_llm_client_openai():
    """Test factory function for OpenAI"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = get_llm_client(LLMProvider.OPENAI)
            assert isinstance(client, OpenAIClient)


def test_get_llm_client_anthropic():
    """Test factory function for Anthropic"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = get_llm_client(LLMProvider.ANTHROPIC)
            assert isinstance(client, AnthropicClient)


def test_get_llm_client_mock():
    """Test factory function for mock"""
    client = get_llm_client(LLMProvider.MOCK)
    assert isinstance(client, MockLLMClient)


def test_get_llm_client_singleton():
    """Test singleton behavior"""
    client1 = get_llm_client(LLMProvider.MOCK, use_singleton=True)
    client2 = get_llm_client(LLMProvider.MOCK, use_singleton=True)

    assert client1 is client2


def test_get_llm_client_no_singleton():
    """Test non-singleton instances"""
    client1 = get_llm_client(LLMProvider.MOCK, use_singleton=False)
    client2 = get_llm_client(LLMProvider.MOCK, use_singleton=False)

    assert client1 is not client2


@pytest.mark.asyncio
async def test_quick_complete():
    """Test quick_complete convenience function"""
    result = await quick_complete("Test prompt", provider=LLMProvider.MOCK)

    assert isinstance(result, str)
    assert len(result) > 0


# ============================================================
# Streaming Tests
# ============================================================

@pytest.mark.asyncio
async def test_openai_streaming():
    """Test OpenAI streaming"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.openai'):
            client = OpenAIClient()
            client.enabled = True

            # Mock streaming response
            async def mock_stream():
                chunks = ["Hello", " world", "!"]
                for chunk_text in chunks:
                    mock_chunk = Mock()
                    mock_chunk.choices = [Mock(
                        delta=Mock(content=chunk_text),
                        finish_reason=None
                    )]
                    yield mock_chunk

                # Final chunk with finish reason
                final_chunk = Mock()
                final_chunk.choices = [Mock(
                    delta=Mock(content=None),
                    finish_reason="stop"
                )]
                yield final_chunk

            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
            client.client = mock_client

            chunks = []
            async for chunk in client.stream("Test"):
                chunks.append(chunk)

            assert len(chunks) > 0
            assert any(chunk.content for chunk in chunks)


@pytest.mark.asyncio
async def test_anthropic_streaming():
    """Test Anthropic streaming"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.ai.llm_provider.anthropic'):
            client = AnthropicClient()
            client.enabled = True

            # Mock streaming
            async def mock_text_stream():
                for word in ["Hello", " Claude", "!"]:
                    yield word

            mock_stream = AsyncMock()
            mock_stream.text_stream = mock_text_stream()
            mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
            mock_stream.__aexit__ = AsyncMock(return_value=None)

            mock_client = AsyncMock()
            mock_client.messages.stream = Mock(return_value=mock_stream)
            client.client = mock_client

            chunks = []
            async for chunk in client.stream("Test"):
                chunks.append(chunk.content)

            assert len(chunks) == 3
            assert "".join(chunks) == "Hello Claude!"


# ============================================================
# Integration Tests (require real API keys)
# ============================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_real_api():
    """
    Integration test with real OpenAI API

    Requires: OPENAI_API_KEY environment variable
    """
    import os

    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("OPENAI_API_KEY not set")

    client = get_llm_client(LLMProvider.OPENAI)

    if not client.enabled:
        pytest.skip("OpenAI not configured")

    response = await client.complete(
        "Say 'Integration test passed' and nothing else.",
        max_tokens=20
    )

    assert response.content is not None
    assert response.usage.total_tokens > 0
    assert response.estimate_cost() > 0
    print(f"\n✅ OpenAI: {response.total_tokens} tokens, ${response.estimate_cost():.4f}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_anthropic_real_api():
    """
    Integration test with real Anthropic API

    Requires: ANTHROPIC_API_KEY environment variable
    """
    import os

    if not os.getenv('ANTHROPIC_API_KEY'):
        pytest.skip("ANTHROPIC_API_KEY not set")

    client = get_llm_client(LLMProvider.ANTHROPIC)

    if not client.enabled:
        pytest.skip("Anthropic not configured")

    response = await client.complete(
        "Say 'Integration test passed' and nothing else.",
        max_tokens=20
    )

    assert response.content is not None
    assert response.usage.total_tokens > 0
    assert response.estimate_cost() > 0
    print(f"\n✅ Anthropic: {response.total_tokens} tokens, ${response.estimate_cost():.4f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
