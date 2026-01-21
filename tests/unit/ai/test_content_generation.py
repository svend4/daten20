"""
Comprehensive tests for ai/content_generation.py module

Tests organized by size:
- Small: Enums, dataclasses, templates
- Medium: Individual generators (async operations)
- Large: Full content generation workflows

Test coverage: ~80% target
"""

import pytest

from src.ai.content_generation import (
    AutoCompleter,
    ContentCondenser,
    ContentExpander,
    ContentGenerator,
    ContentStyle,
    GeneratedContent,
    GenerationConfig,
    GenerationType,
    GrammarCorrector,
    Paraphraser,
    StyleTransfer,
    TemplateGenerator,
    TitleGenerator,
    Translator,
    get_content_generator,
)

# ============================================================================
# SMALL TESTS - Enums, Dataclasses
# ============================================================================

pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestGenerationType:
    """Test GenerationType enum."""

    def test_all_generation_types_defined(self):
        """Test all generation types are defined."""
        types = [t for t in GenerationType]
        assert len(types) == 8

        assert GenerationType.TEMPLATE in types
        assert GenerationType.COMPLETION in types
        assert GenerationType.TRANSLATION in types
        assert GenerationType.PARAPHRASE in types
        assert GenerationType.GRAMMAR_FIX in types

    def test_generation_type_values(self):
        """Test generation type enum values."""
        assert GenerationType.TEMPLATE.value == "template"
        assert GenerationType.TITLE.value == "title"
        assert GenerationType.SUMMARY.value == "summary"


class TestContentStyle:
    """Test ContentStyle enum."""

    def test_all_styles_defined(self):
        """Test all content styles are defined."""
        styles = [s for s in ContentStyle]
        assert len(styles) == 6

        assert ContentStyle.FORMAL in styles
        assert ContentStyle.CASUAL in styles
        assert ContentStyle.TECHNICAL in styles
        assert ContentStyle.CREATIVE in styles

    def test_style_values(self):
        """Test style enum values."""
        assert ContentStyle.FORMAL.value == "formal"
        assert ContentStyle.BUSINESS.value == "business"
        assert ContentStyle.ACADEMIC.value == "academic"


class TestGenerationConfig:
    """Test GenerationConfig dataclass."""

    def test_config_default_values(self):
        """Test default configuration values."""
        config = GenerationConfig()

        assert config.max_tokens == 500
        assert config.temperature == 0.7
        assert config.top_p == 1.0
        assert config.style == ContentStyle.FORMAL

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = GenerationConfig(
            max_tokens=1000,
            temperature=0.5,
            style=ContentStyle.TECHNICAL
        )

        assert config.max_tokens == 1000
        assert config.temperature == 0.5
        assert config.style == ContentStyle.TECHNICAL


class TestGeneratedContent:
    """Test GeneratedContent dataclass."""

    def test_content_creation(self):
        """Test creating generated content."""
        content = GeneratedContent(
            content="Test content",
            generation_type=GenerationType.TEMPLATE
        )

        assert content.content == "Test content"
        assert content.generation_type == GenerationType.TEMPLATE
        assert content.metadata == {}
        assert content.confidence == 0.8

    def test_content_with_metadata(self):
        """Test generated content with metadata."""
        metadata = {"source": "llm", "model": "gpt-4"}
        content = GeneratedContent(
            content="Generated text",
            generation_type=GenerationType.PARAPHRASE,
            metadata=metadata,
            confidence=0.95
        )

        assert content.metadata["source"] == "llm"
        assert content.confidence == 0.95


class TestTemplateGeneratorTemplates:
    """Test TemplateGenerator predefined templates."""

    def test_business_letter_template_exists(self):
        """Test business letter template is defined."""
        gen = TemplateGenerator()

        assert "business_letter" in gen.TEMPLATES
        template = gen.TEMPLATES["business_letter"]
        assert "{body}" in template

    def test_meeting_minutes_template_exists(self):
        """Test meeting minutes template is defined."""
        gen = TemplateGenerator()

        assert "meeting_minutes" in gen.TEMPLATES
        template = gen.TEMPLATES["meeting_minutes"]
        assert "{date}" in template
        assert "{attendees}" in template

    def test_project_proposal_template_exists(self):
        """Test project proposal template is defined."""
        gen = TemplateGenerator()

        assert "project_proposal" in gen.TEMPLATES
        template = gen.TEMPLATES["project_proposal"]
        assert "{title}" in template
        assert "{budget}" in template

    def test_all_templates_defined(self):
        """Test all expected templates are defined."""
        gen = TemplateGenerator()

        expected_templates = [
            "business_letter",
            "meeting_minutes",
            "project_proposal",
            "technical_doc",
            "report"
        ]

        for template_name in expected_templates:
            assert template_name in gen.TEMPLATES


