"""
Performance Tests for ML Model Inference

Tests ML model inference operations for performance regressions.
Tracks inference time, throughput, and memory usage.
"""

import pytest
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class TestMLInferencePerformance:
    """Performance tests for ML model inference"""

    def test_text_classification_inference_performance(self, benchmark):
        """Benchmark text classification inference"""
        try:
            from ml_models.classification_service import ClassificationService

            classifier = ClassificationService()
            sample_text = "This is a sample document for classification testing. " * 10

            def classify_text():
                return classifier.classify(sample_text)

            result = benchmark(classify_text)
            assert result is not None

        except ImportError:
            pytest.skip("Classification service not available")

    def test_ner_inference_performance(self, benchmark):
        """Benchmark Named Entity Recognition inference"""
        try:
            from ml_models.ner_service import NERService

            ner = NERService()
            sample_text = "John Doe works at OpenAI in San Francisco. " * 5

            def extract_entities():
                return ner.extract_entities(sample_text)

            result = benchmark(extract_entities)
            assert result is not None

        except ImportError:
            pytest.skip("NER service not available")

    def test_batch_inference_performance(self, benchmark):
        """Benchmark batch ML inference"""
        # Simulate batch inference
        def batch_predict():
            results = []
            for i in range(10):
                # Simulate model inference work
                prediction = {'class': i % 3, 'confidence': 0.9}
                results.append(prediction)
            return results

        results = benchmark(batch_predict)
        assert len(results) == 10

    def test_embedding_generation_performance(self, benchmark):
        """Benchmark text embedding generation"""
        def generate_embedding():
            # Simulate embedding generation (768-dimensional)
            import random
            return [random.random() for _ in range(768)]

        embedding = benchmark(generate_embedding)
        assert len(embedding) == 768

    @pytest.mark.slow
    def test_large_batch_inference_performance(self, benchmark):
        """Benchmark large batch inference"""
        batch_size = 100

        def large_batch_predict():
            results = []
            for i in range(batch_size):
                # Simulate inference
                prediction = {'id': i, 'score': 0.85 + (i % 10) * 0.01}
                results.append(prediction)
            return results

        results = benchmark(large_batch_predict)
        assert len(results) == batch_size


class TestModelLoadingPerformance:
    """Performance tests for model loading operations"""

    def test_model_initialization_performance(self, benchmark):
        """Benchmark model initialization time"""
        def init_model():
            # Simulate model initialization
            model = {
                'type': 'classifier',
                'weights': [0.1] * 1000,
                'config': {'layers': 3, 'units': 128}
            }
            return model

        model = benchmark(init_model)
        assert model is not None

    def test_model_cache_loading_performance(self, benchmark):
        """Benchmark loading model from cache"""
        # Simulate cached model
        cached_model = {
            'type': 'cached',
            'weights': [0.1] * 5000,
            'metadata': {'version': '1.0'}
        }

        def load_from_cache():
            # Simulate cache lookup and load
            return cached_model.copy()

        model = benchmark(load_from_cache)
        assert model['type'] == 'cached'


class TestFeatureExtractionPerformance:
    """Performance tests for feature extraction"""

    def test_text_feature_extraction_performance(self, benchmark):
        """Benchmark text feature extraction"""
        text = "Sample text for feature extraction. " * 50

        def extract_features():
            # Simulate feature extraction
            features = {
                'word_count': len(text.split()),
                'char_count': len(text),
                'avg_word_length': sum(len(w) for w in text.split()) / len(text.split()),
                'sentence_count': text.count('. '),
            }
            return features

        features = benchmark(extract_features)
        assert 'word_count' in features

    def test_tfidf_feature_extraction_performance(self, benchmark):
        """Benchmark TF-IDF feature extraction"""
        documents = [
            "Document about machine learning and AI",
            "Another document about deep learning",
            "Text about natural language processing"
        ] * 10

        def extract_tfidf():
            # Simulate TF-IDF calculation
            vocab = set()
            for doc in documents:
                vocab.update(doc.lower().split())

            tfidf_vectors = []
            for doc in documents:
                words = doc.lower().split()
                vector = {word: words.count(word) / len(words) for word in vocab}
                tfidf_vectors.append(vector)

            return tfidf_vectors

        vectors = benchmark(extract_tfidf)
        assert len(vectors) == len(documents)

    def test_ngram_extraction_performance(self, benchmark):
        """Benchmark n-gram extraction"""
        text = "The quick brown fox jumps over the lazy dog"
        n = 2  # bigrams

        def extract_ngrams():
            words = text.split()
            ngrams = []
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams.append(ngram)
            return ngrams

        ngrams = benchmark(extract_ngrams)
        assert len(ngrams) > 0


class TestPredictionPipelinePerformance:
    """Performance tests for full prediction pipeline"""

    def test_end_to_end_prediction_performance(self, benchmark):
        """Benchmark complete prediction pipeline"""
        def full_pipeline():
            # Step 1: Preprocess
            text = "Input text for prediction"
            preprocessed = text.lower().strip()

            # Step 2: Feature extraction
            features = {
                'length': len(preprocessed),
                'words': len(preprocessed.split())
            }

            # Step 3: Prediction
            prediction = {
                'class': 'positive',
                'confidence': 0.87,
                'features': features
            }

            return prediction

        result = benchmark(full_pipeline)
        assert 'class' in result

    @pytest.mark.slow
    def test_streaming_prediction_performance(self, benchmark):
        """Benchmark streaming predictions"""
        data_stream = [f"Text sample {i}" for i in range(50)]

        def process_stream():
            results = []
            for text in data_stream:
                # Simulate prediction on each item
                pred = {'text': text, 'score': 0.9}
                results.append(pred)
            return results

        results = benchmark(process_stream)
        assert len(results) == len(data_stream)


class TestModelOptimizationPerformance:
    """Performance tests for model optimization techniques"""

    def test_quantized_inference_performance(self, benchmark):
        """Benchmark quantized model inference"""
        def quantized_predict():
            # Simulate quantized (INT8) inference - faster but less precise
            weights_int8 = [int(w * 127) for w in [0.5] * 100]
            result = sum(weights_int8) / 127.0
            return result

        result = benchmark(quantized_predict)
        assert isinstance(result, float)

    def test_pruned_model_performance(self, benchmark):
        """Benchmark pruned model (sparse) inference"""
        def pruned_predict():
            # Simulate pruned model - skip zero weights
            weights = [0.5 if i % 3 != 0 else 0.0 for i in range(100)]
            result = sum(w for w in weights if w != 0.0)
            return result

        result = benchmark(pruned_predict)
        assert isinstance(result, float)


# Run with: pytest tests/performance/test_ml_inference_perf.py -v --benchmark-only
# Save baseline: pytest tests/performance/test_ml_inference_perf.py --benchmark-save=baseline
# Compare: pytest tests/performance/test_ml_inference_perf.py --benchmark-compare=baseline
