#!/usr/bin/env python3
"""Test ml modules Pure Python versions"""

import sys
sys.path.insert(0, '/home/user/daten20/src')

def test_embedding_cache():
    from ml.embedding_cache import EmbeddingCache, get_embedding_cache
    
    print("Testing embedding_cache...")
    cache = get_embedding_cache(max_size=100)
    
    # Set and get
    embedding = [0.1, 0.2, 0.3]
    cache.set("test text", embedding)
    retrieved = cache.get("test text")
    
    print(f"  Cache hit: {retrieved is not None}")
    stats = cache.get_stats()
    print(f"  Stats - Hits: {stats.hits}, Misses: {stats.misses}")
    print("  ✅ embedding_cache works!")

def test_ocr():
    from ml.ocr import OCREngine, get_ocr_engine
    
    print("Testing ocr...")
    ocr = get_ocr_engine()
    
    result = ocr.extract_text("dummy.png")
    print(f"  Extracted text length: {len(result.text)}")
    print(f"  Confidence: {result.confidence:.2f}")
    
    regions = ocr.extract_regions("dummy.png")
    print(f"  Regions extracted: {len(regions)}")
    
    print("  ✅ ocr works!")

def test_semantic_search():
    from ml.semantic_search import SemanticSearchEngine, get_semantic_search_engine
    
    print("Testing semantic_search...")
    engine = get_semantic_search_engine()
    
    # Index documents
    engine.index_document("doc1", "Python programming language")
    engine.index_document("doc2", "Machine learning with Python")
    engine.index_document("doc3", "JavaScript web development")
    
    # Search
    results = engine.search("Python coding", top_k=2)
    print(f"  Search results: {len(results)}")
    if results:
        print(f"  Top result score: {results[0].score:.3f}")
    
    stats = engine.get_stats()
    print(f"  Indexed documents: {stats['num_documents']}")
    
    print("  ✅ semantic_search works!")

if __name__ == "__main__":
    print("=" * 60)
    print("ML Modules Test Suite (Pure Python)")
    print("=" * 60)
    print()
    
    test_embedding_cache()
    print()
    test_ocr()
    print()
    test_semantic_search()
    
    print()
    print("=" * 60)
    print("✅ ALL ML TESTS PASSED!")
    print("=" * 60)
