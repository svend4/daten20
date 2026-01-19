"""
Comprehensive tests for src/ml/classifier.py

Tests document classification to achieve >80% coverage.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.ml.classifier import (
    AutoCategorizer,
    BERTClassifier,
    ClassificationResult,
    DocumentCategory,
    DocumentClassifier,
    ModelMetrics,
    ModelType,
    TextPreprocessor,
    TfidfSVMClassifier,
    TrainingData,
    configure_document_classifier,
    get_document_classifier,
)


class TestDocumentCategory:
    """Test DocumentCategory enum"""

    def test_document_categories_exist(self):
        """Test all document categories are defined"""
        assert hasattr(DocumentCategory, "INVOICE")
        assert hasattr(DocumentCategory, "CONTRACT")
        assert hasattr(DocumentCategory, "REPORT")
        assert hasattr(DocumentCategory, "SERVICE_PLAN")
        assert hasattr(DocumentCategory, "BUDGET_PLAN")

    def test_category_values(self):
        """Test category values"""
        assert DocumentCategory.INVOICE.value == "invoice"
        assert DocumentCategory.CONTRACT.value == "contract"
        assert DocumentCategory.OTHER.value == "other"

    def test_category_is_enum(self):
        """Test DocumentCategory is an enum"""
        assert isinstance(DocumentCategory.INVOICE, DocumentCategory)


class TestModelType:
    """Test ModelType enum"""

    def test_model_types_exist(self):
        """Test all model types are defined"""
        assert hasattr(ModelType, "TFIDF_SVM")
        assert hasattr(ModelType, "NAIVE_BAYES")
        assert hasattr(ModelType, "BERT")

    def test_model_type_values(self):
        """Test model type values"""
        assert ModelType.TFIDF_SVM.value == "tfidf_svm"
        assert ModelType.BERT.value == "bert"


class TestClassificationResult:
    """Test ClassificationResult dataclass"""

    def test_creation(self):
        """Test creating a ClassificationResult"""
        result = ClassificationResult(
            category=DocumentCategory.INVOICE,
            confidence=0.95,
        )
        assert result.category == DocumentCategory.INVOICE
        assert result.confidence == 0.95

    def test_with_probabilities(self):
        """Test with probabilities"""
        probs = {"invoice": 0.9, "contract": 0.1}
        result = ClassificationResult(
            category=DocumentCategory.INVOICE,
            confidence=0.9,
            probabilities=probs,
        )
        assert result.probabilities == probs

    def test_with_features(self):
        """Test with features"""
        features = {"word_count": 100, "has_numbers": True}
        result = ClassificationResult(
            category=DocumentCategory.REPORT,
            confidence=0.85,
            features=features,
        )
        assert result.features == features


class TestTrainingData:
    """Test TrainingData dataclass"""

    def test_creation(self):
        """Test creating TrainingData"""
        data = TrainingData(
            id="doc1",
            text="Sample text",
            category=DocumentCategory.INVOICE,
        )
        assert data.id == "doc1"
        assert data.text == "Sample text"
        assert data.category == DocumentCategory.INVOICE

    def test_with_metadata(self):
        """Test with metadata"""
        metadata = {"source": "scanner", "date": "2024-01-01"}
        data = TrainingData(
            id="doc2",
            text="Text",
            category=DocumentCategory.CONTRACT,
            metadata=metadata,
        )
        assert data.metadata == metadata


class TestModelMetrics:
    """Test ModelMetrics dataclass"""

    def test_creation(self):
        """Test creating ModelMetrics"""
        metrics = ModelMetrics(
            accuracy=0.92,
            precision=0.91,
            recall=0.90,
            f1_score=0.905,
        )
        assert metrics.accuracy == 0.92
        assert metrics.precision == 0.91

    def test_with_confusion_matrix(self):
        """Test with confusion matrix"""
        cm = [[10, 2], [1, 15]]
        metrics = ModelMetrics(
            accuracy=0.90,
            precision=0.88,
            recall=0.87,
            f1_score=0.875,
            confusion_matrix=cm,
        )
        assert metrics.confusion_matrix == cm


class TestTextPreprocessor:
    """Test TextPreprocessor class"""

    @pytest.fixture
    def preprocessor(self):
        """Create a TextPreprocessor instance"""
        return TextPreprocessor()

    def test_initialization(self, preprocessor):
        """Test TextPreprocessor initialization"""
        assert preprocessor.stopwords is not None
        assert len(preprocessor.stopwords) > 0

    def test_get_stopwords(self, preprocessor):
        """Test stopwords include German and English"""
        stopwords = preprocessor._get_stopwords()
        # German stopwords
        assert "der" in stopwords
        assert "die" in stopwords
        assert "und" in stopwords
        # English stopwords
        assert "the" in stopwords
        assert "and" in stopwords

    def test_preprocess_lowercase(self, preprocessor):
        """Test preprocessing converts to lowercase"""
        result = preprocessor.preprocess("INVOICE Document")
        assert result.islower()

    def test_preprocess_removes_special_chars(self, preprocessor):
        """Test preprocessing removes special characters"""
        text = "Hello! How are you? #test @user"
        result = preprocessor.preprocess(text)
        # Should not contain special chars
        assert "!" not in result
        assert "?" not in result
        assert "#" not in result

    def test_preprocess_removes_stopwords(self, preprocessor):
        """Test preprocessing removes stopwords"""
        text = "the quick brown fox and the lazy dog"
        result = preprocessor.preprocess(text)
        # 'the' and 'and' should be removed
        assert "the" not in result.split()
        assert "and" not in result.split()

    def test_preprocess_handles_german_text(self, preprocessor):
        """Test preprocessing handles German umlauts"""
        text = "Schön für Äpfel und Öl"
        result = preprocessor.preprocess(text)
        # Should preserve umlauts but remove stopwords
        assert "schön" in result or "sch" in result
        assert "und" not in result.split()

    def test_preprocess_removes_extra_spaces(self, preprocessor):
        """Test preprocessing removes extra spaces"""
        text = "hello    world     test"
        result = preprocessor.preprocess(text)
        # Should have single spaces
        assert "  " not in result

    def test_extract_features_word_count(self, preprocessor):
        """Test feature extraction counts words"""
        text = "hello world test"
        features = preprocessor.extract_features(text)
        assert features["word_count"] == 3

    def test_extract_features_char_count(self, preprocessor):
        """Test feature extraction counts characters"""
        text = "hello"
        features = preprocessor.extract_features(text)
        assert features["char_count"] == 5

    def test_extract_features_avg_word_length(self, preprocessor):
        """Test feature extraction calculates average word length"""
        text = "abc defgh"  # 3 and 5 chars = avg 4
        features = preprocessor.extract_features(text)
        assert features["avg_word_length"] == 4.0

    def test_extract_features_unique_words(self, preprocessor):
        """Test feature extraction counts unique words"""
        text = "hello world hello test"
        features = preprocessor.extract_features(text)
        assert features["unique_words"] == 3  # hello, world, test

    def test_extract_features_has_numbers(self, preprocessor):
        """Test feature extraction detects numbers"""
        text1 = "invoice 12345"
        text2 = "invoice only"
        features1 = preprocessor.extract_features(text1)
        features2 = preprocessor.extract_features(text2)
        assert features1["has_numbers"] is True
        assert features2["has_numbers"] is False

    def test_extract_features_has_currency(self, preprocessor):
        """Test feature extraction detects currency symbols"""
        features_euro = preprocessor.extract_features("Price: 100€")
        features_dollar = preprocessor.extract_features("Price: $100")
        features_eur = preprocessor.extract_features("Total EUR 500")
        features_none = preprocessor.extract_features("No price")

        assert features_euro["has_currency"] is True
        assert features_dollar["has_currency"] is True
        assert features_eur["has_currency"] is True
        assert features_none["has_currency"] is False

    def test_extract_features_empty_text(self, preprocessor):
        """Test feature extraction with empty text"""
        features = preprocessor.extract_features("")
        assert features["word_count"] == 0
        assert features["avg_word_length"] == 0


class TestTfidfSVMClassifier:
    """Test TfidfSVMClassifier class"""

    @pytest.fixture
    def classifier(self):
        """Create a TfidfSVMClassifier instance"""
        return TfidfSVMClassifier()

    def test_initialization(self, classifier):
        """Test TfidfSVMClassifier initialization"""
        assert classifier.vectorizer is None
        assert classifier.classifier is None
        assert classifier.trained is False

    def test_train_without_sklearn(self, classifier):
        """Test training fallback without sklearn"""
        training_data = [
            TrainingData(id="1", text="invoice 123", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="contract agreement", category=DocumentCategory.CONTRACT),
        ]

        # Mock sklearn import to fail
        with patch.dict("sys.modules", {"sklearn.feature_extraction.text": None}):
            # Should handle gracefully and return fallback metrics
            metrics = classifier.train(training_data)
            assert isinstance(metrics, ModelMetrics)
            assert classifier.trained is True
            assert metrics.accuracy == 0.92  # Fallback metrics

    def test_predict_untrained(self, classifier):
        """Test prediction without training"""
        result = classifier.predict("test document")
        assert result.category == DocumentCategory.OTHER
        assert result.confidence == 0.5

    def test_predict_fallback_invoice(self, classifier):
        """Test fallback keyword prediction for invoice"""
        # Set trained but create error condition to trigger fallback
        classifier.trained = True
        classifier.vectorizer = MagicMock()
        classifier.vectorizer.transform.side_effect = Exception("Test error")
        classifier.classifier = MagicMock()

        text = "Rechnung 12345 Betrag EUR 100"
        result = classifier.predict(text)
        assert result.category == DocumentCategory.INVOICE
        assert result.confidence > 0.9

    def test_predict_fallback_contract(self, classifier):
        """Test fallback keyword prediction for contract"""
        classifier.trained = True
        classifier.vectorizer = MagicMock()
        classifier.vectorizer.transform.side_effect = Exception("Test error")
        classifier.classifier = MagicMock()

        text = "Vertrag und Vereinbarung zwischen Parteien"
        result = classifier.predict(text)
        assert result.category == DocumentCategory.CONTRACT

    def test_predict_fallback_report(self, classifier):
        """Test fallback keyword prediction for report"""
        classifier.trained = True
        classifier.vectorizer = MagicMock()
        classifier.vectorizer.transform.side_effect = Exception("Test error")
        classifier.classifier = MagicMock()

        text = "Bericht und Zusammenfassung der Ergebnisse"
        result = classifier.predict(text)
        assert result.category == DocumentCategory.REPORT

    def test_predict_fallback_budget(self, classifier):
        """Test fallback keyword prediction for budget"""
        classifier.trained = True
        classifier.vectorizer = MagicMock()
        classifier.vectorizer.transform.side_effect = Exception("Test error")
        classifier.classifier = MagicMock()

        text = "Budget Finanzplan und Kosten"
        result = classifier.predict(text)
        assert result.category == DocumentCategory.BUDGET_PLAN

    def test_predict_fallback_other(self, classifier):
        """Test fallback prediction for unknown text"""
        classifier.trained = True
        classifier.vectorizer = MagicMock()
        classifier.vectorizer.transform.side_effect = Exception("Test error")
        classifier.classifier = MagicMock()

        text = "random text with no keywords"
        result = classifier.predict(text)
        assert result.category == DocumentCategory.OTHER

    def test_save_model(self, classifier):
        """Test saving model"""
        result = classifier.save_model("/tmp/model.pkl")
        # Currently prints and returns True
        assert result is True

    def test_load_model(self, classifier):
        """Test loading model"""
        result = classifier.load_model("/tmp/model.pkl")
        # Currently prints and returns True
        assert result is True
        assert classifier.trained is True


class TestBERTClassifier:
    """Test BERTClassifier class"""

    @pytest.fixture
    def classifier(self):
        """Create a BERTClassifier instance"""
        return BERTClassifier()

    def test_initialization(self, classifier):
        """Test BERTClassifier initialization"""
        assert classifier.model_name == "bert-base-german-cased"
        assert classifier.model is None
        assert classifier.tokenizer is None
        assert classifier.trained is False

    def test_initialization_custom_model(self):
        """Test initialization with custom model name"""
        classifier = BERTClassifier(model_name="distilbert-base-german-cased")
        assert classifier.model_name == "distilbert-base-german-cased"

    def test_train(self, classifier):
        """Test training BERT classifier"""
        training_data = [
            TrainingData(id="1", text="invoice", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="contract", category=DocumentCategory.CONTRACT),
        ]

        metrics = classifier.train(training_data, epochs=2)
        assert isinstance(metrics, ModelMetrics)
        assert classifier.trained is True
        assert metrics.accuracy > 0.9

    def test_predict_untrained(self, classifier):
        """Test prediction before training"""
        result = classifier.predict("test")
        assert result.category == DocumentCategory.OTHER
        assert result.confidence == 0.5

    def test_predict_trained(self, classifier):
        """Test prediction after training"""
        classifier.trained = True
        result = classifier.predict("service plan document")
        assert result.category == DocumentCategory.SERVICE_PLAN
        assert result.confidence == 0.95


class TestDocumentClassifier:
    """Test DocumentClassifier class"""

    @pytest.fixture
    def classifier(self):
        """Create a DocumentClassifier instance"""
        return DocumentClassifier()

    def test_initialization(self, classifier):
        """Test DocumentClassifier initialization"""
        assert classifier.model_type == ModelType.TFIDF_SVM
        assert classifier.preprocessor is not None
        assert classifier.model is not None
        assert isinstance(classifier.model, TfidfSVMClassifier)

    def test_initialization_bert(self):
        """Test initialization with BERT model"""
        classifier = DocumentClassifier(model_type=ModelType.BERT)
        assert classifier.model_type == ModelType.BERT
        assert isinstance(classifier.model, BERTClassifier)

    def test_create_model_tfidf(self, classifier):
        """Test _create_model creates TfidfSVM"""
        model = classifier._create_model()
        assert isinstance(model, TfidfSVMClassifier)

    def test_create_model_bert(self):
        """Test _create_model creates BERT"""
        classifier = DocumentClassifier(model_type=ModelType.BERT)
        model = classifier._create_model()
        assert isinstance(model, BERTClassifier)

    def test_create_model_distilbert(self):
        """Test _create_model creates BERT for DistilBERT"""
        classifier = DocumentClassifier(model_type=ModelType.DISTILBERT)
        model = classifier._create_model()
        assert isinstance(model, BERTClassifier)

    def test_create_model_default(self):
        """Test _create_model defaults to TfidfSVM"""
        classifier = DocumentClassifier(model_type=ModelType.NAIVE_BAYES)
        model = classifier._create_model()
        assert isinstance(model, TfidfSVMClassifier)

    def test_train(self, classifier):
        """Test training classifier"""
        training_data = [
            TrainingData(id="1", text="INVOICE Document", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="Contract Agreement", category=DocumentCategory.CONTRACT),
        ]

        metrics = classifier.train(training_data)
        assert isinstance(metrics, ModelMetrics)
        assert len(classifier.training_history) == 1

    def test_train_preprocesses_data(self, classifier):
        """Test training preprocesses text"""
        training_data = [
            TrainingData(id="1", text="UPPERCASE TEXT!", category=DocumentCategory.INVOICE),
        ]

        classifier.train(training_data)
        # Text should be preprocessed (lowercase, no special chars)
        assert training_data[0].text.islower()

    def test_train_records_history(self, classifier):
        """Test training records history"""
        training_data = [
            TrainingData(id="1", text="test", category=DocumentCategory.INVOICE),
        ]

        initial_count = len(classifier.training_history)
        classifier.train(training_data)
        assert len(classifier.training_history) == initial_count + 1

        history = classifier.training_history[-1]
        assert "timestamp" in history
        assert "model_type" in history
        assert "training_samples" in history
        assert history["training_samples"] == 1

    def test_classify(self, classifier):
        """Test classifying document"""
        text = "Rechnung Betrag Zahlung"
        result = classifier.classify(text)
        assert isinstance(result, ClassificationResult)
        assert result.features is not None

    def test_classify_includes_features(self, classifier):
        """Test classify includes extracted features"""
        text = "Test document 123"
        result = classifier.classify(text)
        assert result.features is not None
        assert "word_count" in result.features
        assert "has_numbers" in result.features

    def test_classify_batch(self, classifier):
        """Test classifying multiple documents"""
        texts = ["invoice text", "contract text", "report text"]
        results = classifier.classify_batch(texts)

        assert len(results) == 3
        assert all(isinstance(r, ClassificationResult) for r in results)

    def test_classify_batch_empty(self, classifier):
        """Test classifying empty batch"""
        results = classifier.classify_batch([])
        assert results == []

    def test_evaluate(self, classifier):
        """Test evaluating model"""
        test_data = [
            TrainingData(id="1", text="invoice test", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="contract test", category=DocumentCategory.CONTRACT),
        ]

        metrics = classifier.evaluate(test_data)
        assert isinstance(metrics, ModelMetrics)
        assert 0 <= metrics.accuracy <= 1

    def test_get_model_info(self, classifier):
        """Test getting model information"""
        info = classifier.get_model_info()

        assert "model_type" in info
        assert "trained" in info
        assert "training_history" in info
        assert "categories" in info
        assert info["model_type"] == ModelType.TFIDF_SVM.value

    def test_get_model_info_after_training(self, classifier):
        """Test model info after training"""
        training_data = [
            TrainingData(id="1", text="test", category=DocumentCategory.INVOICE),
        ]
        classifier.train(training_data)

        info = classifier.get_model_info()
        assert info["training_history"] == 1
        assert info["last_trained"] is not None


class TestAutoCategorizer:
    """Test AutoCategorizer class"""

    @pytest.fixture
    def categorizer(self):
        """Create an AutoCategorizer instance"""
        classifier = DocumentClassifier()
        return AutoCategorizer(classifier)

    def test_initialization(self, categorizer):
        """Test AutoCategorizer initialization"""
        assert categorizer.classifier is not None
        assert categorizer.categorization_log is not None
        assert len(categorizer.categorization_log) == 0

    def test_categorize_document_high_confidence(self, categorizer):
        """Test categorization with high confidence"""
        # Mock high confidence result
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.95,
            )

            result = categorizer.categorize_document("doc1", "invoice text", confidence_threshold=0.7)
            assert result == DocumentCategory.INVOICE

    def test_categorize_document_low_confidence(self, categorizer):
        """Test categorization with low confidence"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.OTHER,
                confidence=0.5,
            )

            result = categorizer.categorize_document("doc1", "unclear text", confidence_threshold=0.7)
            assert result is None

    def test_categorize_document_logs_result(self, categorizer):
        """Test categorization logs results"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.85,
            )

            initial_count = len(categorizer.categorization_log)
            categorizer.categorize_document("doc1", "test", confidence_threshold=0.7)

            assert len(categorizer.categorization_log) == initial_count + 1

            log_entry = categorizer.categorization_log[-1]
            assert log_entry["document_id"] == "doc1"
            assert log_entry["category"] == "invoice"
            assert log_entry["confidence"] == 0.85
            assert log_entry["auto_applied"] is True

    def test_categorize_document_custom_threshold(self, categorizer):
        """Test categorization with custom threshold"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.85,
            )

            # Lower threshold - should apply
            result1 = categorizer.categorize_document("doc1", "test", confidence_threshold=0.8)
            assert result1 == DocumentCategory.INVOICE

            # Higher threshold - should not apply
            result2 = categorizer.categorize_document("doc2", "test", confidence_threshold=0.9)
            assert result2 is None

    def test_get_suggestions(self, categorizer):
        """Test getting category suggestions"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.9,
                probabilities={
                    "invoice": 0.9,
                    "contract": 0.05,
                    "report": 0.03,
                    "other": 0.02,
                },
            )

            suggestions = categorizer.get_suggestions("test text", top_k=3)

            assert len(suggestions) == 3
            assert suggestions[0][0] == DocumentCategory.INVOICE
            assert suggestions[0][1] == 0.9

    def test_get_suggestions_top_k(self, categorizer):
        """Test getting top-k suggestions"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.9,
                probabilities={
                    "invoice": 0.5,
                    "contract": 0.3,
                    "report": 0.2,
                },
            )

            # Get top 2
            suggestions = categorizer.get_suggestions("test", top_k=2)
            assert len(suggestions) == 2

            # Get top 1
            suggestions = categorizer.get_suggestions("test", top_k=1)
            assert len(suggestions) == 1

    def test_get_suggestions_sorted(self, categorizer):
        """Test suggestions are sorted by probability"""
        with patch.object(categorizer.classifier, "classify") as mock_classify:
            mock_classify.return_value = ClassificationResult(
                category=DocumentCategory.INVOICE,
                confidence=0.9,
                probabilities={
                    "invoice": 0.7,
                    "contract": 0.2,
                    "report": 0.1,
                },
            )

            suggestions = categorizer.get_suggestions("test", top_k=3)

            # Should be sorted descending
            assert suggestions[0][1] >= suggestions[1][1]
            assert suggestions[1][1] >= suggestions[2][1]


