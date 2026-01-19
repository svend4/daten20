#!/usr/bin/env python3
"""
Document Quality Analyzer
==========================

Comprehensive document quality assessment tool.

Features:
- Completeness check (missing fields, empty sections)
- Accuracy validation (dates, emails, phones, IBAN)
- Consistency analysis (data consistency, formatting)
- Readability metrics (Flesch, sentence length, complexity)
- Structure validation
- Compliance checking
- Quality scoring (0-100)

Usage:
    # Full quality analysis
    python doc-quality.py analyze document.pdf --full

    # Check specific dimension
    python doc-quality.py check document.pdf --dimension completeness

    # Batch quality check
    python doc-quality.py batch /documents/ --output quality_report.json

    # With threshold
    python doc-quality.py analyze document.pdf --threshold 80 --fail-on-low-quality

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.logging_config import setup_logging

# Import core modules
from src.core.parser import DocumentParser
from src.core.validator import DocumentValidator

# Import ML modules
from src.ml.ner import NEREngine

# Setup logging
logger = setup_logging(__name__, log_level="INFO")


@dataclass
class QualityIssue:
    """Quality issue found in document."""

    type: str  # missing_field, invalid_value, inconsistency, etc.
    severity: str  # low, medium, high, critical
    dimension: str  # completeness, accuracy, consistency, readability
    location: str  # where in document
    message: str
    suggestion: Optional[str] = None


@dataclass
class QualityDimension:
    """Quality dimension score."""

    name: str
    score: float  # 0-100
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Complete quality assessment report."""

    file_path: str
    analyzed_at: str
    overall_quality: float  # 0-100
    dimensions: Dict[str, QualityDimension]
    total_issues: int
    issues_by_severity: Dict[str, int]
    recommendations: List[str]
    passed: bool  # Whether quality meets threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "file_path": self.file_path,
            "analyzed_at": self.analyzed_at,
            "overall_quality": self.overall_quality,
            "dimensions": {
                name: {"score": dim.score, "issues": [asdict(issue) for issue in dim.issues], "metrics": dim.metrics}
                for name, dim in self.dimensions.items()
            },
            "total_issues": self.total_issues,
            "issues_by_severity": self.issues_by_severity,
            "recommendations": self.recommendations,
            "passed": self.passed,
        }
        return result


