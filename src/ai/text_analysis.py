"""
Text Analysis Engine

Advanced NLP and text processing including sentiment analysis, emotion detection,
text classification, NER, keyword extraction, and readability scoring.

Part of v3.5 AI/ML Services implementation.
"""

import logging
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .llm_integration import get_llm_client

logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Sentiment labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionLabel(Enum):
    """Emotion labels."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    label: SentimentLabel
    score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    scores: Dict[str, float] = field(default_factory=dict)  # All sentiment scores


@dataclass
class EmotionResult:
    """Emotion detection result."""
    primary_emotion: EmotionLabel
    confidence: float
    all_emotions: Dict[EmotionLabel, float] = field(default_factory=dict)


@dataclass
class Keyword:
    """Extracted keyword."""
    word: str
    score: float
    frequency: int
    positions: List[int] = field(default_factory=list)


@dataclass
class TextClassification:
    """Text classification result."""
    category: str
    confidence: float
    all_categories: Dict[str, float] = field(default_factory=dict)


@dataclass
class LanguageDetection:
    """Language detection result."""
    language: str
    confidence: float
    iso_code: str


@dataclass
class ReadabilityMetrics:
    """Text readability metrics."""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_word_length: float
    complex_word_ratio: float
    difficulty_level: str  # easy, medium, hard


class TextTokenizer:
    """Text tokenization utilities."""

    @staticmethod
    def tokenize_words(text: str) -> List[str]:
        """Tokenize text into words."""
        # Simple word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    @staticmethod
    def tokenize_sentences(text: str) -> List[str]:
        """Tokenize text into sentences."""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def remove_stopwords(words: List[str], language: str = "en") -> List[str]:
        """Remove stopwords from word list."""
        stopwords = STOPWORDS.get(language, STOPWORDS["en"])
        return [w for w in words if w not in stopwords]

    @staticmethod
    def stem_word(word: str) -> str:
        """Simple word stemming."""
        # Very basic stemming - in production would use proper stemmer
        if word.endswith('ing'):
            return word[:-3]
        elif word.endswith('ed'):
            return word[:-2]
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        return word


# Simple stopwords lists
STOPWORDS = {
    "en": {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'but', 'or', 'not', 'have', 'had',
        'this', 'they', 'can', 'been', 'their', 'which', 'there', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'being'
    }
}


class SentimentAnalyzer:
    """Sentiment analysis using lexicon and LLM."""

    # Sentiment lexicon (simplified - in production would use VADER or similar)
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'best', 'perfect', 'happy', 'beautiful', 'brilliant',
        'awesome', 'outstanding', 'superb', 'terrific', 'magnificent'
    }

    NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
        'disappointing', 'useless', 'pathetic', 'ugly', 'disgusting',
        'dreadful', 'abysmal', 'atrocious', 'appalling', 'inferior'
    }

    # Intensifiers
    INTENSIFIERS = {
        'very', 'extremely', 'highly', 'absolutely', 'completely',
        'totally', 'really', 'incredibly', 'exceptionally'
    }

    # Negations
    NEGATIONS = {
        'not', 'no', 'never', 'neither', 'nobody', 'nothing', 'none',
        'nowhere', 'hardly', 'scarcely', 'barely'
    }

    def analyze(self, text: str, use_llm: bool = False) -> SentimentResult:
        """Analyze sentiment of text."""
        if use_llm:
            return self._analyze_with_llm(text)
        else:
            return self._analyze_lexicon(text)

    def _analyze_lexicon(self, text: str) -> SentimentResult:
        """Lexicon-based sentiment analysis."""
        words = TextTokenizer.tokenize_words(text)

        positive_count = 0
        negative_count = 0
        negation_context = False

        for i, word in enumerate(words):
            # Check for negation
            if word in self.NEGATIONS:
                negation_context = True
                continue

            # Check for intensifier
            intensifier_boost = 1.5 if i > 0 and words[i-1] in self.INTENSIFIERS else 1.0

            # Check sentiment
            if word in self.POSITIVE_WORDS:
                if negation_context:
                    negative_count += intensifier_boost
                else:
                    positive_count += intensifier_boost
                negation_context = False
            elif word in self.NEGATIVE_WORDS:
                if negation_context:
                    positive_count += intensifier_boost
                else:
                    negative_count += intensifier_boost
                negation_context = False

        # Calculate sentiment score
        total = positive_count + negative_count
        if total == 0:
            label = SentimentLabel.NEUTRAL
            score = 0.0
            confidence = 0.5
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                label = SentimentLabel.POSITIVE
                confidence = min(abs(score), 1.0)
            elif score < -0.2:
                label = SentimentLabel.NEGATIVE
                confidence = min(abs(score), 1.0)
            else:
                label = SentimentLabel.NEUTRAL
                confidence = 1.0 - abs(score)

        return SentimentResult(
            label=label,
            score=score,
            confidence=confidence,
            scores={
                'positive': positive_count / max(total, 1),
                'negative': negative_count / max(total, 1),
                'neutral': 1.0 - (positive_count + negative_count) / max(len(words), 1)
            }
        )

    async def _analyze_with_llm(self, text: str) -> SentimentResult:
        """LLM-based sentiment analysis."""
        client = get_llm_client()

        prompt = f"""Analyze the sentiment of this text. Respond with only one word: positive, negative, or neutral.