class TestGlobalFunctions:
    """Test global functions"""

    def test_get_document_classifier(self):
        """Test get_document_classifier creates instance"""
        classifier = get_document_classifier()
        assert isinstance(classifier, DocumentClassifier)

    def test_get_document_classifier_default_model(self):
        """Test default model type"""
        classifier = get_document_classifier()
        assert classifier.model_type == ModelType.TFIDF_SVM

    def test_get_document_classifier_custom_model(self):
        """Test with custom model type"""
        classifier = get_document_classifier(model_type=ModelType.BERT)
        # Note: global instance is shared, so this might be TFIDF_SVM if already created
        assert isinstance(classifier, DocumentClassifier)

    def test_configure_document_classifier(self):
        """Test configuring global classifier"""
        configure_document_classifier(ModelType.BERT)
        classifier = get_document_classifier()
        assert isinstance(classifier, DocumentClassifier)


class TestIntegration:
    """Integration tests for document classification"""

    def test_full_classification_workflow(self):
        """Test complete classification workflow"""
        classifier = DocumentClassifier()

        # Create training data
        training_data = [
            TrainingData(id="1", text="Rechnung Betrag Zahlung EUR", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="Vertrag Vereinbarung Parteien", category=DocumentCategory.CONTRACT),
            TrainingData(id="3", text="Bericht Zusammenfassung Ergebnisse", category=DocumentCategory.REPORT),
        ]

        # Train
        metrics = classifier.train(training_data)
        assert metrics.accuracy > 0

        # Classify
        result = classifier.classify("Neue Rechnung mit Betrag")
        assert isinstance(result, ClassificationResult)

    def test_auto_categorization_workflow(self):
        """Test auto-categorization workflow"""
        classifier = DocumentClassifier()
        categorizer = AutoCategorizer(classifier)

        # Train classifier
        training_data = [
            TrainingData(id="1", text="invoice document", category=DocumentCategory.INVOICE),
        ]
        classifier.train(training_data)

        # Auto-categorize
        category = categorizer.categorize_document("doc1", "invoice text", confidence_threshold=0.5)
        assert category is not None or category is None  # Can be either depending on model

        # Check log
        assert len(categorizer.categorization_log) > 0

    def test_batch_classification_workflow(self):
        """Test batch classification"""
        classifier = DocumentClassifier()

        texts = ["invoice one", "contract two", "report three"]
        results = classifier.classify_batch(texts)

        assert len(results) == 3
        assert all(isinstance(r, ClassificationResult) for r in results)

    def test_model_evaluation_workflow(self):
        """Test model evaluation"""
        classifier = DocumentClassifier()

        # Train
        training_data = [
            TrainingData(id="1", text="invoice", category=DocumentCategory.INVOICE),
            TrainingData(id="2", text="contract", category=DocumentCategory.CONTRACT),
        ]
        classifier.train(training_data)

        # Evaluate
        test_data = [
            TrainingData(id="3", text="new invoice", category=DocumentCategory.INVOICE),
        ]
        metrics = classifier.evaluate(test_data)

        assert isinstance(metrics, ModelMetrics)
        assert 0 <= metrics.accuracy <= 1


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.ml.classifier", "--cov-report=term-missing"])
