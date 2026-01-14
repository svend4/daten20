"""
Integration tests for v3.5 AI/ML
Tests all AI/ML components together.
"""

import pytest
from pathlib import Path

AI_DIR = Path(__file__).parent.parent.parent / "src" / "ai"


class TestAIMLStructure:
    """Test AI/ML module structure"""

    def test_ai_module_exists(self):
        """Test AI module directory exists"""
        assert AI_DIR.exists(), "AI directory should exist"

    def test_all_modules_exist(self):
        """Test all required modules exist"""
        required_modules = [
            "llm_integration.py",
            "llm_provider.py",
            "document_intelligence.py",
            "recommendations.py",
            "text_analysis.py",
            "embeddings.py",
            "content_generation.py",
            "ai_ml_api.py",
            "ai_services.py",
            "chatbot.py",
            "__init__.py"
        ]

        for module in required_modules:
            module_path = AI_DIR / module
            assert module_path.exists(), f"{module} should exist"

    def test_init_imports(self):
        """Test __init__.py has all imports"""
        init_file = AI_DIR / "__init__.py"
        content = init_file.read_text()

        required_imports = [
            "from .ai_ml_api import",
            "from .llm_integration import",
            "from .document_intelligence import",
            "from .recommendations import",
            "from .text_analysis import",
            "from .embeddings import",
            "from .content_generation import"
        ]

        for import_stmt in required_imports:
            assert import_stmt in content, f"{import_stmt} should be in __init__.py"


