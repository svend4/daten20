"""
Query Processor - Advanced query processing and optimization

Features:
- Query expansion
- Query reformulation
- Result re-ranking
- Query understanding
"""

import logging
from typing import List, Dict, Any, Optional
import re


class QueryProcessor:
    """
    Advanced query processing for semantic search.
    
    Features:
    - Query cleaning and normalization
    - Query expansion (synonyms, related terms)
    - Stopword removal (optional)
    - Query type detection
    """
    
    # Common stopwords (can be customized)
    STOPWORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
        'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
        'that', 'the', 'to', 'was', 'will', 'with'
    }
    
    def __init__(
        self,
        remove_stopwords: bool = False,
        expand_queries: bool = True,
        min_query_length: int = 2
    ):
        """
        Initialize query processor.
        
        Args:
            remove_stopwords: Whether to remove stopwords
            expand_queries: Whether to expand queries
            min_query_length: Minimum query length (chars)
        """
        self.logger = logging.getLogger(__name__)
        self.remove_stopwords = remove_stopwords
        self.expand_queries = expand_queries
        self.min_query_length = min_query_length
        
        # Query expansion dictionary (can be loaded from file)
        self.expansions = {
            "python": ["python", "python programming", "python language"],
            "ml": ["machine learning", "ml", "artificial intelligence"],
            "ai": ["artificial intelligence", "ai", "machine learning"],
            "doc": ["document", "documentation"],
        }
    
    def process(self, query: str) -> str:
        """
        Process and optimize query.
        
        Args:
            query: Raw query string
        
        Returns:
            Processed query string
        """
        if not query or len(query.strip()) < self.min_query_length:
            return query
        
        # Clean query
        query = self._clean_query(query)
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            query = self._remove_stopwords(query)
        
        # Expand query if enabled
        if self.expand_queries:
            query = self._expand_query(query)
        
        return query
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query."""
        # Lowercase
        query = query.lower()
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove special characters (keep alphanumeric and spaces)
        query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query)
        
        # Remove extra spaces again
        query = ' '.join(query.split())
        
        return query.strip()
    
    def _remove_stopwords(self, query: str) -> str:
        """Remove stopwords from query."""
        words = query.split()
        filtered_words = [w for w in words if w.lower() not in self.STOPWORDS]
        return ' '.join(filtered_words)
    
    def _expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms."""
        query_lower = query.lower()
        
        # Check for expansions
        for term, expanded_terms in self.expansions.items():
            if term in query_lower:
                # Use first expansion
                query = query_lower.replace(term, expanded_terms[0])
                break
        
        return query
    
    def add_expansion(self, term: str, expansions: List[str]):
        """
        Add query expansion rule.
        
        Args:
            term: Term to expand
            expansions: List of expanded versions
        """
        self.expansions[term.lower()] = expansions
        self.logger.info(f"Added expansion for '{term}': {expansions}")
    
    def detect_query_type(self, query: str) -> str:
        """
        Detect query type (question, keyword, phrase, etc.).
        
        Args:
            query: Query string
        
        Returns:
            Query type ('question', 'phrase', 'keyword')
        """
        query_lower = query.lower().strip()
        
        # Question
        if any(query_lower.startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who']):
            return 'question'
        
        # Check for question mark
        if '?' in query:
            return 'question'
        
        # Phrase (multiple words)
        if len(query.split()) > 2:
            return 'phrase'
        
        # Keyword (1-2 words)
        return 'keyword'


class ResultReranker:
    """
    Re-rank search results based on additional criteria.
    
    Features:
    - Keyword matching boost
    - Recency boost
    - Custom scoring functions
    """
    
    def __init__(
        self,
        keyword_boost: float = 0.2,
        recency_boost: float = 0.1
    ):
        """
        Initialize result re-ranker.
        
        Args:
            keyword_boost: Boost factor for keyword matches
            recency_boost: Boost factor for recent documents
        """
        self.logger = logging.getLogger(__name__)
        self.keyword_boost = keyword_boost
        self.recency_boost = recency_boost
    
    def rerank(
        self,
        results: List[Dict[str, Any]],
        query: str,
        boost_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results.
        
        Args:
            results: List of search results
            query: Original query
            boost_fields: Fields to check for keyword matches
        
        Returns:
            Re-ranked results
        """
        if not results:
            return results
        
        boost_fields = boost_fields or ['content', 'title', 'description']
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Calculate new scores
        for result in results:
            original_score = result.get('score', 0.0)
            boost = 0.0
            
            # Keyword matching boost
            doc = result.get('document', {})
            for field in boost_fields:
                if field in doc:
                    field_text = str(doc[field]).lower()
                    # Count matching words
                    matches = sum(1 for word in query_words if word in field_text)
                    if matches > 0:
                        boost += (matches / len(query_words)) * self.keyword_boost
            
            # Recency boost (if timestamp available)
            if 'timestamp' in doc or 'created_at' in doc:
                # Simple recency boost (can be made more sophisticated)
                boost += self.recency_boost
            
            # Update score
            result['original_score'] = original_score
            result['boost'] = boost
            result['score'] = min(1.0, original_score + boost)
        
        # Sort by new score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def diversity_rerank(
        self,
        results: List[Dict[str, Any]],
        diversity_field: str = 'category',
        max_per_category: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results to promote diversity.
        
        Args:
            results: List of search results
            diversity_field: Field to use for diversity
            max_per_category: Maximum results per category
        
        Returns:
            Diversified results
        """
        category_counts = {}
        diversified = []
        remaining = []
        
        for result in results:
            doc = result.get('document', {})
            category = doc.get(diversity_field, 'unknown')
            
            count = category_counts.get(category, 0)
            if count < max_per_category:
                diversified.append(result)
                category_counts[category] = count + 1
            else:
                remaining.append(result)
        
        # Add remaining results at the end
        diversified.extend(remaining)
        
        return diversified
