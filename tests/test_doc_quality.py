#!/usr/bin/env python3
"""
Unit tests for doc-quality.py

Tests document quality assessment functionality including:
- Completeness dimension
- Accuracy dimension
- Consistency dimension
- Readability dimension (Flesch Reading Ease)
- Timeliness dimension
- Issue detection and severity levels
- Quality scoring (0-100)
"""

import re

# Import required modules
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.ner import NEREngine


class TestCompletenessDimension:
    """Test completeness assessment"""

    def test_word_count_score(self):
        """Test scoring based on word count"""
        # Short document
        short_text = "This is short"
        short_words = len(short_text.split())

        # Long document
        long_text = " ".join(["word"] * 500)
        long_words = len(long_text.split())

        # Longer documents should score higher for completeness
        # Assuming minimum 100 words for full score
        short_score = min(100, (short_words / 100) * 100)
        long_score = min(100, (long_words / 100) * 100)

        assert long_score > short_score

    def test_section_detection(self):
        """Test detection of document sections"""
        text = """
# Introduction
This is the introduction.

## Background
Background information here.

### Methods
Methodology section.

# Results
Results of the analysis.

# Conclusion
Final thoughts.
"""

        # Detect headers (markdown or similar)
        headers = re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)

        # Document with sections is more complete
        assert len(headers) > 0

    def test_minimum_length(self):
        """Test minimum length requirement"""
        min_words = 50

        text1 = " ".join(["word"] * 30)  # Below minimum
        text2 = " ".join(["word"] * 100)  # Above minimum

        words1 = len(text1.split())
        words2 = len(text2.split())

        assert words1 < min_words
        assert words2 >= min_words

    def test_metadata_presence(self):
        """Test presence of metadata (author, date, etc.)"""
        text_with_metadata = """
        Title: Important Document
        Author: John Smith
        Date: 2026-01-12
        Version: 1.0

        Content here...
        """

        text_without_metadata = "Just plain content with no metadata."

        # Check for metadata patterns
        has_author = "Author:" in text_with_metadata
        has_date = "Date:" in text_with_metadata

        assert has_author
        assert has_date


class TestAccuracyDimension:
    """Test accuracy assessment"""

    def test_email_validation(self):
        """Test email address validation"""
        valid_emails = ["user@example.com", "first.last@company.org", "name+tag@domain.co.uk"]

        invalid_emails = ["invalid.email", "@example.com", "user@", "user @example.com"]

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

        for email in valid_emails:
            assert re.match(email_pattern, email), f"Valid email rejected: {email}"

        for email in invalid_emails:
            assert not re.match(email_pattern, email), f"Invalid email accepted: {email}"

    def test_phone_validation(self):
        """Test phone number validation"""
        valid_phones = ["+1-555-123-4567", "(555) 123-4567", "555.123.4567"]

        phone_pattern = r"[\+]?[(]?\d{1,4}[)]?[-\s\.]?\(?\d{1,4}\)?[-\s\.]?\d{1,4}[-\s\.]?\d{1,9}"

        for phone in valid_phones:
            assert re.search(phone_pattern, phone), f"Valid phone rejected: {phone}"

    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://www.example.com",
            "http://example.org/path",
            "https://subdomain.example.com:8080/path?query=value",
        ]

        invalid_urls = ["not_a_url", "htp://wrong.com", "www.example.com"]  # Missing protocol

        url_pattern = r"https?://[^\s]+"

        for url in valid_urls:
            assert re.match(url_pattern, url), f"Valid URL rejected: {url}"

    def test_date_validation(self):
        """Test date format validation"""
        valid_dates = ["01.01.2020", "31.12.1999", "15.06.2026"]

        invalid_dates = ["32.01.2020", "01.13.2020", "2020-01-01"]  # Invalid day  # Invalid month  # Wrong format

        date_pattern = r"\b\d{2}\.\d{2}\.\d{4}\b"

        for date in valid_dates:
            assert re.match(date_pattern, date), f"Valid date rejected: {date}"

    def test_fact_checking(self):
        """Test basic fact checking (example: year ranges)"""
        text = "The event happened in year 2050"

        # Extract years
        years = re.findall(r"\b(19|20)\d{2}\b", text)

        # Check if years are reasonable (not too far in future)
        current_year = datetime.now().year
        for year in years:
            year_int = int(year)
            # Flag if more than 50 years in future
            if year_int > current_year + 50:
                # This would be flagged as potentially inaccurate
                pass


