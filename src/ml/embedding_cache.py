#!/usr/bin/env python3
"""
Embedding Cache Module (Pure Python - Simplified)

Mock embedding cache without numpy/redis dependencies.
"""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    size: int = 0
    evictions: int = 0

class EmbeddingCache:
    """Embedding cache (Pure Python - Mock)"""
    
    def __init__(self, max_size: int = 10000, ttl: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.stats = CacheStats()
        self.timestamps: Dict[str, float] = {}
    
    def _make_key(self, text: str) -> str:
        """Make cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache (mock)"""
        key = self._make_key(text)
        
        if key in self.cache:
            # Check TTL
            if self.ttl and time.time() - self.timestamps.get(key, 0) > self.ttl:
                del self.cache[key]
                self.stats.misses += 1
                return None
            
            self.stats.hits += 1
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return self.cache[key]
        
        self.stats.misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]):
        """Set embedding in cache (mock)"""
        key = self._make_key(text)
        
        # Evict if needed
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
            self.stats.evictions += 1
        
        self.cache[key] = embedding
        self.timestamps[key] = time.time()
        self.stats.size = len(self.cache)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        self.stats.size = len(self.cache)
        return self.stats

def get_embedding_cache(max_size: int = 10000) -> EmbeddingCache:
    """Get embedding cache singleton"""
    return EmbeddingCache(max_size=max_size)
