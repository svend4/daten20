#!/usr/bin/env python3
"""
Document Semantic Search - BERT-based semantic search CLI

Advanced semantic search using BERT embeddings for intelligent document retrieval.

Features:
- Index documents with BERT embeddings
- Semantic similarity search
- Multi-lingual support
- Query expansion
- Result re-ranking

Examples:
    # Index documents from directory
    python doc-semantic-search.py index ./documents/ --recursive

    # Search for similar documents
    python doc-semantic-search.py search "machine learning tutorial"

    # Find similar documents to a specific document
    python doc-semantic-search.py similar doc_123 --top-k 10

    # Clear index
    python doc-semantic-search.py clear --confirm
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search import SemanticSearch, QueryProcessor, ResultReranker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_documents_from_directory(
    directory: str,
    recursive: bool = False,
    file_extensions: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Load documents from directory.
    
    Args:
        directory: Directory path
        recursive: Search recursively
        file_extensions: List of file extensions to include
    
    Returns:
        List of document dicts
    """
    if file_extensions is None:
        file_extensions = ['.txt', '.md', '.json']
    
    documents = []
    path = Path(directory)
    
    # Get files
    if recursive:
        files = [f for ext in file_extensions for f in path.rglob(f'*{ext}')]
    else:
        files = [f for ext in file_extensions for f in path.glob(f'*{ext}')]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = {
                "content": content,
                "filename": file_path.name,
                "path": str(file_path),
                "extension": file_path.suffix
            }
            documents.append(doc)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
    
    return documents


def cmd_index(args):
    """Index documents."""
    logger.info(f"Indexing documents from: {args.path}")
    
    # Initialize search engine
    search = SemanticSearch(
        model_name=args.model,
        store_type=args.store,
        persist_directory=args.db_path
    )
    
    # Load documents
    if os.path.isdir(args.path):
        documents = load_documents_from_directory(
            args.path,
            recursive=args.recursive,
            file_extensions=args.extensions.split(',') if args.extensions else None
        )
    elif os.path.isfile(args.path):
        # Load single file
        with open(args.path, 'r') as f:
            if args.path.endswith('.json'):
                documents = json.load(f)
            else:
                content = f.read()
                documents = [{"content": content, "filename": os.path.basename(args.path)}]
    else:
        logger.error(f"Path not found: {args.path}")
        return 1
    
    if not documents:
        logger.warning("No documents found to index")
        return 0
    
    logger.info(f"Found {len(documents)} documents")
    
    # Index documents
    doc_ids = search.add_documents(documents, batch_size=args.batch_size)
    
    logger.info(f"✓ Successfully indexed {len(doc_ids)} documents")
    logger.info(f"Total documents in index: {search.count_documents()}")
    
    return 0


def cmd_search(args):
    """Search for documents."""
    logger.info(f"Searching for: {args.query}")
    
    # Initialize search engine
    search = SemanticSearch(
        model_name=args.model,
        store_type=args.store,
        persist_directory=args.db_path
    )
    
    # Process query
    if args.expand:
        processor = QueryProcessor(expand_queries=True)
        processed_query = processor.process(args.query)
        logger.info(f"Processed query: {processed_query}")
    else:
        processed_query = args.query
    
    # Search
    results = search.search(
        processed_query,
        top_k=args.top_k,
        min_score=args.min_score
    )
    
    # Re-rank if requested
    if args.rerank:
        reranker = ResultReranker()
        results = reranker.rerank(results, args.query)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Search Results for: '{args.query}'")
    print(f"{'='*80}\n")
    
    if not results:
        print("No results found.")
        return 0
    
    for i, result in enumerate(results, 1):
        doc = result['document']
        score = result.get('score', 0.0)
        
        print(f"{i}. Score: {score:.3f}")
        if isinstance(doc, dict):
            if 'filename' in doc:
                print(f"   File: {doc['filename']}")
            if 'content' in doc:
                # Show preview
                content = doc['content']
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   {preview}")
        else:
            print(f"   {doc}")
        print()
    
    # Export results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to: {args.output}")
    
    return 0


def cmd_similar(args):
    """Find similar documents."""
    logger.info(f"Finding documents similar to: {args.document_id}")
    
    # Initialize search engine
    search = SemanticSearch(
        model_name=args.model,
        store_type=args.store,
        persist_directory=args.db_path
    )
    
    # Find similar
    results = search.search_similar(
        args.document_id,
        top_k=args.top_k
    )
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Similar Documents to: '{args.document_id}'")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        doc = result['document']
        score = result.get('score', 0.0)
        
        print(f"{i}. Score: {score:.3f}")
        print(f"   ID: {result['id']}")
        if isinstance(doc, dict) and 'filename' in doc:
            print(f"   File: {doc['filename']}")
        print()
    
    return 0


def cmd_stats(args):
    """Show index statistics."""
    # Initialize search engine
    search = SemanticSearch(
        model_name=args.model,
        store_type=args.store,
        persist_directory=args.db_path
    )
    
    stats = search.get_stats()
    
    print(f"\n{'='*80}")
    print("Semantic Search Statistics")
    print(f"{'='*80}\n")
    
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Vector Store: {stats['vector_store_type']}")
    print(f"\nEmbedder Info:")
    for key, value in stats['embedder_info'].items():
        print(f"  {key}: {value}")
    
    return 0


def cmd_clear(args):
    """Clear index."""
    if not args.confirm:
        response = input("Are you sure you want to clear the index? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return 0
    
    # Initialize search engine
    search = SemanticSearch(
        model_name=args.model,
        store_type=args.store,
        persist_directory=args.db_path
    )
    
    count_before = search.count_documents()
    search.clear_index()
    
    logger.info(f"✓ Cleared {count_before} documents from index")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Document Semantic Search - BERT-based search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Global options
    parser.add_argument('--model', default='fast',
                       help='Embedding model (fast/balanced/multilingual/large)')
    parser.add_argument('--store', default='chroma', choices=['chroma', 'faiss'],
                       help='Vector store type')
    parser.add_argument('--db-path', default='./semantic_search_db',
                       help='Database path')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documents')
    index_parser.add_argument('path', help='Path to file or directory')
    index_parser.add_argument('--recursive', '-r', action='store_true',
                             help='Search directories recursively')
    index_parser.add_argument('--extensions', default='.txt,.md,.json',
                             help='File extensions to include (comma-separated)')
    index_parser.add_argument('--batch-size', type=int, default=32,
                             help='Batch size for embedding')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--top-k', '-k', type=int, default=10,
                              help='Number of results')
    search_parser.add_argument('--min-score', type=float,
                              help='Minimum similarity score')
    search_parser.add_argument('--expand', action='store_true',
                              help='Expand query with synonyms')
    search_parser.add_argument('--rerank', action='store_true',
                              help='Re-rank results')
    search_parser.add_argument('--output', '-o',
                              help='Save results to file (JSON)')
    
    # Similar command
    similar_parser = subparsers.add_parser('similar', help='Find similar documents')
    similar_parser.add_argument('document_id', help='Document ID')
    similar_parser.add_argument('--top-k', '-k', type=int, default=10,
                               help='Number of results')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear index')
    clear_parser.add_argument('--confirm', action='store_true',
                             help='Skip confirmation')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'index':
        return cmd_index(args)
    elif args.command == 'search':
        return cmd_search(args)
    elif args.command == 'similar':
        return cmd_similar(args)
    elif args.command == 'stats':
        return cmd_stats(args)
    elif args.command == 'clear':
        return cmd_clear(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