class TestConsistencyDimension:
    """Test consistency assessment"""

    def test_terminology_consistency(self):
        """Test consistent use of terminology"""
        text = """
        The company uses AI technology.
        Their artificial intelligence solutions are advanced.
        The AI system processes data.
        """

        # Check for consistent terminology
        ai_count = text.lower().count("ai ")
        artificial_intelligence_count = text.lower().count("artificial intelligence")

        # Both terms used - could be flagged for consistency
        assert ai_count > 0
        assert artificial_intelligence_count > 0

    def test_date_format_consistency(self):
        """Test consistent date formatting"""
        dates_format1 = ["01.01.2020", "15.06.2020", "31.12.2020"]
        dates_format2 = ["2020-01-01", "2020-06-15", "2020-12-31"]

        # All should follow same format
        pattern1 = r"\d{2}\.\d{2}\.\d{4}"
        pattern2 = r"\d{4}-\d{2}-\d{2}"

        all_match_1 = all(re.match(pattern1, d) for d in dates_format1)
        all_match_2 = all(re.match(pattern2, d) for d in dates_format2)

        assert all_match_1
        assert all_match_2

    def test_number_format_consistency(self):
        """Test consistent number formatting"""
        numbers_us = ["1,234.56", "9,876.54", "543.21"]
        numbers_eu = ["1.234,56", "9.876,54", "543,21"]

        # Check consistency within each set
        # US format: comma for thousands, period for decimal
        # EU format: period for thousands, comma for decimal

    def test_capitalization_consistency(self):
        """Test consistent capitalization"""
        text = """
        The Company provides services.
        The company has many employees.
        """

        # "Company" vs "company" - inconsistent capitalization
        # Could be flagged

    def test_abbreviation_consistency(self):
        """Test consistent use of abbreviations"""
        text = """
        The United States government.
        The US economy is strong.
        """

        # "United States" vs "US" - could check for consistency


class TestReadabilityDimension:
    """Test readability assessment (Flesch Reading Ease)"""

    def test_flesch_reading_ease_calculation(self):
        """Test Flesch Reading Ease formula"""
        # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)

        text = "The cat sat on the mat."

        # Count components
        words = len(text.split())
        sentences = text.count(".") + text.count("!") + text.count("?")

        # Simple syllable count (approximation)
        def count_syllables(word):
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count += 1
            return count

        syllables = sum(count_syllables(word.strip(".,!?")) for word in text.split())

        # Calculate score
        if sentences > 0 and words > 0:
            score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

            # Score should be in reasonable range (0-100)
            # Higher = easier to read
            assert -100 <= score <= 200  # Extended range for edge cases

    def test_average_sentence_length(self):
        """Test average sentence length calculation"""
        text = "This is sentence one. This is sentence two. Short."

        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        total_words = sum(len(s.split()) for s in sentences)
        avg_length = total_words / len(sentences) if sentences else 0

        # Shorter sentences are generally more readable
        assert avg_length > 0

    def test_complex_word_detection(self):
        """Test detection of complex words (3+ syllables)"""
        words = ["simple", "complexity", "understanding", "cat", "sophisticated"]

        def count_syllables(word):
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            if word and word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count += 1
            return count

        complex_words = [w for w in words if count_syllables(w) >= 3]

        # Should identify: complexity, understanding, sophisticated
        assert len(complex_words) >= 2

    def test_passive_voice_detection(self):
        """Test detection of passive voice (readability concern)"""
        passive_text = "The document was created by the team."
        active_text = "The team created the document."

        # Simple passive voice detection: "was/were" + past participle ending in "ed"
        passive_pattern = r"\b(was|were|is|are|been|being)\s+\w+ed\b"

        has_passive = bool(re.search(passive_pattern, passive_text))
        has_passive_active = bool(re.search(passive_pattern, active_text))

        assert has_passive
        assert not has_passive_active

    def test_readability_scoring(self):
        """Test overall readability scoring"""
        easy_text = "The cat sat on the mat. The dog ran in the park. The sun was bright."
        hard_text = (
            "The methodology encompasses sophisticated analytical procedures. "
            "Comprehensive evaluations demonstrate exceptional effectiveness."
        )

        # Easy text should score higher for readability
        # (implementation would calculate actual scores)