# ============================================================================
# MEDIUM TESTS - Individual Generators
# ============================================================================


@pytest.mark.medium
@pytest.mark.integration
class TestTemplateGenerator:
    """Test TemplateGenerator class."""

    @pytest.mark.asyncio
    async def test_generate_template_without_context(self):
        """Test generating template without context."""
        gen = TemplateGenerator()

        result = await gen.generate("business_letter", context=None, use_llm=False)

        assert isinstance(result, GeneratedContent)
        assert result.generation_type == GenerationType.TEMPLATE
        assert "{body}" in result.content  # Placeholders remain

    @pytest.mark.asyncio
    async def test_generate_template_with_context(self):
        """Test generating template with context."""
        gen = TemplateGenerator()

        context = {
            "date": "2024-01-20",
            "time": "10:00 AM",
            "location": "Conference Room A",
            "attendees": "Alice, Bob, Charlie",
            "agenda": "1. Project updates\n2. Budget review",
            "discussion": "Team discussed progress",
            "action_items": "- Complete tasks by Friday",
            "next_meeting": "2024-01-27"
        }

        result = await gen.generate("meeting_minutes", context=context, use_llm=False)

        assert "2024-01-20" in result.content
        assert "10:00 AM" in result.content
        assert "Conference Room A" in result.content

    @pytest.mark.asyncio
    async def test_generate_unknown_template(self):
        """Test generating unknown template."""
        gen = TemplateGenerator()

        with pytest.raises(ValueError, match="Unknown template type"):
            await gen.generate("nonexistent_template")

    @pytest.mark.asyncio
    async def test_generate_with_llm_enabled(self):
        """Test generating template with LLM (mocked)."""
        gen = TemplateGenerator()

        context = {"title": "Test Project"}

        # This will use mocked LLM
        result = await gen.generate("project_proposal", context=context, use_llm=True)

        assert isinstance(result, GeneratedContent)
        assert "Test Project" in result.content


@pytest.mark.medium
@pytest.mark.integration
class TestAutoCompleter:
    """Test AutoCompleter class."""

    @pytest.mark.asyncio
    async def test_auto_complete(self):
        """Test auto-completion generation."""
        completer = AutoCompleter()

        text = "The weather today is"
        suggestions = await completer.complete(text, num_suggestions=3)

        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3
        assert all(isinstance(s, str) for s in suggestions)

    @pytest.mark.asyncio
    async def test_auto_complete_with_max_tokens(self):
        """Test auto-completion with max tokens limit."""
        completer = AutoCompleter()

        text = "Python is"
        suggestions = await completer.complete(text, num_suggestions=2, max_tokens=20)

        assert len(suggestions) <= 2


@pytest.mark.medium
@pytest.mark.integration
class TestTitleGenerator:
    """Test TitleGenerator class."""

    @pytest.mark.asyncio
    async def test_generate_titles(self):
        """Test title generation."""
        gen = TitleGenerator()

        content = "Machine learning is a subset of artificial intelligence..."
        titles = await gen.generate(content, num_suggestions=5)

        assert isinstance(titles, list)
        assert len(titles) <= 5
        assert all(isinstance(t, str) for t in titles)

    @pytest.mark.asyncio
    async def test_generate_titles_with_style(self):
        """Test title generation with specific style."""
        gen = TitleGenerator()

        content = "Research on quantum computing algorithms"
        titles = await gen.generate(content, num_suggestions=3, style=ContentStyle.ACADEMIC)

        assert len(titles) <= 3

    @pytest.mark.asyncio
    async def test_simple_title_fallback(self):
        """Test simple title generation fallback."""
        gen = TitleGenerator()

        # Test the fallback method directly
        content = "This is a very long first sentence that should be truncated because it exceeds sixty characters."
        title = gen._generate_simple_title(content)

        assert len(title) <= 63  # 60 + "..."
        assert isinstance(title, str)