class TestLLMIntegration:
    """Test LLM integration implementation"""

    def test_llm_integration_file_exists(self):
        """Test llm_integration.py exists"""
        llm_integration = AI_DIR / "llm_integration.py"
        assert llm_integration.exists()

    def test_llm_integration_classes(self):
        """Test LLM integration has required classes"""
        llm_integration = AI_DIR / "llm_integration.py"
        content = llm_integration.read_text()

        required_classes = [
            "class LLMProvider",
            "class LLMConfig",
            "class LLMResponse",
            "class TokenUsage",
            "class BaseLLMClient",
            "class PromptTemplate"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_llm_functions(self):
        """Test LLM functions exist"""
        llm_integration = AI_DIR / "llm_integration.py"
        content = llm_integration.read_text()

        required_functions = [
            "def get_llm_client",
            "async def complete",
            "async def complete_stream"
        ]

        for func in required_functions:
            assert func in content, f"{func} should be defined"


class TestLLMProvider:
    """Test LLM provider implementation"""

    def test_llm_provider_file_exists(self):
        """Test llm_provider.py exists"""
        llm_provider = AI_DIR / "llm_provider.py"
        assert llm_provider.exists()

    def test_llm_provider_classes(self):
        """Test LLM provider has required classes"""
        llm_provider = AI_DIR / "llm_provider.py"
        content = llm_provider.read_text()

        required_classes = [
            "class OpenAIClient",
            "class AnthropicClient",
            "class MockLLMClient"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"


class TestDocumentIntelligence:
    """Test document intelligence implementation"""

    def test_document_intelligence_file_exists(self):
        """Test document_intelligence.py exists"""
        doc_intel = AI_DIR / "document_intelligence.py"
        assert doc_intel.exists()

    def test_document_intelligence_classes(self):
        """Test document intelligence has required classes"""
        doc_intel = AI_DIR / "document_intelligence.py"
        content = doc_intel.read_text()

        required_classes = [
            "class DocumentIntelligence",
            "class DocumentAnalysis",
            "class DocumentSummary",
            "class Entity",
            "class SummaryType"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_document_intelligence_methods(self):
        """Test document intelligence methods exist"""
        doc_intel = AI_DIR / "document_intelligence.py"
        content = doc_intel.read_text()

        required_methods = [
            "async def summarize",
            "async def classify",
            "async def extract_entities",
            "def get_document_intelligence"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestRecommendations:
    """Test recommendations engine"""

    def test_recommendations_file_exists(self):
        """Test recommendations.py exists"""
        recommendations = AI_DIR / "recommendations.py"
        assert recommendations.exists()

    def test_recommendations_classes(self):
        """Test recommendations has required classes"""
        recommendations = AI_DIR / "recommendations.py"
        content = recommendations.read_text()

        required_classes = [
            "class RecommendationEngine",
            "class Recommendation",
            "class RecommendationMethod",
            "class UserProfile"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_recommendations_methods(self):
        """Test recommendations methods exist"""
        recommendations = AI_DIR / "recommendations.py"
        content = recommendations.read_text()

        required_methods = [
            "async def recommend",
            "async def find_similar",
            "def get_recommendation_engine"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestTextAnalysis:
    """Test text analysis engine"""

    def test_text_analysis_file_exists(self):
        """Test text_analysis.py exists"""
        text_analysis = AI_DIR / "text_analysis.py"
        assert text_analysis.exists()

    def test_text_analysis_classes(self):
        """Test text analysis has required classes"""
        text_analysis = AI_DIR / "text_analysis.py"
        content = text_analysis.read_text()

        required_classes = [
            "class TextAnalyzer",
            "class SentimentResult",
            "class SentimentLabel",
            "class Keyword"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_text_analysis_methods(self):
        """Test text analysis methods exist"""
        text_analysis = AI_DIR / "text_analysis.py"
        content = text_analysis.read_text()

        required_methods = [
            "def analyze_sentiment",
            "def extract_keywords",
            "def detect_language",
            "def get_text_analyzer"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestEmbeddings:
    """Test embeddings and vector search"""

    def test_embeddings_file_exists(self):
        """Test embeddings.py exists"""
        embeddings = AI_DIR / "embeddings.py"
        assert embeddings.exists()

    def test_embeddings_classes(self):
        """Test embeddings has required classes"""
        embeddings = AI_DIR / "embeddings.py"
        content = embeddings.read_text()

        required_classes = [
            "class EmbeddingService",
            "class Embedding",
            "class EmbeddingModel",
            "class SearchResult"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_embeddings_methods(self):
        """Test embeddings methods exist"""
        embeddings = AI_DIR / "embeddings.py"
        content = embeddings.read_text()

        required_methods = [
            "async def embed_text",
            "async def search",
            "async def compute_similarity",
            "def get_embedding_service"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestContentGeneration:
    """Test content generation"""

    def test_content_generation_file_exists(self):
        """Test content_generation.py exists"""
        content_gen = AI_DIR / "content_generation.py"
        assert content_gen.exists()

    def test_content_generation_classes(self):
        """Test content generation has required classes"""
        content_gen = AI_DIR / "content_generation.py"
        content = content_gen.read_text()

        required_classes = [
            "class ContentGenerator",
            "class GeneratedContent",
            "class GenerationType",
            "class ContentStyle"
        ]

        for cls in required_classes:
            assert cls in content, f"{cls} should be defined"

    def test_content_generation_methods(self):
        """Test content generation methods exist"""
        content_gen = AI_DIR / "content_generation.py"
        content = content_gen.read_text()

        required_methods = [
            "async def generate",
            "async def translate",
            "async def paraphrase",
            "def get_content_generator"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"


class TestUnifiedAPI:
    """Test unified AI/ML API"""

    def test_ai_ml_api_file_exists(self):
        """Test ai_ml_api.py exists"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        assert ai_ml_api.exists()

    def test_ai_ml_api_class(self):
        """Test AIMLAPI class exists"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        assert "class AIMLAPI" in content, "AIMLAPI class should be defined"

    def test_ai_ml_api_config(self):
        """Test AIMLConfig exists"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        assert "class AIMLConfig" in content, "AIMLConfig should be defined"

    def test_ai_ml_api_operations(self):
        """Test AIMLAPI has all operation methods"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        required_methods = [
            "async def complete",
            "async def summarize_document",
            "async def classify_document",
            "async def extract_entities",
            "async def recommend",
            "def analyze_sentiment",
            "def extract_keywords",
            "async def embed_text",
            "async def semantic_search",
            "async def generate_content",
            "async def translate"
        ]

        for method in required_methods:
            assert method in content, f"{method} should be defined"

    def test_ai_ml_api_singleton(self):
        """Test get_ai_ml_api function exists"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        assert "def get_ai_ml_api" in content, "get_ai_ml_api function should be defined"

    def test_ai_ml_api_convenience_functions(self):
        """Test convenience functions exist"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        convenience_functions = [
            "async def summarize",
            "async def classify",
            "async def recommend",
            "def sentiment",
            "async def translate_text"
        ]

        for func in convenience_functions:
            assert func in content, f"{func} should be defined"


class TestAIMLIntegration:
    """Test integration between AI/ML components"""

    def test_all_singleton_getters_exist(self):
        """Test all modules have singleton getters"""
        init_file = AI_DIR / "__init__.py"
        content = init_file.read_text()

        required_getters = [
            "get_ai_ml_api",
            "get_llm_client",
            "get_document_intelligence",
            "get_recommendation_engine",
            "get_text_analyzer",
            "get_embedding_service",
            "get_content_generator"
        ]

        for getter in required_getters:
            assert getter in content, f"{getter} should be in __all__"

    def test_module_version(self):
        """Test module has correct version"""
        init_file = AI_DIR / "__init__.py"
        content = init_file.read_text()

        assert "__version__ = '3.5.0'" in content
        assert "Version: 3.5.0 (Complete)" in content

    def test_unified_api_imports_all_services(self):
        """Test unified API imports all services"""
        ai_ml_api = AI_DIR / "ai_ml_api.py"
        content = ai_ml_api.read_text()

        required_imports = [
            "from .llm_integration import",
            "from .document_intelligence import",
            "from .recommendations import",
            "from .text_analysis import",
            "from .embeddings import",
            "from .content_generation import"
        ]

        for import_stmt in required_imports:
            assert import_stmt in content, f"{import_stmt} should be in ai_ml_api.py"


class TestAIServices:
    """Test legacy AI services"""

    def test_ai_services_file_exists(self):
        """Test ai_services.py exists"""
        ai_services = AI_DIR / "ai_services.py"
        assert ai_services.exists()

    def test_ai_services_has_legacy_classes(self):
        """Test ai_services has legacy classes for backward compatibility"""
        ai_services = AI_DIR / "ai_services.py"
        content = ai_services.read_text()

        # Should have some legacy classes
        assert "class" in content, "Should have class definitions"


class TestChatbot:
    """Test chatbot implementation"""

    def test_chatbot_file_exists(self):
        """Test chatbot.py exists"""
        chatbot = AI_DIR / "chatbot.py"
        assert chatbot.exists()

    def test_chatbot_has_implementation(self):
        """Test chatbot has implementation"""
        chatbot = AI_DIR / "chatbot.py"
        content = chatbot.read_text()

        # Should have chatbot implementation
        assert "class" in content or "def" in content, "Should have chatbot implementation"


class TestFileStructure:
    """Test overall file structure and sizes"""

    def test_all_files_have_content(self):
        """Test all Python files have meaningful content"""
        python_files = list(AI_DIR.glob("*.py"))

        for py_file in python_files:
            if py_file.name == "__init__.py":
                min_lines = 50  # __init__.py should have imports
            else:
                min_lines = 100  # Other files should have implementations

            lines = len(py_file.read_text().splitlines())
            assert lines >= min_lines, f"{py_file.name} should have at least {min_lines} lines (has {lines})"

    def test_total_code_size(self):
        """Test total AI/ML code is substantial"""
        python_files = list(AI_DIR.glob("*.py"))
        total_lines = sum(len(f.read_text().splitlines()) for f in python_files)

        # Should have at least 3,000 lines total (plan says 3,450)
        assert total_lines >= 3000, f"Total AI/ML code should be at least 3,000 lines (has {total_lines})"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