Text: {text[:500]}

Sentiment:"""

        try:
            response = await client.complete(prompt, max_tokens=10)
            content = response.content.lower().strip()

            if 'positive' in content:
                label = SentimentLabel.POSITIVE
                score = 0.7
            elif 'negative' in content:
                label = SentimentLabel.NEGATIVE
                score = -0.7
            else:
                label = SentimentLabel.NEUTRAL
                score = 0.0

            return SentimentResult(
                label=label,
                score=score,
                confidence=0.85,
                scores={label.value: 0.85}
            )

        except Exception as e:
            logger.error(f"LLM sentiment analysis failed: {e}")
            return self._analyze_lexicon(text)


class EmotionDetector:
    """Emotion detection from text."""

    # Emotion lexicon (simplified)
    EMOTION_WORDS = {
        EmotionLabel.JOY: {'happy', 'joy', 'delighted', 'pleased', 'cheerful', 'excited'},
        EmotionLabel.SADNESS: {'sad', 'unhappy', 'depressed', 'miserable', 'gloomy', 'disappointed'},
        EmotionLabel.ANGER: {'angry', 'furious', 'mad', 'irritated', 'annoyed', 'enraged'},
        EmotionLabel.FEAR: {'afraid', 'scared', 'frightened', 'terrified', 'worried', 'anxious'},
        EmotionLabel.SURPRISE: {'surprised', 'amazed', 'astonished', 'shocked', 'stunned'},
        EmotionLabel.DISGUST: {'disgusted', 'revolted', 'repulsed', 'appalled'},
        EmotionLabel.TRUST: {'trust', 'confident', 'secure', 'certain', 'assured'},
        EmotionLabel.ANTICIPATION: {'anticipate', 'expect', 'hope', 'eager', 'ready'}
    }

    def detect(self, text: str) -> EmotionResult:
        """Detect emotions in text."""
        words = TextTokenizer.tokenize_words(text)

        emotion_scores: Dict[EmotionLabel, float] = defaultdict(float)

        for word in words:
            for emotion, emotion_words in self.EMOTION_WORDS.items():
                if word in emotion_words:
                    emotion_scores[emotion] += 1.0

        if not emotion_scores:
            # Default to neutral/trust
            return EmotionResult(
                primary_emotion=EmotionLabel.TRUST,
                confidence=0.3,
                all_emotions={EmotionLabel.TRUST: 0.3}
            )

        # Normalize scores
        total = sum(emotion_scores.values())
        normalized = {e: s/total for e, s in emotion_scores.items()}

        primary_emotion = max(normalized.items(), key=lambda x: x[1])

        return EmotionResult(
            primary_emotion=primary_emotion[0],
            confidence=primary_emotion[1],
            all_emotions=normalized
        )


class KeywordExtractor:
    """Keyword extraction using TF-IDF and statistical methods."""

    def extract(
        self,
        text: str,
        top_k: int = 10,
        min_word_length: int = 3
    ) -> List[Keyword]:
        """Extract keywords from text."""
        words = TextTokenizer.tokenize_words(text)

        # Remove stopwords
        words = TextTokenizer.remove_stopwords(words)

        # Filter by length
        words = [w for w in words if len(w) >= min_word_length]

        # Calculate word frequencies
        word_freq = Counter(words)

        # Calculate positions
        word_positions: Dict[str, List[int]] = defaultdict(list)
        for i, word in enumerate(words):
            word_positions[word].append(i)

        # Score words (simple frequency-based)
        total_words = len(words)
        keywords = []

        for word, count in word_freq.most_common(top_k * 2):
            # Calculate TF
            tf = count / total_words

            # Simple importance score
            score = tf * math.log(len(word))  # Longer words often more important

            keywords.append(Keyword(
                word=word,
                score=score,
                frequency=count,
                positions=word_positions[word]
            ))

        # Sort by score and take top_k
        keywords.sort(key=lambda k: k.score, reverse=True)
        return keywords[:top_k]

    def extract_phrases(self, text: str, top_k: int = 5) -> List[str]:
        """Extract key phrases (n-grams)."""
        words = TextTokenizer.tokenize_words(text)

        # Extract bigrams and trigrams
        phrases = []

        # Bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            phrases.append(bigram)

        # Trigrams
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            phrases.append(trigram)

        # Count frequencies
        phrase_freq = Counter(phrases)

        # Get most common
        top_phrases = [phrase for phrase, _ in phrase_freq.most_common(top_k)]

        return top_phrases


class TextClassifier:
    """Text classification."""

    def classify(
        self,
        text: str,
        categories: List[str],
        use_llm: bool = True
    ) -> TextClassification:
        """Classify text into categories."""
        if use_llm:
            return self._classify_with_llm(text, categories)
        else:
            return self._classify_keyword(text, categories)

    def _classify_keyword(self, text: str, categories: List[str]) -> TextClassification:
        """Simple keyword-based classification."""
        words = set(TextTokenizer.tokenize_words(text))

        # Simple scoring based on category name appearance
        scores = {}
        for category in categories:
            category_words = set(TextTokenizer.tokenize_words(category))
            overlap = len(words & category_words)
            scores[category] = overlap

        if not any(scores.values()):
            # No match, return first category
            return TextClassification(
                category=categories[0],
                confidence=0.3,
                all_categories={categories[0]: 0.3}
            )

        total = sum(scores.values())
        normalized = {c: s/total for c, s in scores.items()}

        best_category = max(normalized.items(), key=lambda x: x[1])

        return TextClassification(
            category=best_category[0],
            confidence=best_category[1],
            all_categories=normalized
        )

    async def _classify_with_llm(
        self,
        text: str,
        categories: List[str]
    ) -> TextClassification:
        """LLM-based classification."""
        client = get_llm_client()

        prompt = f"""Classify this text into one of these categories: {', '.join(categories)}

