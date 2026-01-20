#!/usr/bin/env python3
"""
Semantic Search Module (Pure Python - Simplified)

Mock semantic search without numpy/transformers dependencies.
"""

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class SearchResult:
    """Search result"""
    document_id: str
    score: float
    text: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Document:
    """Document for indexing"""
    doc_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

class SemanticSearchEngine:
    """Semantic search engine (Pure Python - Mock)"""
    
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
        self.documents: Dict[str, Document] = {}
    
    def _mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding"""
        h = hashlib.md5(text.encode()).hexdigest()
        random.seed(int(h, 16))
        embedding = [random.gauss(0, 1) for _ in range(128)]
        random.seed()
        return embedding
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity (simplified)"""
        import math
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)
    
    def index_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        """Index document (mock)"""
        embedding = self._mock_embedding(text)
        doc = Document(
            doc_id=doc_id,
            text=text,
            embedding=embedding,
            metadata=metadata
        )
        self.documents[doc_id] = doc
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Semantic search (mock)"""
        query_embedding = self._mock_embedding(query)
        
        results = []
        for doc_id, doc in self.documents.items():
            if doc.embedding:
                score = self._cosine_similarity(query_embedding, doc.embedding)
                results.append(SearchResult(
                    document_id=doc_id,
                    score=score,
                    text=doc.text,
                    metadata=doc.metadata
                ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def clear_index(self):
        """Clear all documents"""
        self.documents.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "num_documents": len(self.documents),
            "model": self.model_name
        }

def get_semantic_search_engine(model: str = "mock-model") -> SemanticSearchEngine:
    """Get semantic search engine singleton"""
    return SemanticSearchEngine(model_name=model)
