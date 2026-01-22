#!/usr/bin/env python3
"""
BERT Semantic Search - Practical Examples

This file demonstrates various use cases for the BERT Semantic Search module.

Examples covered:
1. Basic document indexing and search
2. Multi-lingual search
3. Advanced filtering with metadata
4. Query expansion and re-ranking
5. Batch processing
6. Performance optimization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search import SemanticSearch, QueryProcessor, BERTEmbedder
from typing import List, Dict, Any


# ============================================================================
# Example 1: Basic Document Indexing and Search
# ============================================================================

def example_basic_search():
    """
    Basic semantic search example - index documents and search.
    """
    print("=" * 80)
    print("Example 1: Basic Document Indexing and Search")
    print("=" * 80)

    # Initialize search engine
    search = SemanticSearch(
        model_name="fast",          # Use fast model for quick results
        store_type="chroma",        # Persistent storage
        persist_directory="./demo_db"
    )

    # Sample documents
    documents = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability.",
            "title": "Introduction to Python",
            "category": "programming"
        },
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
            "title": "ML Basics",
            "category": "AI"
        },
        {
            "content": "Data science combines statistics, programming, and domain expertise to extract insights from data.",
            "title": "Data Science Overview",
            "category": "data"
        },
        {
            "content": "JavaScript is the programming language of the web, used for frontend and backend development.",
            "title": "JavaScript Guide",
            "category": "programming"
        },
        {
            "content": "Deep learning uses neural networks with multiple layers to model complex patterns in data.",
            "title": "Deep Learning Intro",
            "category": "AI"
        }
    ]

    # Index documents
    print(f"\n📝 Indexing {len(documents)} documents...")
    doc_ids = search.add_documents(documents)
    print(f"✓ Indexed {len(doc_ids)} documents")
    print(f"Total documents in index: {search.count_documents()}")

    # Search
    query = "learn artificial intelligence"
    print(f"\n🔍 Searching for: '{query}'")

    results = search.search(query, top_k=3)

    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        doc = result['document']
        score = result.get('score', 0.0)
        print(f"{i}. Score: {score:.3f}")
        print(f"   Title: {doc.get('title', 'N/A')}")
        print(f"   Category: {doc.get('category', 'N/A')}")
        print(f"   Content: {doc['content'][:80]}...")
        print()

    # Clean up
    search.clear_index()
    print("✓ Index cleared\n")


# ============================================================================
# Example 2: Multi-lingual Search
# ============================================================================

def example_multilingual_search():
    """
    Multi-lingual semantic search - search across different languages.
    """
    print("=" * 80)
    print("Example 2: Multi-lingual Search")
    print("=" * 80)

    # Initialize with multilingual model
    search = SemanticSearch(
        model_name="multilingual",
        store_type="chroma",
        persist_directory="./demo_multilingual_db"
    )

    # Documents in different languages
    documents = [
        {"content": "Python programming tutorial for beginners", "lang": "en"},
        {"content": "Tutorial de programación Python para principiantes", "lang": "es"},
        {"content": "Tutoriel de programmation Python pour débutants", "lang": "fr"},
        {"content": "Python プログラミング チュートリアル 初心者向け", "lang": "ja"},
        {"content": "Python Programmierung Tutorial für Anfänger", "lang": "de"}
    ]

    print(f"\n📝 Indexing {len(documents)} multilingual documents...")
    search.add_documents(documents)
    print(f"✓ Documents indexed")

    # Search in different languages
    queries = [
        ("aprender Python", "es"),
        ("learn Python programming", "en"),
        ("Python lernen", "de")
    ]

    for query, lang in queries:
        print(f"\n🔍 Query ({lang}): '{query}'")
        results = search.search(query, top_k=2)

        for i, result in enumerate(results, 1):
            doc = result['document']
            print(f"  {i}. [{doc['lang']}] Score: {result['score']:.3f} - {doc['content'][:50]}...")

    search.clear_index()
    print("\n✓ Index cleared\n")


# ============================================================================
# Example 3: Advanced Filtering with Metadata
# ============================================================================

def example_metadata_filtering():
    """
    Search with metadata filters.
    """
    print("=" * 80)
    print("Example 3: Advanced Filtering with Metadata")
    print("=" * 80)

    search = SemanticSearch(model_name="fast", store_type="chroma")

    # Documents with rich metadata
    documents = [
        {
            "content": "Introduction to supervised learning algorithms",
            "category": "AI",
            "difficulty": "beginner",
            "year": 2024,
            "author": "John Doe"
        },
        {
            "content": "Advanced deep learning architectures",
            "category": "AI",
            "difficulty": "advanced",
            "year": 2024,
            "author": "Jane Smith"
        },
        {
            "content": "Python basics for data science",
            "category": "programming",
            "difficulty": "beginner",
            "year": 2023,
            "author": "John Doe"
        },
        {
            "content": "Reinforcement learning in robotics",
            "category": "AI",
            "difficulty": "advanced",
            "year": 2023,
            "author": "Alice Johnson"
        }
    ]

    print(f"\n📝 Indexing {len(documents)} documents with metadata...")
    search.add_documents(documents)

    # Search with filters
    print("\n🔍 Search: 'machine learning' with filters:")
    print("   - Category: AI")
    print("   - Difficulty: beginner")
    print("   - Year: 2024")

    results = search.search(
        "machine learning",
        top_k=10,
        filters={
            "category": "AI",
            "difficulty": "beginner",
            "year": 2024
        }
    )

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        doc = result['document']
        print(f"{i}. {doc['content'][:60]}...")
        print(f"   Category: {doc['category']}, Difficulty: {doc['difficulty']}, Year: {doc['year']}")
        print(f"   Author: {doc['author']}, Score: {result['score']:.3f}")

    search.clear_index()
    print("\n✓ Index cleared\n")


# ============================================================================
# Example 4: Query Expansion and Re-ranking
# ============================================================================

def example_query_processing():
    """
    Advanced query processing with expansion and re-ranking.
    """
    print("=" * 80)
    print("Example 4: Query Expansion and Re-ranking")
    print("=" * 80)

    search = SemanticSearch(model_name="fast")

    # Sample documents
    documents = [
        {"content": "Machine learning algorithms and techniques"},
        {"content": "Deep neural networks for image recognition"},
        {"content": "Natural language processing with transformers"},
        {"content": "Computer vision and object detection"},
        {"content": "Reinforcement learning for game playing"}
    ]

    search.add_documents(documents)

    # Query processor
    processor = QueryProcessor(
        remove_stopwords=True,
        expand_queries=True
    )

    # Add custom expansions
    processor.add_expansion("ML", ["machine learning", "ML", "artificial intelligence"])
    processor.add_expansion("NLP", ["natural language processing", "NLP", "text analysis"])

    # Original query
    query = "ML and NLP techniques"
    print(f"\n🔍 Original query: '{query}'")

    # Process query
    processed_query = processor.process(query)
    print(f"✓ Processed query: '{processed_query}'")

    # Search without expansion
    results_basic = search.search(query, top_k=3)
    print(f"\n📊 Basic search results ({len(results_basic)}):")
    for i, result in enumerate(results_basic, 1):
        print(f"{i}. Score: {result['score']:.3f} - {result['document']['content']}")

    # Search with expansion
    results_expanded = search.search(processed_query, top_k=3)
    print(f"\n📊 Expanded search results ({len(results_expanded)}):")
    for i, result in enumerate(results_expanded, 1):
        print(f"{i}. Score: {result['score']:.3f} - {result['document']['content']}")

    search.clear_index()
    print("\n✓ Index cleared\n")


# ============================================================================
# Example 5: Batch Processing
# ============================================================================

def example_batch_processing():
    """
    Efficient batch processing for large document collections.
    """
    print("=" * 80)
    print("Example 5: Batch Processing")
    print("=" * 80)

    search = SemanticSearch(model_name="fast")

    # Generate large document collection
    print("\n📝 Generating 100 sample documents...")
    documents = []
    topics = ["AI", "programming", "data science", "web development", "cybersecurity"]

    for i in range(100):
        topic = topics[i % len(topics)]
        documents.append({
            "content": f"This is a document about {topic} - document number {i+1}",
            "topic": topic,
            "id": i
        })

    # Batch indexing
    print(f"📝 Indexing {len(documents)} documents in batches...")
    import time
    start_time = time.time()

    doc_ids = search.add_documents(documents, batch_size=32)

    elapsed = time.time() - start_time
    print(f"✓ Indexed {len(doc_ids)} documents in {elapsed:.2f}s")
    print(f"  Throughput: {len(doc_ids)/elapsed:.1f} docs/sec")

    # Batch search
    queries = [
        "artificial intelligence",
        "python programming",
        "data analysis",
        "web design",
        "security"
    ]

    print(f"\n🔍 Performing batch search for {len(queries)} queries...")
    start_time = time.time()

    all_results = search.batch_search(queries, top_k=5)

    elapsed = time.time() - start_time
    print(f"✓ Searched {len(queries)} queries in {elapsed:.2f}s")
    print(f"  Throughput: {len(queries)/elapsed:.1f} queries/sec")

    # Show sample results
    print(f"\nSample results for query: '{queries[0]}'")
    for i, result in enumerate(all_results[0][:3], 1):
        doc = result['document']
        print(f"{i}. Score: {result['score']:.3f} - {doc['content'][:60]}...")

    search.clear_index()
    print("\n✓ Index cleared\n")


# ============================================================================
# Example 6: Finding Similar Documents
# ============================================================================

def example_find_similar():
    """
    Find documents similar to a given document.
    """
    print("=" * 80)
    print("Example 6: Finding Similar Documents")
    print("=" * 80)

    search = SemanticSearch(model_name="fast")

    # Sample documents
    documents = [
        {
            "content": "Python is a versatile programming language used for web development, data science, and automation.",
            "id": "doc_1",
            "title": "Python Overview"
        },
        {
            "content": "JavaScript is essential for web development, enabling interactive user interfaces.",
            "id": "doc_2",
            "title": "JavaScript Basics"
        },
        {
            "content": "Machine learning enables computers to learn patterns from data without explicit programming.",
            "id": "doc_3",
            "title": "ML Introduction"
        },
        {
            "content": "Python's simplicity and extensive libraries make it ideal for data analysis and scientific computing.",
            "id": "doc_4",
            "title": "Python for Data Science"
        },
        {
            "content": "Deep learning, a subset of machine learning, uses neural networks to solve complex problems.",
            "id": "doc_5",
            "title": "Deep Learning"
        }
    ]

    print(f"\n📝 Indexing {len(documents)} documents...")
    doc_ids = search.add_documents(documents)

    # Find similar documents
    target_doc_id = doc_ids[0]  # First document (Python Overview)
    print(f"\n🔍 Finding documents similar to: '{documents[0]['title']}'")
    print(f"   Content: {documents[0]['content'][:70]}...")

    similar = search.search_similar(target_doc_id, top_k=3)

    print(f"\nFound {len(similar)} similar documents:")
    for i, result in enumerate(similar, 1):
        doc = result['document']
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Title: {doc.get('title', 'N/A')}")
        print(f"   Content: {doc['content'][:70]}...")
        print()

    search.clear_index()
    print("✓ Index cleared\n")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 20 + "BERT Semantic Search - Examples")
    print("=" * 80 + "\n")

    try:
        # Run examples
        example_basic_search()
        input("Press Enter to continue to next example...")

        example_multilingual_search()
        input("Press Enter to continue to next example...")

        example_metadata_filtering()
        input("Press Enter to continue to next example...")

        example_query_processing()
        input("Press Enter to continue to next example...")

        example_batch_processing()
        input("Press Enter to continue to next example...")

        example_find_similar()

        print("\n" + "=" * 80)
        print(" " * 25 + "All examples completed!")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