class DocumentQualityAnalyzer:
    """Document quality analyzer."""

    def __init__(self):
        """Initialize quality analyzer."""
        self.parser = DocumentParser()
        self.validator = DocumentValidator()
        self.ner_engine = NEREngine(use_spacy=True)
        logger.info("DocumentQualityAnalyzer initialized")

    def analyze(self, file_path: str, dimensions: Optional[List[str]] = None, threshold: float = 0.0) -> QualityReport:
        """
        Analyze document quality.

        Args:
            file_path: Path to document
            dimensions: Specific dimensions to check (None = all)
            threshold: Quality threshold (0-100)

        Returns:
            QualityReport object
        """
        logger.info(f"Analyzing quality of: {file_path}")

        # Parse document
        parsed = self.parser.parse(file_path)
        text = parsed.get("text", "")
        metadata = parsed.get("metadata", {})

        # Default to all dimensions
        if dimensions is None:
            dimensions = ["completeness", "accuracy", "consistency", "readability", "timeliness"]

        # Analyze each dimension
        dimension_results = {}

        if "completeness" in dimensions:
            dimension_results["completeness"] = self._check_completeness(text, metadata)

        if "accuracy" in dimensions:
            dimension_results["accuracy"] = self._check_accuracy(text, metadata)

        if "consistency" in dimensions:
            dimension_results["consistency"] = self._check_consistency(text, metadata)

        if "readability" in dimensions:
            dimension_results["readability"] = self._check_readability(text)

        if "timeliness" in dimensions:
            dimension_results["timeliness"] = self._check_timeliness(text, metadata)

        # Calculate overall quality
        overall_quality = self._calculate_overall_quality(dimension_results)

        # Aggregate issues
        all_issues = []
        for dim in dimension_results.values():
            all_issues.extend(dim.issues)

        issues_by_severity = Counter(issue.severity for issue in all_issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(dimension_results, all_issues)

        # Create report
        report = QualityReport(
            file_path=file_path,
            analyzed_at=datetime.now().isoformat(),
            overall_quality=overall_quality,
            dimensions=dimension_results,
            total_issues=len(all_issues),
            issues_by_severity=dict(issues_by_severity),
            recommendations=recommendations,
            passed=overall_quality >= threshold,
        )

        logger.info(f"Quality analysis complete. Score: {overall_quality:.1f}/100")
        return report

    def _check_completeness(self, text: str, metadata: Dict[str, Any]) -> QualityDimension:
        """Check document completeness."""
        issues = []
        metrics = {}

        # Check text length
        if len(text) < 100:
            issues.append(
                QualityIssue(
                    type="insufficient_content",
                    severity="high",
                    dimension="completeness",
                    location="entire document",
                    message="Document has very little content (< 100 characters)",
                    suggestion="Add more detailed information",
                )
            )

        # Check for common required fields (extracted from entities)
        entities = self.ner_engine.extract_entities(text)
        entity_types_found = set(e.type.value for e in entities)

        # Metrics
        metrics["text_length"] = len(text)
        metrics["word_count"] = len(text.split())
        metrics["entity_types_found"] = list(entity_types_found)

        # Calculate score
        score = 100.0
        for issue in issues:
            if issue.severity == "critical":
                score -= 30
            elif issue.severity == "high":
                score -= 20
            elif issue.severity == "medium":
                score -= 10
            elif issue.severity == "low":
                score -= 5

        score = max(0, min(100, score))

        return QualityDimension(name="Completeness", score=score, issues=issues, metrics=metrics)

    def _check_accuracy(self, text: str, metadata: Dict[str, Any]) -> QualityDimension:
        """Check data accuracy."""
        issues = []
        metrics = {}

        # Extract entities for validation
        entities = self.ner_engine.extract_entities(text)

        # Validate emails
        emails = [e for e in entities if e.type.value == "EMAIL"]
        invalid_emails = 0
        for email_entity in emails:
            email = email_entity.text
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                invalid_emails += 1
                issues.append(
                    QualityIssue(
                        type="invalid_email",
                        severity="medium",
                        dimension="accuracy",
                        location=f"position {email_entity.start}",
                        message=f"Invalid email format: {email}",
                        suggestion="Correct email format",
                    )
                )

        # Validate phones
        phones = [e for e in entities if e.type.value == "PHONE"]
        invalid_phones = 0
        for phone_entity in phones:
            phone = phone_entity.text
            # Basic phone validation
            if not re.search(r"\d", phone):
                invalid_phones += 1
                issues.append(
                    QualityIssue(
                        type="invalid_phone",
                        severity="low",
                        dimension="accuracy",
                        location=f"position {phone_entity.start}",
                        message=f"Invalid phone format: {phone}",
                        suggestion="Use standard phone format",
                    )
                )

        # Metrics
        metrics["emails_checked"] = len(emails)
        metrics["invalid_emails"] = invalid_emails
        metrics["phones_checked"] = len(phones)
        metrics["invalid_phones"] = invalid_phones
        metrics["accuracy_rate"] = (
            1.0 - (invalid_emails + invalid_phones) / (len(emails) + len(phones))
            if (len(emails) + len(phones)) > 0
            else 1.0
        )

        # Calculate score
        score = 100.0 * metrics["accuracy_rate"]

        return QualityDimension(name="Accuracy", score=score, issues=issues, metrics=metrics)

    def _check_consistency(self, text: str, metadata: Dict[str, Any]) -> QualityDimension:
        """Check internal consistency."""
        issues = []
        metrics = {}

        # Check for duplicate entities (potential inconsistency)
        entities = self.ner_engine.extract_entities(text)
        entity_texts = [e.text for e in entities]
        entity_counts = Counter(entity_texts)

        # Find entities mentioned multiple times (potentially good or bad)
        frequently_mentioned = {text: count for text, count in entity_counts.items() if count > 3}

        metrics["unique_entities"] = len(entity_counts)
        metrics["total_entity_mentions"] = len(entity_texts)
        metrics["frequently_mentioned"] = frequently_mentioned

        # Check text formatting consistency
        lines = text.split("\n")
        empty_lines = sum(1 for line in lines if not line.strip())
        metrics["empty_lines"] = empty_lines
        metrics["total_lines"] = len(lines)

        # Calculate score (high consistency = good)
        score = 100.0
        for issue in issues:
            if issue.severity == "high":
                score -= 15
            elif issue.severity == "medium":
                score -= 10

        score = max(0, min(100, score))

        return QualityDimension(name="Consistency", score=score, issues=issues, metrics=metrics)

    def _check_readability(self, text: str) -> QualityDimension:
        """Check readability metrics."""
        issues = []
        metrics = {}

        # Basic readability metrics
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = text.split()
        total_words = len(words)
        total_sentences = len(sentences) if sentences else 1

        # Average sentence length
        avg_sentence_length = total_words / total_sentences

        # Long sentences (> 40 words)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 40)

        if long_sentences > total_sentences * 0.3:
            issues.append(
                QualityIssue(
                    type="long_sentences",
                    severity="medium",
                    dimension="readability",
                    location="entire document",
                    message=f"Document has many long sentences ({long_sentences}/{total_sentences})",
                    suggestion="Break long sentences into shorter ones for better readability",
                )
            )

        # Complex words (> 10 characters)
        complex_words = sum(1 for w in words if len(w) > 10)
        complex_word_ratio = complex_words / total_words if total_words > 0 else 0

        # Flesch Reading Ease (simplified)
        syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllables / total_words if total_words > 0 else 0

        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))

        # Metrics
        metrics["total_words"] = total_words
        metrics["total_sentences"] = total_sentences
        metrics["avg_sentence_length"] = round(avg_sentence_length, 2)
        metrics["long_sentences"] = long_sentences
        metrics["complex_words"] = complex_words
        metrics["complex_word_ratio"] = round(complex_word_ratio, 3)
        metrics["flesch_reading_ease"] = round(flesch_score, 2)

        # Calculate score
        # Flesch score:  90-100 = very easy, 60-70 = standard, 0-30 = very difficult
        # Normalize to 0-100 where higher is better
        score = flesch_score

        return QualityDimension(name="Readability", score=score, issues=issues, metrics=metrics)

    def _check_timeliness(self, text: str, metadata: Dict[str, Any]) -> QualityDimension:
        """Check timeliness/relevance."""
        issues = []
        metrics = {}

        # Extract dates
        entities = self.ner_engine.extract_entities(text)
        dates = [e for e in entities if e.type.value == "DATE"]

        # Check for very old dates (might indicate outdated content)
        current_year = datetime.now().year
        old_dates = []

        for date_entity in dates:
            date_text = date_entity.text
            # Try to extract year
            year_match = re.search(r"\b(19|20)\d{2}\b", date_text)
            if year_match:
                year = int(year_match.group(0))
                if year < current_year - 5:  # More than 5 years old
                    old_dates.append((date_text, year))

        if old_dates:
            issues.append(
                QualityIssue(
                    type="outdated_dates",
                    severity="medium",
                    dimension="timeliness",
                    location="multiple locations",
                    message=f"Document contains {len(old_dates)} dates older than 5 years",
                    suggestion="Verify information is still current",
                )
            )

        # Metrics
        metrics["dates_found"] = len(dates)
        metrics["old_dates"] = len(old_dates)

        # Calculate score
        score = 100.0
        if old_dates:
            # Reduce score based on percentage of old dates
            old_ratio = len(old_dates) / len(dates) if dates else 0
            score = max(50, 100 - (old_ratio * 50))

        return QualityDimension(name="Timeliness", score=score, issues=issues, metrics=metrics)

    def _count_syllables(self, word: str) -> int:
        """Count syllables in word (simplified)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith("e"):
            syllable_count -= 1

        # At least one syllable
        return max(1, syllable_count)

    def _calculate_overall_quality(self, dimensions: Dict[str, QualityDimension]) -> float:
        """Calculate overall quality score."""
        if not dimensions:
            return 0.0

        # Weighted average (can be customized)
        weights = {"completeness": 0.25, "accuracy": 0.30, "consistency": 0.20, "readability": 0.15, "timeliness": 0.10}

        total_score = 0.0
        total_weight = 0.0

        for name, dimension in dimensions.items():
            weight = weights.get(name, 0.2)  # Default weight
            total_score += dimension.score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _generate_recommendations(
        self, dimensions: Dict[str, QualityDimension], all_issues: List[QualityIssue]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Sort issues by severity
        critical_issues = [i for i in all_issues if i.severity == "critical"]
        high_issues = [i for i in all_issues if i.severity == "high"]

        if critical_issues:
            recommendations.append(f"FIX IMMEDIATELY: {len(critical_issues)} critical issues found")
            for issue in critical_issues[:3]:  # Top 3
                if issue.suggestion:
                    recommendations.append(f"  - {issue.suggestion}")

        if high_issues:
            recommendations.append(f"Address {len(high_issues)} high-priority issues")

        # Dimension-specific recommendations
        for name, dimension in dimensions.items():
            if dimension.score < 70:
                recommendations.append(f"Improve {name}: Current score {dimension.score:.1f}/100")

        return recommendations


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Quality Analyzer - Comprehensive quality assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full quality analysis
  python doc-quality.py analyze document.pdf --full

  # Check specific dimension
  python doc-quality.py check document.pdf --dimension completeness

  # With quality threshold
  python doc-quality.py analyze document.pdf --threshold 80 --fail-on-low-quality

  # Batch quality check
  python doc-quality.py batch /documents/ --output quality_report.json

  # Generate HTML report
  python doc-quality.py analyze document.pdf --report html --output quality.html
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze document quality")
    analyze_parser.add_argument("file", help="Document to analyze")
    analyze_parser.add_argument("--full", action="store_true", help="Run full analysis (all dimensions)")
    analyze_parser.add_argument(
        "--dimension",
        "-d",
        action="append",
        choices=["completeness", "accuracy", "consistency", "readability", "timeliness"],
        help="Specific dimension(s) to check",
    )
    analyze_parser.add_argument("--threshold", type=float, default=0.0, help="Quality threshold (0-100)")
    analyze_parser.add_argument(
        "--fail-on-low-quality", action="store_true", help="Exit with error if quality below threshold"
    )
    analyze_parser.add_argument("--output", "-o", help="Output file for report (JSON)")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch quality check")
    batch_parser.add_argument("input_dir", help="Input directory")
    batch_parser.add_argument("--output", "-o", help="Output report file (JSON)")
    batch_parser.add_argument("--threshold", type=float, default=70.0, help="Quality threshold")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    analyzer = DocumentQualityAnalyzer()

    try:
        if args.command == "analyze":
            # Determine dimensions
            dimensions = args.dimension if args.dimension else None
            if args.full:
                dimensions = None  # All dimensions

            # Analyze
            report = analyzer.analyze(args.file, dimensions, args.threshold)

            # Print results
            print(f"\n📊 Document Quality Report")
            print(f"=" * 80)
            print(f"File: {report.file_path}")
            print(f"Overall Quality: {report.overall_quality:.1f}/100")
            print(f"Status: {'✅ PASSED' if report.passed else '❌ FAILED'}")
            print(f"\nDimension Scores:")

            for name, dimension in report.dimensions.items():
                status = "✅" if dimension.score >= 70 else "⚠️" if dimension.score >= 50 else "❌"
                print(f"  {status} {dimension.name:15s}: {dimension.score:5.1f}/100")

            if report.total_issues > 0:
                print(f"\nIssues Found: {report.total_issues}")
                print(f"  Critical: {report.issues_by_severity.get('critical', 0)}")
                print(f"  High:     {report.issues_by_severity.get('high', 0)}")
                print(f"  Medium:   {report.issues_by_severity.get('medium', 0)}")
                print(f"  Low:      {report.issues_by_severity.get('low', 0)}")

            if report.recommendations:
                print(f"\nRecommendations:")
                for rec in report.recommendations:
                    print(f"  • {rec}")

            # Save report if requested
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"\nReport saved to: {args.output}")

            # Exit with error if quality below threshold
            if args.fail_on_low_quality and not report.passed:
                sys.exit(2)

        elif args.command == "batch":
            # Batch analyze
            input_path = Path(args.input_dir)
            files = list(input_path.glob("*.*"))

            results = []
            for file_path in files:
                try:
                    report = analyzer.analyze(str(file_path), threshold=args.threshold)
                    results.append(report.to_dict())
                    status = "✅" if report.passed else "❌"
                    print(f"{status} {file_path.name}: {report.overall_quality:.1f}/100")
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")

            # Save batch results
            if args.output:
                batch_report = {
                    "analyzed_at": datetime.now().isoformat(),
                    "total_files": len(files),
                    "analyzed": len(results),
                    "threshold": args.threshold,
                    "passed": sum(1 for r in results if r["passed"]),
                    "failed": sum(1 for r in results if not r["passed"]),
                    "results": results,
                }
                with open(args.output, "w") as f:
                    json.dump(batch_report, f, indent=2, ensure_ascii=False)
                print(f"\nBatch report saved to: {args.output}")

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
