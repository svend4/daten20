#!/usr/bin/env python3
"""
Semantic Search Examples

Practical examples demonstrating BERT semantic search capabilities.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search import SemanticSearch, QueryProcessor, ResultReranker


def example_1_basic_search():
    """Example 1: Basic semantic search."""
    print("\n" + "="*80)
    print("Example 1: Basic Semantic Search")
    print("="*80)
    
    # Initialize search engine
    search = SemanticSearch(model_name="fast", store_type="chroma")
    
    # Clear any existing data
    search.clear_index()
    
    # Add sample documents
    documents = [
        {"content": "Python is a high-level programming language", "category": "programming"},
        {"content": "Machine learning is a subset of artificial intelligence", "category": "AI"},
        {"content": "Deep learning uses neural networks", "category": "AI"},
        {"content": "JavaScript is used for web development", "category": "programming"},
        {"content": "Data science involves statistics and programming", "category": "data"}
    ]
    
    print(f"\n📚 Indexing {len(documents)} documents...")
    search.add_documents(documents)
    print(f"✓ Indexed successfully")
    
    # Search
    query = "learn artificial intelligence"
    print(f"\n🔍 Searching for: '{query}'")
    
    results = search.search(query, top_k=3)
    
    print(f"\n📊 Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Content: {result['document']['content']}")
        print(f"   Category: {result['document']['category']}")


def example_2_multilingual_search():
    """Example 2: Multi-lingual semantic search."""
    print("\n" + "="*80)
    print("Example 2: Multi-lingual Semantic Search")
    print("="*80)
    
    # Use multilingual model
    search = SemanticSearch(model_name="multilingual", store_type="chroma")
    search.clear_index()
    
    # Documents in multiple languages
    documents = [
        {"content": "Python programming tutorial", "lang": "en"},
        {"content": "Tutorial de programación en Python", "lang": "es"},
        {"content": "Python プログラミング チュートリアル", "lang": "ja"},
        {"content": "Tutoriel de programmation Python", "lang": "fr"}
    ]
    
    print(f"\n📚 Indexing {len(documents)} multilingual documents...")
    search.add_documents(documents)
    
    # Search in different languages
    queries = [
        ("learn Python", "en"),
        ("aprender Python", "es"),
        ("学ぶ Python", "ja")
    ]
    
    for query, lang in queries:
        print(f"\n🔍 Query ({lang}): '{query}'")
        results = search.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['score']:.3f} - {result['document']['content']}")


def example_3_query_expansion():
    """Example 3: Query expansion and re-ranking."""
    print("\n" + "="*80)
    print("Example 3: Query Expansion and Re-ranking")
    print("="*80)
    
    search = SemanticSearch(model_name="fast")
    search.clear_index()
    
    # Documents
    documents = [
        {"content": "Machine learning algorithms for beginners", "difficulty": "easy"},
        {"content": "Advanced neural network architectures", "difficulty": "hard"},
        {"content": "Introduction to artificial intelligence", "difficulty": "easy"},
        {"content": "Deep learning optimization techniques", "difficulty": "hard"}
    ]
    
    search.add_documents(documents)
    
    # Query processor
    processor = QueryProcessor(expand_queries=True)
    processor.add_expansion("ML", ["machine learning", "ML", "artificial intelligence"])
    
    # Original query
    query = "ML tutorial"
    processed_query = processor.process(query)
    
    print(f"\n🔍 Original query: '{query}'")
    print(f"✨ Expanded query: '{processed_query}'")
    
    # Search
    results = search.search(processed_query, top_k=4)
    
    print(f"\n📊 Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f} - {result['document']['content']}")
    
    # Re-rank results
    reranker = ResultReranker()
    reranked = reranker.rerank(results, query)
    
    print(f"\n🔄 Re-ranked results:")
    for i, result in enumerate(reranked, 1):
        print(f"{i}. Score: {result['score']:.3f} (boost: {result.get('boost', 0):.3f})")
        print(f"   {result['document']['content']}")


def example_4_metadata_filtering():
    """Example 4: Search with metadata filters."""
    print("\n" + "="*80)
    print("Example 4: Metadata Filtering")
    print("="*80)
    
    search = SemanticSearch(model_name="fast")
    search.clear_index()
    
    # Documents with metadata
    documents = [
        {"content": "Python tutorial for beginners", "language": "python", "level": "beginner"},
        {"content": "Advanced Python techniques", "language": "python", "level": "advanced"},
        {"content": "JavaScript basics", "language": "javascript", "level": "beginner"},
        {"content": "React advanced patterns", "language": "javascript", "level": "advanced"}
    ]
    
    search.add_documents(documents)
    
    # Search with filters
    query = "programming tutorial"
    
    print(f"\n🔍 Query: '{query}'")
    print(f"🏷️  Filter: language=python, level=beginner")
    
    results = search.search(
        query,
        top_k=10,
        filters={"language": "python", "level": "beginner"}
    )
    
    print(f"\n📊 Filtered results:")
    for i, result in enumerate(results, 1):
        doc = result['document']
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Content: {doc['content']}")
        print(f"   Language: {doc['language']}, Level: {doc['level']}")


def example_5_find_similar():
    """Example 5: Find similar documents."""
    print("\n" + "="*80)
    print("Example 5: Find Similar Documents")
    print("="*80)
    
    search = SemanticSearch(model_name="fast")
    search.clear_index()
    
    # Documents
    documents = [
        {"content": "Python is great for data science", "id": "doc_1"},
        {"content": "Data analysis with pandas library", "id": "doc_2"},
        {"content": "JavaScript for frontend development", "id": "doc_3"},
        {"content": "React framework for building UIs", "id": "doc_4"},
        {"content": "Machine learning with scikit-learn", "id": "doc_5"}
    ]
    
    # Use custom IDs
    ids = [doc['id'] for doc in documents]
    search.add_documents(documents, ids=ids)
    
    # Find documents similar to doc_1
    reference_id = "doc_1"
    reference_doc = search.get_document(reference_id)
    
    print(f"\n📄 Reference document: '{reference_doc['document']['content']}'")
    print(f"\n🔍 Finding similar documents...")
    
    similar = search.search_similar(reference_id, top_k=3)
    
    print(f"\n📊 Similar documents:")
    for i, result in enumerate(similar, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   ID: {result['id']}")
        print(f"   Content: {result['document']['content']}")


def example_6_batch_operations():
    """Example 6: Batch indexing and search."""
    print("\n" + "="*80)
    print("Example 6: Batch Operations")
    print("="*80)
    
    search = SemanticSearch(model_name="fast")
    search.clear_index()
    
    # Large batch of documents
    print(f"\n📚 Creating 100 sample documents...")
    documents = []
    topics = ["Python", "JavaScript", "Machine Learning", "Data Science", "Web Development"]
    
    for i in range(100):
        topic = topics[i % len(topics)]
        documents.append({
            "content": f"{topic} tutorial number {i+1}",
            "topic": topic,
            "index": i
        })
    
    # Batch indexing
    print(f"📥 Indexing {len(documents)} documents in batches...")
    doc_ids = search.add_documents(documents, batch_size=32)
    print(f"✓ Indexed {len(doc_ids)} documents")
    
    # Batch search
    queries = [
        "Python programming",
        "web development",
        "artificial intelligence"
    ]
    
    print(f"\n🔍 Batch searching for {len(queries)} queries...")
    batch_results = search.batch_search(queries, top_k=3)
    
    for i, (query, results) in enumerate(zip(queries, batch_results)):
        print(f"\n{i+1}. Query: '{query}' - {len(results)} results")
        for j, result in enumerate(results[:2], 1):  # Show top 2
            print(f"   {j}. Score: {result['score']:.3f} - {result['document']['content']}")
    
    # Get statistics
    stats = search.get_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Embedder: {stats['embedder_info']['model_name']}")
    print(f"   Embedding dimension: {stats['embedder_info']['embedding_dim']}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("BERT Semantic Search Examples")
    print("="*80)
    
    examples = [
        ("Basic Search", example_1_basic_search),
        ("Multi-lingual Search", example_2_multilingual_search),
        ("Query Expansion", example_3_query_expansion),
        ("Metadata Filtering", example_4_metadata_filtering),
        ("Find Similar", example_5_find_similar),
        ("Batch Operations", example_6_batch_operations)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\n" + "-"*80)
    choice = input("\nEnter example number (1-6) or 'all' to run all: ").strip()
    
    if choice.lower() == 'all':
        for name, func in examples:
            try:
                func()
                input("\n\nPress Enter to continue to next example...")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
                import traceback
                traceback.print_exc()
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
