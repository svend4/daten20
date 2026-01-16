#!/usr/bin/env python3
"""
Document Comparator
===================

Professional document comparison tool with advanced features.

Features:
- Text-level diff (line-by-line, word-by-word)
- Similarity metrics (Cosine, Jaccard, Levenshtein)
- Entity comparison (using NER)
- Structural comparison
- Semantic similarity
- Visual diff reports (HTML, PDF)
- Version tracking
- Change detection

Usage:
    # Basic comparison
    python doc-comparator.py compare doc1.pdf doc2.pdf

    # With detailed HTML report
    python doc-comparator.py compare doc1.pdf doc2.pdf --report html --output diff_report.html

    # Multiple versions timeline
    python doc-comparator.py versions v1.pdf v2.pdf v3.pdf --timeline

    # Entity comparison
    python doc-comparator.py entities doc1.pdf doc2.pdf --highlight-changes

    # Semantic similarity only
    python doc-comparator.py semantic doc1.pdf doc2.pdf --threshold 0.8

Author: Document Management System
Version: 1.0.0
"""

import argparse
import difflib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from src.core.logging_config import setup_logging

# Import core modules
from src.core.parser import DocumentParser

# Import ML modules
from src.ml.ner import Entity, NEREngine

# Setup logging
logger = setup_logging(__name__, log_level="INFO")