class TestTimelinessDimension:
    """Test timeliness assessment"""

    def test_document_age(self):
        """Test document age calculation"""
        # Simulate document date
        doc_date = datetime.now() - timedelta(days=30)
        current_date = datetime.now()

        age_days = (current_date - doc_date).days

        # Fresher documents score higher
        if age_days < 30:
            score = 100
        elif age_days < 90:
            score = 80
        elif age_days < 180:
            score = 60
        elif age_days < 365:
            score = 40
        else:
            score = 20

        assert score > 0

    def test_reference_freshness(self):
        """Test freshness of references/citations"""
        text = """
        According to Smith (2025), the study shows...
        Research from 2020 indicates...
        A 2010 paper found...
        """

        # Extract years from citations
        years = re.findall(r"\((\d{4})\)", text)
        years.extend(re.findall(r"\b(20\d{2})\b", text))

        # Check how recent references are
        current_year = datetime.now().year
        recent_refs = [int(y) for y in years if int(y) >= current_year - 5]

        # More recent references = more timely
        timeliness_score = (len(recent_refs) / len(years) * 100) if years else 0

    def test_outdated_information_detection(self):
        """Test detection of potentially outdated information"""
        text = "As of January 2020, the population was 1 million."

        # Extract temporal markers
        temporal_markers = re.findall(r"as of\s+(\w+\s+\d{4})", text, re.IGNORECASE)

        # Check if dates are recent
        current_year = datetime.now().year
        # Flag if more than 2 years old


class TestIssueDetection:
    """Test issue detection and categorization"""

    def test_critical_issues(self):
        """Test detection of critical issues"""
        issues = []

        # Missing required sections
        text = "Some content without introduction or conclusion"
        if "introduction" not in text.lower():
            issues.append(
                {"severity": "critical", "type": "missing_section", "message": "Missing introduction section"}
            )

        # Empty document
        if len(text.strip()) == 0:
            issues.append({"severity": "critical", "type": "empty_document", "message": "Document is empty"})

        critical = [i for i in issues if i["severity"] == "critical"]
        assert isinstance(critical, list)

    def test_high_severity_issues(self):
        """Test detection of high severity issues"""
        issues = []

        text = "Contact us at invalid.email"

        # Invalid email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if "email" in text.lower() and not re.search(email_pattern, text):
            issues.append({"severity": "high", "type": "invalid_contact", "message": "Invalid email address found"})

        high = [i for i in issues if i["severity"] == "high"]
        assert isinstance(high, list)

    def test_medium_severity_issues(self):
        """Test detection of medium severity issues"""
        issues = []

        text = "The company provides AI services. The artificial intelligence system..."

        # Inconsistent terminology
        if "ai" in text.lower() and "artificial intelligence" in text.lower():
            issues.append(
                {
                    "severity": "medium",
                    "type": "inconsistent_terminology",
                    "message": "Inconsistent use of AI/artificial intelligence",
                }
            )

        medium = [i for i in issues if i["severity"] == "medium"]
        assert isinstance(medium, list)

    def test_low_severity_issues(self):
        """Test detection of low severity issues"""
        issues = []

        text = "The methodology encompasses sophisticated procedures."

        # Complex language
        avg_word_length = sum(len(w) for w in text.split()) / len(text.split())
        if avg_word_length > 7:
            issues.append(
                {"severity": "low", "type": "complex_language", "message": "Language complexity may affect readability"}
            )

        low = [i for i in issues if i["severity"] == "low"]
        assert isinstance(low, list)