@pytest.mark.medium
@pytest.mark.integration
class TestTranslator:
    """Test Translator class."""

    @pytest.mark.asyncio
    async def test_translate_supported_languages(self):
        """Test translation between supported languages."""
        translator = Translator()

        text = "Hello world"
        result = await translator.translate(text, source_lang="en", target_lang="es")

        assert isinstance(result, GeneratedContent)
        assert result.generation_type == GenerationType.TRANSLATION
        assert result.metadata["source_lang"] == "en"
        assert result.metadata["target_lang"] == "es"

    @pytest.mark.asyncio
    async def test_translate_unsupported_language(self):
        """Test translation with unsupported language."""
        translator = Translator()

        with pytest.raises(ValueError, match="Unsupported"):
            await translator.translate("Hello", source_lang="xx", target_lang="en")

    def test_supported_languages_defined(self):
        """Test supported languages are defined."""
        translator = Translator()

        assert "en" in translator.LANGUAGES
        assert "es" in translator.LANGUAGES
        assert "fr" in translator.LANGUAGES
        assert "de" in translator.LANGUAGES

        # Check language names
        assert translator.LANGUAGES["en"] == "English"
        assert translator.LANGUAGES["de"] == "German"


@pytest.mark.medium
@pytest.mark.integration
class TestParaphraser:
    """Test Paraphraser class."""

    @pytest.mark.asyncio
    async def test_paraphrase_text(self):
        """Test paraphrasing text."""
        paraphraser = Paraphraser()

        text = "Machine learning is a fascinating field of study."
        paraphrases = await paraphraser.paraphrase(text, num_variations=2)

        assert isinstance(paraphrases, list)
        assert len(paraphrases) <= 2
        assert all(isinstance(p, str) for p in paraphrases)

    @pytest.mark.asyncio
    async def test_paraphrase_with_style(self):
        """Test paraphrasing with specific style."""
        paraphraser = Paraphraser()

        text = "The experiment was successful."
        paraphrases = await paraphraser.paraphrase(
            text,
            num_variations=1,
            style=ContentStyle.FORMAL
        )

        assert len(paraphrases) >= 1


@pytest.mark.medium
@pytest.mark.integration
class TestGrammarCorrector:
    """Test GrammarCorrector class."""

    @pytest.mark.asyncio
    async def test_correct_grammar(self):
        """Test grammar correction."""
        corrector = GrammarCorrector()

        text = "This are a test."
        result = await corrector.correct(text)

        assert isinstance(result, GeneratedContent)
        assert result.generation_type == GenerationType.GRAMMAR_FIX
        assert isinstance(result.content, str)

    @pytest.mark.asyncio
    async def test_find_changes(self):
        """Test detecting changes between original and corrected."""
        corrector = GrammarCorrector()

        original = "This are wrong"
        corrected = "This is wrong"

        changes = corrector._find_changes(original, corrected)

        assert isinstance(changes, list)

    @pytest.mark.asyncio
    async def test_correct_already_correct_text(self):
        """Test correcting already correct text."""
        corrector = GrammarCorrector()

        text = "This is correct."
        result = await corrector.correct(text)

        assert result.content is not None


@pytest.mark.medium
@pytest.mark.integration
class TestStyleTransfer:
    """Test StyleTransfer class."""

    @pytest.mark.asyncio
    async def test_transfer_style(self):
        """Test transferring text style."""
        transfer = StyleTransfer()

        text = "Hey, what's up?"
        result = await transfer.transfer(text, target_style=ContentStyle.FORMAL)

        assert isinstance(result, GeneratedContent)
        assert result.generation_type == GenerationType.STYLE_TRANSFER
        assert result.metadata["target_style"] == "formal"

    @pytest.mark.asyncio
    async def test_transfer_to_casual_style(self):
        """Test transferring to casual style."""
        transfer = StyleTransfer()

        text = "Good morning, how may I assist you?"
        result = await transfer.transfer(text, target_style=ContentStyle.CASUAL)

        assert result.metadata["target_style"] == "casual"


@pytest.mark.medium
@pytest.mark.integration
class TestContentExpander:
    """Test ContentExpander class."""

    @pytest.mark.asyncio
    async def test_expand_bullet_points(self):
        """Test expanding bullet points."""
        expander = ContentExpander()

        bullet_points = [
            "Machine learning is powerful",
            "It requires data",
            "Models need training"
        ]

        expanded = await expander.expand(bullet_points, target_length="medium")

        assert isinstance(expanded, str)
        assert len(expanded) > 0

    @pytest.mark.asyncio
    async def test_expand_with_different_lengths(self):
        """Test expanding with different target lengths."""
        expander = ContentExpander()

        points = ["Test point"]

        short = await expander.expand(points, target_length="short")
        medium = await expander.expand(points, target_length="medium")
        long = await expander.expand(points, target_length="long")

        # All should produce output
        assert short is not None
        assert medium is not None
        assert long is not None