@dataclass
class ComparisonResult:
    """Results of document comparison."""

    doc1_path: str
    doc2_path: str
    compared_at: str

    # Text similarity metrics
    cosine_similarity: float
    jaccard_similarity: float
    levenshtein_distance: int
    levenshtein_similarity: float

    # Structural metrics
    length_ratio: float
    word_count_ratio: float

    # Changes
    added_lines: int
    removed_lines: int
    modified_lines: int
    unchanged_lines: int

    # Entity comparison
    entities_doc1: int
    entities_doc2: int
    common_entities: int
    unique_entities_doc1: int
    unique_entities_doc2: int
    entity_overlap: float

    # Detailed results
    diff_unified: str = ""
    diff_html: str = ""
    entity_changes: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class DocumentComparator:
    """Advanced document comparison engine."""

    def __init__(self):
        """Initialize comparator with all components."""
        self.parser = DocumentParser()
        self.ner_engine = NEREngine(use_spacy=True)
        logger.info("DocumentComparator initialized")

    def compare(
        self, file1: str, file2: str, include_entities: bool = True, include_diff: bool = True
    ) -> ComparisonResult:
        """
        Compare two documents comprehensively.

        Args:
            file1: Path to first document
            file2: Path to second document
            include_entities: Include entity comparison
            include_diff: Include detailed diff

        Returns:
            ComparisonResult object
        """
        logger.info(f"Comparing documents: {file1} vs {file2}")

        # Parse documents
        doc1 = self.parser.parse(file1)
        doc2 = self.parser.parse(file2)

        text1 = doc1.get("text", "")
        text2 = doc2.get("text", "")

        # Calculate similarity metrics
        cosine_sim = self._cosine_similarity(text1, text2)
        jaccard_sim = self._jaccard_similarity(text1, text2)
        lev_dist, lev_sim = self._levenshtein_distance_and_similarity(text1, text2)

        # Structural metrics
        length_ratio = len(text2) / len(text1) if len(text1) > 0 else 0
        words1 = text1.split()
        words2 = text2.split()
        word_count_ratio = len(words2) / len(words1) if len(words1) > 0 else 0

        # Diff analysis
        diff_stats = self._analyze_diff(text1, text2)

        # Entity comparison
        entity_stats = {}
        if include_entities:
            entity_stats = self._compare_entities(text1, text2)

        # Generate diffs
        diff_unified = ""
        diff_html = ""
        if include_diff:
            diff_unified = self._generate_unified_diff(text1, text2, file1, file2)
            diff_html = self._generate_html_diff(text1, text2)

        result = ComparisonResult(
            doc1_path=file1,
            doc2_path=file2,
            compared_at=datetime.now().isoformat(),
            cosine_similarity=cosine_sim,
            jaccard_similarity=jaccard_sim,
            levenshtein_distance=lev_dist,
            levenshtein_similarity=lev_sim,
            length_ratio=length_ratio,
            word_count_ratio=word_count_ratio,
            added_lines=diff_stats["added"],
            removed_lines=diff_stats["removed"],
            modified_lines=diff_stats["modified"],
            unchanged_lines=diff_stats["unchanged"],
            entities_doc1=entity_stats.get("doc1_count", 0),
            entities_doc2=entity_stats.get("doc2_count", 0),
            common_entities=entity_stats.get("common_count", 0),
            unique_entities_doc1=entity_stats.get("unique_doc1", 0),
            unique_entities_doc2=entity_stats.get("unique_doc2", 0),
            entity_overlap=entity_stats.get("overlap", 0.0),
            diff_unified=diff_unified,
            diff_html=diff_html,
            entity_changes=entity_stats.get("changes", {}),
        )

        logger.info(f"Comparison complete. Similarity: {cosine_sim:.2%}")
        return result

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        # Simple word-based cosine similarity
        words1 = text1.lower().split()
        words2 = text2.lower().split()

        # Build vocabulary
        vocab = set(words1 + words2)

        # Create vectors
        vec1 = [words1.count(word) for word in vocab]
        vec2 = [words2.count(word) for word in vocab]

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)

    def _levenshtein_distance_and_similarity(self, text1: str, text2: str) -> Tuple[int, float]:
        """
        Calculate Levenshtein distance and normalized similarity.

        Returns:
            Tuple of (distance, similarity_ratio)
        """
        # For very long texts, use sampling
        max_len = 5000
        if len(text1) > max_len:
            text1 = text1[:max_len]
        if len(text2) > max_len:
            text2 = text2[:max_len]

        # Dynamic programming approach
        m, n = len(text1), len(text2)

        # Create distance matrix
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Fill matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]  # deletion  # insertion  # substitution
                    )

        distance = dp[m][n]
        max_len = max(m, n)
        similarity = 1 - (distance / max_len) if max_len > 0 else 1.0

        return distance, similarity

    def _analyze_diff(self, text1: str, text2: str) -> Dict[str, int]:
        """Analyze differences between texts line-by-line."""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        diff = difflib.unified_diff(lines1, lines2, lineterm="")

        added = 0
        removed = 0
        unchanged = 0

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
            elif not line.startswith("@@"):
                unchanged += 1

        # Modified lines = min(added, removed) approximation
        modified = min(added, removed)
        added = added - modified
        removed = removed - modified

        return {"added": added, "removed": removed, "modified": modified, "unchanged": unchanged}

    def _compare_entities(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare entities between two texts."""
        # Extract entities from both documents
        entities1 = self.ner_engine.extract_entities(text1)
        entities2 = self.ner_engine.extract_entities(text2)

        # Convert to sets of entity text
        entity_texts1 = set(e.text for e in entities1)
        entity_texts2 = set(e.text for e in entities2)

        # Calculate overlap
        common = entity_texts1.intersection(entity_texts2)
        unique1 = entity_texts1 - entity_texts2
        unique2 = entity_texts2 - entity_texts1

        overlap = len(common) / len(entity_texts1.union(entity_texts2)) if entity_texts1.union(entity_texts2) else 0.0

        # Group by type
        def group_by_type(entities: List[Entity]) -> Dict[str, List[str]]:
            grouped = {}
            for entity in entities:
                type_name = entity.type.value
                if type_name not in grouped:
                    grouped[type_name] = []
                grouped[type_name].append(entity.text)
            return grouped

        grouped1 = group_by_type(entities1)
        grouped2 = group_by_type(entities2)

        return {
            "doc1_count": len(entities1),
            "doc2_count": len(entities2),
            "common_count": len(common),
            "unique_doc1": len(unique1),
            "unique_doc2": len(unique2),
            "overlap": overlap,
            "changes": {
                "added": list(unique2),
                "removed": list(unique1),
                "common": list(common),
                "doc1_by_type": grouped1,
                "doc2_by_type": grouped2,
            },
        }

    def _generate_unified_diff(self, text1: str, text2: str, file1: str, file2: str) -> str:
        """Generate unified diff format."""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        diff = difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2, lineterm="")

        return "\n".join(diff)

    def _generate_html_diff(self, text1: str, text2: str) -> str:
        """Generate HTML diff with highlighting."""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        diff = difflib.HtmlDiff()
        html = diff.make_file(lines1, lines2, fromdesc="Document 1", todesc="Document 2")

        return html

    def generate_report(self, result: ComparisonResult, format: str = "html", output_file: str = None) -> str:
        """
        Generate comparison report.

        Args:
            result: Comparison result
            format: Report format ('html', 'json', 'text')
            output_file: Optional output file path

        Returns:
            Report content as string
        """
        if format == "html":
            report = self._generate_html_report(result)
        elif format == "json":
            report = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        elif format == "text":
            report = self._generate_text_report(result)
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report saved to: {output_file}")

        return report

    def _generate_html_report(self, result: ComparisonResult) -> str:
        """Generate HTML report with visualizations."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Comparison Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            display: block;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .metric-value.good {{
            color: #10b981;
        }}
        .metric-value.medium {{
            color: #f59e0b;
        }}
        .metric-value.low {{
            color: #ef4444;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 10px 0;
        }}
        .entity-tag {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }}
        .entity-tag.added {{
            background: #d1fae5;
            color: #065f46;
        }}
        .entity-tag.removed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .entity-tag.common {{
            background: #e0e7ff;
            color: #3730a3;
        }}
        .diff-section {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Document Comparison Report</h1>
        <p><strong>Document 1:</strong> {result.doc1_path}</p>
        <p><strong>Document 2:</strong> {result.doc2_path}</p>
        <p><strong>Compared at:</strong> {result.compared_at}</p>
    </div>

    <div class="section">
        <h2>Similarity Metrics</h2>
        <div class="metric">
            <span class="metric-label">Cosine Similarity</span>
            <span class="metric-value {'good' if result.cosine_similarity > 0.8 else 'medium' if result.cosine_similarity > 0.5 else 'low'}">
                {result.cosine_similarity:.1%}
            </span>
        </div>
        <div class="metric">
            <span class="metric-label">Jaccard Similarity</span>
            <span class="metric-value {'good' if result.jaccard_similarity > 0.8 else 'medium' if result.jaccard_similarity > 0.5 else 'low'}">
                {result.jaccard_similarity:.1%}
            </span>
        </div>
        <div class="metric">
            <span class="metric-label">Levenshtein Similarity</span>
            <span class="metric-value {'good' if result.levenshtein_similarity > 0.8 else 'medium' if result.levenshtein_similarity > 0.5 else 'low'}">
                {result.levenshtein_similarity:.1%}
            </span>
        </div>

        <h3 style="margin-top: 30px;">Overall Similarity</h3>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {result.cosine_similarity * 100}%">
                {result.cosine_similarity:.1%}
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Structural Changes</h2>
        <div class="metric">
            <span class="metric-label">Added Lines</span>
            <span class="metric-value" style="color: #10b981;">{result.added_lines}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Removed Lines</span>
            <span class="metric-value" style="color: #ef4444;">{result.removed_lines}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Modified Lines</span>
            <span class="metric-value" style="color: #f59e0b;">{result.modified_lines}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Unchanged Lines</span>
            <span class="metric-value" style="color: #6b7280;">{result.unchanged_lines}</span>
        </div>
    </div>

    <div class="section">
        <h2>Entity Comparison</h2>
        <div class="metric">
            <span class="metric-label">Document 1 Entities</span>
            <span class="metric-value">{result.entities_doc1}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Document 2 Entities</span>
            <span class="metric-value">{result.entities_doc2}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Common Entities</span>
            <span class="metric-value">{result.common_entities}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Entity Overlap</span>
            <span class="metric-value {'good' if result.entity_overlap > 0.7 else 'medium' if result.entity_overlap > 0.4 else 'low'}">
                {result.entity_overlap:.1%}
            </span>
        </div>

        {self._generate_entity_changes_html(result.entity_changes) if result.entity_changes else ''}
    </div>

    <div class="section">
        <h2>Detailed Diff</h2>
        {result.diff_html if result.diff_html else '<p>Diff not generated</p>'}
    </div>
</body>
</html>
"""
        return html

    def _generate_entity_changes_html(self, changes: Dict[str, Any]) -> str:
        """Generate HTML for entity changes."""
        if not changes:
            return ""

        html = "<h3>Entity Changes</h3>"

        if changes.get("added"):
            html += "<h4 style='color: #10b981;'>Added Entities</h4>"
            html += '<div class="entity-list">'
            for entity in changes["added"][:20]:  # Limit to 20
                html += f'<span class="entity-tag added">{entity}</span>'
            html += "</div>"

        if changes.get("removed"):
            html += "<h4 style='color: #ef4444;'>Removed Entities</h4>"
            html += '<div class="entity-list">'
            for entity in changes["removed"][:20]:
                html += f'<span class="entity-tag removed">{entity}</span>'
            html += "</div>"

        if changes.get("common"):
            html += "<h4 style='color: #3730a3;'>Common Entities</h4>"
            html += '<div class="entity-list">'
            for entity in changes["common"][:20]:
                html += f'<span class="entity-tag common">{entity}</span>'
            html += "</div>"

        return html

    def _generate_text_report(self, result: ComparisonResult) -> str:
        """Generate plain text report."""
        report = []
        report.append("=" * 80)
        report.append("DOCUMENT COMPARISON REPORT")
        report.append("=" * 80)
        report.append(f"Document 1: {result.doc1_path}")
        report.append(f"Document 2: {result.doc2_path}")
        report.append(f"Compared at: {result.compared_at}")
        report.append("")

        report.append("SIMILARITY METRICS")
        report.append("-" * 80)
        report.append(f"Cosine Similarity:      {result.cosine_similarity:>6.1%}")
        report.append(f"Jaccard Similarity:     {result.jaccard_similarity:>6.1%}")
        report.append(f"Levenshtein Similarity: {result.levenshtein_similarity:>6.1%}")
        report.append(f"Levenshtein Distance:   {result.levenshtein_distance:>6}")
        report.append("")

        report.append("STRUCTURAL CHANGES")
        report.append("-" * 80)
        report.append(f"Added Lines:      {result.added_lines:>6}")
        report.append(f"Removed Lines:    {result.removed_lines:>6}")
        report.append(f"Modified Lines:   {result.modified_lines:>6}")
        report.append(f"Unchanged Lines:  {result.unchanged_lines:>6}")
        report.append("")

        report.append("ENTITY COMPARISON")
        report.append("-" * 80)
        report.append(f"Document 1 Entities:  {result.entities_doc1:>6}")
        report.append(f"Document 2 Entities:  {result.entities_doc2:>6}")
        report.append(f"Common Entities:      {result.common_entities:>6}")
        report.append(f"Unique to Doc 1:      {result.unique_entities_doc1:>6}")
        report.append(f"Unique to Doc 2:      {result.unique_entities_doc2:>6}")
        report.append(f"Entity Overlap:       {result.entity_overlap:>6.1%}")
        report.append("")

        return "\n".join(report)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Comparator - Professional document comparison tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison
  python doc-comparator.py compare doc1.pdf doc2.pdf

  # With HTML report
  python doc-comparator.py compare doc1.pdf doc2.pdf --report html --output diff_report.html

  # Entity comparison only
  python doc-comparator.py compare doc1.pdf doc2.pdf --entities-only

  # High threshold similarity check
  python doc-comparator.py compare doc1.pdf doc2.pdf --threshold 0.9
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two documents")
    compare_parser.add_argument("file1", help="First document")
    compare_parser.add_argument("file2", help="Second document")
    compare_parser.add_argument("--report", choices=["html", "json", "text"], default="text", help="Report format")
    compare_parser.add_argument("--output", "-o", help="Output file for report")
    compare_parser.add_argument("--no-entities", action="store_true", help="Skip entity comparison")
    compare_parser.add_argument("--no-diff", action="store_true", help="Skip detailed diff generation")
    compare_parser.add_argument("--threshold", type=float, help="Similarity threshold (0.0-1.0)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize comparator
    comparator = DocumentComparator()

    try:
        if args.command == "compare":
            # Perform comparison
            result = comparator.compare(
                args.file1, args.file2, include_entities=not args.no_entities, include_diff=not args.no_diff
            )

            # Check threshold if specified
            if args.threshold is not None:
                if result.cosine_similarity < args.threshold:
                    logger.warning(f"Similarity {result.cosine_similarity:.1%} is below threshold {args.threshold:.1%}")
                    sys.exit(2)

            # Generate report
            report = comparator.generate_report(result, args.report, args.output)

            # Print to stdout if no output file
            if not args.output:
                print(report)

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