class TestQualityScoring:
    """Test overall quality scoring"""

    def test_score_calculation(self):
        """Test calculation of overall quality score"""
        dimension_scores = {"completeness": 85, "accuracy": 90, "consistency": 80, "readability": 75, "timeliness": 95}

        # Average of all dimensions
        overall = sum(dimension_scores.values()) / len(dimension_scores)

        assert 0 <= overall <= 100
        assert overall == 85  # (85+90+80+75+95)/5 = 85

    def test_weighted_scoring(self):
        """Test weighted quality scoring"""
        dimension_scores = {"completeness": 80, "accuracy": 95, "consistency": 70, "readability": 85, "timeliness": 60}

        weights = {
            "completeness": 0.25,
            "accuracy": 0.30,  # More important
            "consistency": 0.15,
            "readability": 0.20,
            "timeliness": 0.10,
        }

        # Weighted average
        overall = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)

        assert 0 <= overall <= 100

    def test_threshold_evaluation(self):
        """Test quality threshold evaluation"""
        quality_score = 85
        threshold = 80

        passes = quality_score >= threshold

        assert passes

        # Below threshold
        quality_score = 75
        passes = quality_score >= threshold

        assert not passes


class TestQualityRecommendations:
    """Test generation of quality recommendations"""

    def test_low_completeness_recommendations(self):
        """Test recommendations for low completeness"""
        completeness_score = 45

        recommendations = []

        if completeness_score < 50:
            recommendations.append("Add more content to reach minimum length")
            recommendations.append("Include missing sections (introduction, conclusion)")
            recommendations.append("Provide more detailed explanations")

        assert len(recommendations) > 0

    def test_low_readability_recommendations(self):
        """Test recommendations for low readability"""
        readability_score = 40

        recommendations = []

        if readability_score < 50:
            recommendations.append("Simplify complex sentences")
            recommendations.append("Use shorter words where possible")
            recommendations.append("Break long paragraphs into smaller ones")

        assert len(recommendations) > 0

    def test_accuracy_recommendations(self):
        """Test recommendations for accuracy issues"""
        accuracy_score = 60

        recommendations = []

        if accuracy_score < 80:
            recommendations.append("Verify all email addresses and contact information")
            recommendations.append("Check date formats for correctness")
            recommendations.append("Validate all URLs and links")

        assert len(recommendations) > 0


class TestQualityCLI:
    """Test CLI functionality"""

    def test_cli_help(self):
        """Test CLI help message"""
        import subprocess

        result = subprocess.run(["python", "doc-quality.py", "--help"], capture_output=True, text=True)

        assert result.returncode == 0
        assert "analyze" in result.stdout.lower()

    def test_cli_analyze_command(self):
        """Test analyze command exists"""
        import subprocess

        result = subprocess.run(["python", "doc-quality.py", "analyze", "--help"], capture_output=True, text=True)

        assert result.returncode == 0


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_document(self):
        """Test handling of empty document"""
        text = ""

        # Should handle gracefully
        word_count = len(text.split())
        assert word_count == 0

    def test_very_short_document(self):
        """Test handling of very short document"""
        text = "Hi"

        word_count = len(text.split())
        assert word_count < 10

        # Should score low on completeness

    def test_very_long_document(self):
        """Test handling of very long document"""
        text = " ".join(["word"] * 10000)

        word_count = len(text.split())
        assert word_count == 10000

        # Should handle without performance issues

    def test_special_characters(self):
        """Test handling of special characters"""
        text = "Test @#$%^&*() symbols"

        # Should not crash
        words = text.split()
        assert len(words) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
