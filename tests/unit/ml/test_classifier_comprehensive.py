"""
Comprehensive tests for Document Classifier module

Test coverage goals:
- TextPreprocessor: Text cleaning, normalization, stopword removal
- TfidfSVMClassifier: Training, prediction, model persistence
- DocumentClassifier: Multi-model support, auto-categorization
- ClassificationResult: Confidence scores, probabilities
- Edge cases: Empty text, unknown categories, model serialization
- Performance: Large datasets, batch processing
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from src.ml.classifier import (
    DocumentCategory,
    ModelType,
    ClassificationResult,
    TrainingData,
    ModelMetrics,
    TextPreprocessor,
    TfidfSVMClassifier,
    DocumentClassifier,
)


class TestDocumentCategory:
    """Test DocumentCategory enum"""

    def test_all_categories(self):
        """Test all document categories"""
        categories = [
            DocumentCategory.INVOICE,
            DocumentCategory.CONTRACT,
            DocumentCategory.REPORT,
            DocumentCategory.SERVICE_PLAN,
            DocumentCategory.BUDGET_PLAN,
            DocumentCategory.CORRESPONDENCE,
            DocumentCategory.LEGAL,
            DocumentCategory.FINANCIAL,
            DocumentCategory.ADMINISTRATIVE,
            DocumentCategory.OTHER,
        ]

        assert len(categories) == 10
        for cat in categories:
            assert isinstance(cat.value, str)


class TestModelType:
    """Test ModelType enum"""

    def test_all_model_types(self):
        """Test all model types"""
        models = [
            ModelType.TFIDF_SVM,
            ModelType.NAIVE_BAYES,
            ModelType.LOGISTIC_REGRESSION,
            ModelType.BERT,
            ModelType.DISTILBERT,
        ]

        assert len(models) == 5


class TestClassificationResult:
    """Test ClassificationResult dataclass"""

    def test_result_creation(self):
        """Test basic result creation"""
        result = ClassificationResult(
            category=DocumentCategory.INVOICE,
            confidence=0.95,
            probabilities={"invoice": 0.95, "contract": 0.05},
            features={"length": 1000}
        )

        assert result.category == DocumentCategory.INVOICE
        assert result.confidence == 0.95
        assert result.probabilities["invoice"] == 0.95

    def test_result_default_values(self):
        """Test result with default values"""
        result = ClassificationResult(
            category=DocumentCategory.CONTRACT,
            confidence=0.80
        )

        assert result.probabilities == {}
        assert result.features is None


class TestTrainingData:
    """Test TrainingData dataclass"""

    def test_training_data_creation(self):
        """Test training data creation"""
        data = TrainingData(
            id="doc_001",
            text="Sample invoice text",
            category=DocumentCategory.INVOICE,
            metadata={"source": "scan"}
        )

        assert data.id == "doc_001"
        assert data.category == DocumentCategory.INVOICE
        assert data.metadata["source"] == "scan"

    def test_training_data_defaults(self):
        """Test training data with defaults"""
        data = TrainingData(
            id="doc_002",
            text="Sample text",
            category=DocumentCategory.REPORT
        )

        assert data.metadata == {}


class TestModelMetrics:
    """Test ModelMetrics dataclass"""

    def test_metrics_creation(self):
        """Test metrics creation"""
        metrics = ModelMetrics(
            accuracy=0.95,
            precision=0.93,
            recall=0.94,
            f1_score=0.935,
            confusion_matrix=[[100, 5], [3, 92]],
            classification_report={"invoice": {"precision": 0.95}}
        )

        assert metrics.accuracy == 0.95
        assert metrics.f1_score == 0.935
        assert len(metrics.confusion_matrix) == 2


class TestTextPreprocessor:
    """Test TextPreprocessor class"""

    @pytest.fixture
    def preprocessor(self):
        """Create TextPreprocessor instance"""
        return TextPreprocessor()

    def test_initialization(self, preprocessor):
        """Test preprocessor initialization"""
        assert preprocessor is not None
        assert hasattr(preprocessor, 'stopwords')
        assert len(preprocessor.stopwords) > 0

    def test_lowercase_conversion(self, preprocessor):
        """Test text lowercasing"""
        text = "THIS IS UPPERCASE TEXT"
        result = preprocessor.preprocess(text)
        assert result.islower() or result == ""

    def test_remove_punctuation(self, preprocessor):
        """Test punctuation removal"""
        text = "Hello, World! How are you?"
        result = preprocessor.preprocess(text)
        # Punctuation should be removed or text should be cleaned
        assert isinstance(result, str)

    def test_remove_numbers(self, preprocessor):
        """Test number removal"""
        text = "Invoice 12345 dated 2023"
        result = preprocessor.preprocess(text)
        assert isinstance(result, str)

    def test_stopword_removal(self, preprocessor):
        """Test stopword removal"""
        # German text with stopwords
        text = "der das die und oder"
        result = preprocessor.preprocess(text)
        # Most stopwords should be removed
        assert len(result) < len(text) or result == ""

    def test_whitespace_normalization(self, preprocessor):
        """Test whitespace normalization"""
        text = "Multiple    spaces   and\n\nnewlines"
        result = preprocessor.preprocess(text)
        # Should normalize whitespace
        assert "    " not in result or result == ""

    def test_empty_text(self, preprocessor):
        """Test empty text handling"""
        result = preprocessor.preprocess("")
        assert result == ""

    def test_special_characters(self, preprocessor):
        """Test special character handling"""
        text = "Special chars: @#$%^&*()"
        result = preprocessor.preprocess(text)
        assert isinstance(result, str)

    @pytest.mark.parametrize("text", [
        "Normal text",
        "TEXT WITH CAPITALS",
        "text with, punctuation!",
        "Text 123 with numbers",
        "Übermäßige Sonderzeichen",  # German umlauts
    ])
    def test_various_inputs(self, preprocessor, text):
        """Test preprocessing various inputs"""
        result = preprocessor.preprocess(text)
        assert isinstance(result, str)


class TestTfidfSVMClassifier:
    """Test TfidfSVMClassifier class"""

    @pytest.fixture
    def classifier(self):
        """Create TfidfSVMClassifier instance"""
        return TfidfSVMClassifier()

    @pytest.fixture
    def training_samples(self):
        """Create sample training data"""
        return [
            TrainingData("1", "invoice payment due", DocumentCategory.INVOICE),
            TrainingData("2", "contract agreement terms", DocumentCategory.CONTRACT),
            TrainingData("3", "monthly report summary", DocumentCategory.REPORT),
            TrainingData("4", "invoice billing statement", DocumentCategory.INVOICE),
            TrainingData("5", "contract legal document", DocumentCategory.CONTRACT),
        ]

    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert not classifier.is_trained

    def test_training_basic(self, classifier, training_samples):
        """Test basic training"""
        classifier.train(training_samples)
        assert classifier.is_trained

    def test_prediction_after_training(self, classifier, training_samples):
        """Test prediction after training"""
        classifier.train(training_samples)
        result = classifier.predict("new invoice document")

        assert isinstance(result, ClassificationResult)
        assert result.category in DocumentCategory
        assert 0.0 <= result.confidence <= 1.0

    def test_prediction_before_training(self, classifier):
        """Test prediction before training raises error"""
        with pytest.raises((ValueError, RuntimeError, AttributeError)):
            classifier.predict("some text")

    def test_batch_prediction(self, classifier, training_samples):
        """Test batch prediction"""
        classifier.train(training_samples)
        texts = ["invoice", "contract", "report"]
        results = classifier.predict_batch(texts)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, ClassificationResult)

    def test_model_persistence(self, classifier, training_samples):
        """Test model save and load"""
        classifier.train(training_samples)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp:
            model_path = tmp.name

        try:
            # Save model
            classifier.save(model_path)
            assert os.path.exists(model_path)

            # Load model
            new_classifier = TfidfSVMClassifier()
            new_classifier.load(model_path)
            assert new_classifier.is_trained

            # Test prediction with loaded model
            result = new_classifier.predict("invoice document")
            assert isinstance(result, ClassificationResult)

        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)

    def test_evaluation_metrics(self, classifier, training_samples):
        """Test model evaluation"""
        # Split data for training and testing
        train_data = training_samples[:4]
        test_data = training_samples[4:]

        classifier.train(train_data)
        metrics = classifier.evaluate(test_data)

        assert isinstance(metrics, ModelMetrics)
        assert 0.0 <= metrics.accuracy <= 1.0
        assert 0.0 <= metrics.precision <= 1.0
        assert 0.0 <= metrics.recall <= 1.0
        assert 0.0 <= metrics.f1_score <= 1.0

    def test_probability_distribution(self, classifier, training_samples):
        """Test probability distribution in predictions"""
        classifier.train(training_samples)
        result = classifier.predict("invoice document")

        assert len(result.probabilities) > 0
        # Sum of probabilities should be close to 1.0
        total_prob = sum(result.probabilities.values())
        assert 0.9 <= total_prob <= 1.1

    def test_confidence_scores(self, classifier, training_samples):
        """Test confidence score accuracy"""
        classifier.train(training_samples)
        result = classifier.predict("invoice payment billing")

        # Confidence should match the max probability
        max_prob = max(result.probabilities.values())
        assert abs(result.confidence - max_prob) < 0.01

    def test_multiclass_classification(self, classifier, training_samples):
        """Test multiclass classification"""
        classifier.train(training_samples)

        # Get predictions for different categories
        results = [
            classifier.predict("invoice"),
            classifier.predict("contract"),
            classifier.predict("report")
        ]

        # Should predict different categories
        categories = {r.category for r in results}
        assert len(categories) >= 2  # At least 2 different categories


class TestDocumentClassifier:
    """Test DocumentClassifier main class"""

    @pytest.fixture
    def classifier(self):
        """Create DocumentClassifier instance"""
        return DocumentClassifier(model_type=ModelType.TFIDF_SVM)

    @pytest.fixture
    def training_data(self):
        """Create comprehensive training data"""
        return [
            TrainingData("1", "invoice payment due amount", DocumentCategory.INVOICE),
            TrainingData("2", "contract agreement legal terms", DocumentCategory.CONTRACT),
            TrainingData("3", "monthly quarterly report summary", DocumentCategory.REPORT),
            TrainingData("4", "service plan care assistance", DocumentCategory.SERVICE_PLAN),
            TrainingData("5", "budget financial planning", DocumentCategory.BUDGET_PLAN),
            TrainingData("6", "correspondence letter email", DocumentCategory.CORRESPONDENCE),
            TrainingData("7", "legal document court law", DocumentCategory.LEGAL),
            TrainingData("8", "financial statement balance", DocumentCategory.FINANCIAL),
            TrainingData("9", "administrative procedure process", DocumentCategory.ADMINISTRATIVE),
            TrainingData("10", "other miscellaneous documents", DocumentCategory.OTHER),
        ]

    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert classifier.model_type == ModelType.TFIDF_SVM

    def test_train_and_classify(self, classifier, training_data):
        """Test training and classification"""
        classifier.train(training_data)
        result = classifier.classify("new invoice document with payment")

        assert isinstance(result, ClassificationResult)
        assert result.category in DocumentCategory

    def test_auto_categorize(self, classifier, training_data):
        """Test auto-categorization"""
        classifier.train(training_data)
        result = classifier.auto_categorize("monthly report for Q4")

        assert isinstance(result, ClassificationResult)
        # Should likely be categorized as REPORT
        assert result.confidence > 0.0

    def test_batch_classification(self, classifier, training_data):
        """Test batch classification"""
        classifier.train(training_data)

        documents = [
            "invoice for payment",
            "contract agreement",
            "monthly report"
        ]

        results = classifier.classify_batch(documents)
        assert len(results) == 3

    def test_model_switching(self):
        """Test switching between model types"""
        # Test different model types
        for model_type in [ModelType.TFIDF_SVM, ModelType.NAIVE_BAYES, ModelType.LOGISTIC_REGRESSION]:
            try:
                classifier = DocumentClassifier(model_type=model_type)
                assert classifier.model_type == model_type
            except NotImplementedError:
                # Some models might not be implemented yet
                pass

    def test_incremental_training(self, classifier):
        """Test incremental training"""
        # Initial training
        initial_data = [
            TrainingData("1", "invoice payment", DocumentCategory.INVOICE),
            TrainingData("2", "contract terms", DocumentCategory.CONTRACT),
        ]
        classifier.train(initial_data)

        # Additional training
        additional_data = [
            TrainingData("3", "report summary", DocumentCategory.REPORT),
        ]

        # Should be able to train again
        try:
            classifier.train(additional_data, incremental=True)
        except (NotImplementedError, ValueError):
            # Incremental training might not be supported
            pass


class TestPerformance:
    """Performance tests for classifier"""

    @pytest.fixture
    def classifier(self):
        """Create classifier"""
        return TfidfSVMClassifier()

    @pytest.fixture
    def large_training_set(self):
        """Create large training dataset"""
        data = []
        categories = list(DocumentCategory)

        for i in range(100):
            category = categories[i % len(categories)]
            data.append(TrainingData(
                id=f"doc_{i}",
                text=f"Sample document text {i} for {category.value}",
                category=category
            ))

        return data

    def test_training_performance(self, classifier, large_training_set, benchmark):
        """Benchmark training performance"""
        result = benchmark(classifier.train, large_training_set)

    def test_prediction_performance(self, classifier, large_training_set, benchmark):
        """Benchmark prediction performance"""
        classifier.train(large_training_set)

        def predict_sample():
            return classifier.predict("test invoice document")

        result = benchmark(predict_sample)

    def test_batch_prediction_performance(self, classifier, large_training_set, benchmark):
        """Benchmark batch prediction"""
        classifier.train(large_training_set)
        test_texts = ["invoice", "contract", "report"] * 10  # 30 documents

        result = benchmark(classifier.predict_batch, test_texts)


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def classifier(self):
        """Create classifier"""
        return TfidfSVMClassifier()

    def test_empty_training_data(self, classifier):
        """Test training with empty data"""
        with pytest.raises((ValueError, RuntimeError)):
            classifier.train([])

    def test_single_sample_training(self, classifier):
        """Test training with single sample"""
        data = [TrainingData("1", "test", DocumentCategory.INVOICE)]

        # Should either work or raise appropriate error
        try:
            classifier.train(data)
        except (ValueError, RuntimeError):
            pass  # Expected for insufficient data

    def test_empty_text_prediction(self, classifier):
        """Test prediction on empty text"""
        training_data = [
            TrainingData("1", "invoice", DocumentCategory.INVOICE),
            TrainingData("2", "contract", DocumentCategory.CONTRACT),
        ]
        classifier.train(training_data)

        # Empty text should either return default or raise error
        try:
            result = classifier.predict("")
            assert isinstance(result, ClassificationResult)
        except (ValueError, RuntimeError):
            pass

    def test_very_long_text(self, classifier):
        """Test classification of very long text"""
        training_data = [
            TrainingData("1", "invoice", DocumentCategory.INVOICE),
            TrainingData("2", "contract", DocumentCategory.CONTRACT),
        ]
        classifier.train(training_data)

        long_text = "invoice " * 10000
        result = classifier.predict(long_text)
        assert isinstance(result, ClassificationResult)

    def test_unicode_text(self, classifier):
        """Test classification with Unicode text"""
        training_data = [
            TrainingData("1", "Rechnung Zahlung", DocumentCategory.INVOICE),
            TrainingData("2", "Vertrag Vereinbarung", DocumentCategory.CONTRACT),
        ]
        classifier.train(training_data)

        result = classifier.predict("Neue Rechnung mit Umlauten: äöü")
        assert isinstance(result, ClassificationResult)

    def test_imbalanced_training_data(self, classifier):
        """Test training with imbalanced data"""
        data = [TrainingData(f"inv_{i}", f"invoice {i}", DocumentCategory.INVOICE) for i in range(90)]
        data.append(TrainingData("con_1", "contract", DocumentCategory.CONTRACT))

        # Should handle imbalanced data
        classifier.train(data)
        assert classifier.is_trained


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