@pytest.mark.medium
@pytest.mark.integration
class TestContentCondenser:
    """Test ContentCondenser class."""

    @pytest.mark.asyncio
    async def test_condense_text(self):
        """Test condensing text to bullet points."""
        condenser = ContentCondenser()

        text = """Machine learning is a powerful technology.
        It requires large amounts of data to train models effectively.
        The models learn patterns from data.
        They can make predictions on new data."""

        points = await condenser.condense(text, num_points=3)

        assert isinstance(points, list)
        assert len(points) <= 3
        assert all(isinstance(p, str) for p in points)

    @pytest.mark.asyncio
    async def test_condense_empty_text(self):
        """Test condensing empty text."""
        condenser = ContentCondenser()

        points = await condenser.condense("", num_points=5)

        # Should handle gracefully
        assert isinstance(points, list)


# ============================================================================
# LARGE TESTS - Full Workflows
# ============================================================================


@pytest.mark.large
@pytest.mark.e2e
class TestContentGenerator:
    """Test ContentGenerator end-to-end workflows."""

    def test_content_generator_initialization(self):
        """Test creating content generator."""
        gen = ContentGenerator()

        assert gen.template_generator is not None
        assert gen.auto_completer is not None
        assert gen.title_generator is not None
        assert gen.translator is not None

    @pytest.mark.asyncio
    async def test_full_content_workflow(self):
        """Test complete content generation workflow."""
        gen = ContentGenerator()

        # 1. Generate from template
        template_result = await gen.generate_from_template(
            "business_letter",
            context={"body": "This is a test letter"}
        )
        assert isinstance(template_result, GeneratedContent)

        # 2. Generate title
        titles = await gen.generate_title("Machine learning research", num_suggestions=3)
        assert len(titles) <= 3

        # 3. Auto-complete
        completions = await gen.auto_complete("Python is", num_suggestions=2)
        assert len(completions) <= 2

    @pytest.mark.asyncio
    async def test_translation_workflow(self):
        """Test translation workflow."""
        gen = ContentGenerator()

        text = "Hello, how are you?"
        result = await gen.translate(text, source_lang="en", target_lang="es")

        assert isinstance(result, GeneratedContent)
        assert result.generation_type == GenerationType.TRANSLATION

    @pytest.mark.asyncio
    async def test_text_improvement_workflow(self):
        """Test text improvement workflow."""
        gen = ContentGenerator()

        # 1. Paraphrase
        paraphrases = await gen.paraphrase("This is a test", num_variations=2)
        assert len(paraphrases) <= 2

        # 2. Grammar correction
        corrected = await gen.correct_grammar("This are wrong")
        assert isinstance(corrected, GeneratedContent)

        # 3. Style transfer
        styled = await gen.transfer_style("Hey!", target_style=ContentStyle.FORMAL)
        assert isinstance(styled, GeneratedContent)

    @pytest.mark.asyncio
    async def test_content_expansion_and_condensation(self):
        """Test expanding and condensing content."""
        gen = ContentGenerator()

        # Expand bullet points
        points = ["Point 1", "Point 2"]
        expanded = await gen.expand_content(points, target_length="medium")
        assert isinstance(expanded, str)

        # Condense text
        long_text = "This is a long text that needs to be condensed into bullet points."
        condensed = await gen.condense_content(long_text, num_points=2)
        assert isinstance(condensed, list)

    @pytest.mark.asyncio
    async def test_get_content_generator_singleton(self):
        """Test get_content_generator() function."""
        gen1 = get_content_generator()
        gen2 = get_content_generator()

        # Should return same instance
        assert gen1 is gen2

    @pytest.mark.asyncio
    async def test_multiple_operations_in_sequence(self):
        """Test multiple content operations in sequence."""
        gen = ContentGenerator()

        # 1. Start with template
        template = await gen.generate_from_template(
            "technical_doc",
            context={"title": "API Documentation"}
        )

        # 2. Generate title options
        titles = await gen.generate_title(template.content[:200], num_suggestions=3)
        assert len(titles) > 0

        # 3. Expand some bullet points
        points = ["Feature 1", "Feature 2"]
        expanded = await gen.expand_content(points)

        # All operations should complete successfully
        assert template is not None
        assert titles is not None
        assert expanded is not None