Text: {text[:500]}

Category:"""

        try:
            response = await client.complete(prompt, max_tokens=20)
            content = response.content.lower().strip()

            # Find matching category
            for category in categories:
                if category.lower() in content:
                    return TextClassification(
                        category=category,
                        confidence=0.8,
                        all_categories={category: 0.8}
                    )

            # Fallback
            return TextClassification(
                category=categories[0],
                confidence=0.5,
                all_categories={categories[0]: 0.5}
            )

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self._classify_keyword(text, categories)


class LanguageDetector:
    """Language detection."""

    # Common words in different languages (simplified)
    LANGUAGE_PATTERNS = {
        'en': {'the', 'is', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'for'},
        'es': {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'por', 'los'},
        'fr': {'le', 'de', 'un', 'et', 'être', 'à', 'il', 'avoir', 'ne', 'pour'},
        'de': {'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'ist'},
        'ru': {'и', 'в', 'не', 'на', 'я', 'что', 'он', 'с', 'это', 'как'},
    }

    ISO_CODES = {
        'en': 'eng',
        'es': 'spa',
        'fr': 'fra',
        'de': 'deu',
        'ru': 'rus',
    }

    def detect(self, text: str) -> LanguageDetection:
        """Detect language of text."""
        words = set(TextTokenizer.tokenize_words(text))

        scores = {}
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            overlap = len(words & patterns)
            scores[lang] = overlap

        if not any(scores.values()):
            # Default to English
            return LanguageDetection(
                language='English',
                confidence=0.3,
                iso_code='eng'
            )

        best_lang = max(scores.items(), key=lambda x: x[1])[0]
        confidence = scores[best_lang] / sum(scores.values())

        lang_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ru': 'Russian',
        }

        return LanguageDetection(
            language=lang_names.get(best_lang, 'Unknown'),
            confidence=confidence,
            iso_code=self.ISO_CODES.get(best_lang, 'unk')
        )


class ReadabilityAnalyzer:
    """Text readability analysis."""

    def analyze(self, text: str) -> ReadabilityMetrics:
        """Calculate readability metrics."""
        sentences = TextTokenizer.tokenize_sentences(text)
        words = TextTokenizer.tokenize_words(text)

        if not sentences or not words:
            return ReadabilityMetrics(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                avg_sentence_length=0.0,
                avg_word_length=0.0,
                complex_word_ratio=0.0,
                difficulty_level="unknown"
            )

        # Calculate metrics
        num_sentences = len(sentences)
        num_words = len(words)
        num_syllables = sum(self._count_syllables(w) for w in words)

        avg_sentence_length = num_words / num_sentences
        avg_syllables_per_word = num_syllables / num_words
        avg_word_length = sum(len(w) for w in words) / num_words

        # Complex words (3+ syllables)
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_word_ratio = len(complex_words) / num_words

        # Flesch Reading Ease
        flesch_reading_ease = (
            206.835
            - 1.015 * avg_sentence_length
            - 84.6 * avg_syllables_per_word
        )

        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (
            0.39 * avg_sentence_length
            + 11.8 * avg_syllables_per_word
            - 15.59
        )

        # Determine difficulty level
        if flesch_reading_ease >= 60:
            difficulty = "easy"
        elif flesch_reading_ease >= 30:
            difficulty = "medium"
        else:
            difficulty = "hard"

        return ReadabilityMetrics(
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid_grade,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            complex_word_ratio=complex_word_ratio,
            difficulty_level=difficulty
        )

    def _count_syllables(self, word: str) -> int:
        """Count syllables in word (simplified)."""
        word = word.lower()
        vowels = 'aeiou'

        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1

        # Ensure at least one syllable
        return max(1, syllable_count)


class TextSimilarity:
    """Text similarity calculation."""

    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(TextTokenizer.tokenize_words(text1))
        words2 = set(TextTokenizer.tokenize_words(text2))

        intersection = words1 & words2
        union = words1 | words2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    @staticmethod
    def cosine_similarity(text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        words1 = TextTokenizer.tokenize_words(text1)
        words2 = TextTokenizer.tokenize_words(text2)

        # Create word frequency vectors
        all_words = set(words1 + words2)
        vec1 = [words1.count(w) for w in all_words]
        vec2 = [words2.count(w) for w in all_words]

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


class TextAnalyzer:
    """Main text analysis service."""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_detector = EmotionDetector()
        self.keyword_extractor = KeywordExtractor()
        self.classifier = TextClassifier()
        self.language_detector = LanguageDetector()
        self.readability_analyzer = ReadabilityAnalyzer()

    async def analyze(
        self,
        text: str,
        operations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive text analysis."""
        if operations is None:
            operations = ["sentiment", "keywords", "readability"]

        results = {}

        if "sentiment" in operations:
            results["sentiment"] = self.sentiment_analyzer.analyze(text)

        if "emotion" in operations:
            results["emotion"] = self.emotion_detector.detect(text)

        if "keywords" in operations:
            results["keywords"] = self.keyword_extractor.extract(text)

        if "phrases" in operations:
            results["phrases"] = self.keyword_extractor.extract_phrases(text)

        if "language" in operations:
            results["language"] = self.language_detector.detect(text)

        if "readability" in operations:
            results["readability"] = self.readability_analyzer.analyze(text)

        return results

    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Quick sentiment analysis."""
        return self.sentiment_analyzer.analyze(text)

    def extract_keywords(self, text: str, top_k: int = 10) -> List[Keyword]:
        """Quick keyword extraction."""
        return self.keyword_extractor.extract(text, top_k=top_k)

    def detect_language(self, text: str) -> LanguageDetection:
        """Quick language detection."""
        return self.language_detector.detect(text)

    def calculate_readability(self, text: str) -> ReadabilityMetrics:
        """Quick readability analysis."""
        return self.readability_analyzer.analyze(text)


# Singleton instance
_text_analyzer: Optional[TextAnalyzer] = None


def get_text_analyzer() -> TextAnalyzer:
    """Get or create text analyzer."""
    global _text_analyzer

    if _text_analyzer is None:
        _text_analyzer = TextAnalyzer()

    return _text_analyzer
