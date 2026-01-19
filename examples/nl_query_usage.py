#!/usr/bin/env python3
"""
Natural Language Query - Usage Examples

This module demonstrates real-world applications of the NL Query system,
including:
- Intent classification for different query types
- Entity extraction from natural language
- SQL query generation
- Aggregation pipeline generation
- Business analytics queries
- Multi-language support basics
- Conversation context management

Author: DMS Team
Date: 2026-01-16
"""

from src.analytics.nl_query import (
    NLQueryProcessor,
    IntentClassifier,
    EntityExtractor,
    QueryGenerator,
    TimeRange,
    get_nl_processor,
)


# ============================================================================
# EXAMPLE 1: Basic Query Processing
# ============================================================================


def example_basic_queries():
    """
    Example: Process basic natural language queries

    Use Case: Business user wants to ask questions in plain English
    Demonstrates: Intent classification and entity extraction
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Query Processing")
    print("=" * 80)

    processor = NLQueryProcessor()

    # Define test queries
    queries = [
        "What is the total revenue?",
        "Show me all customers",
        "How many users signed up last month?",
        "Find transactions greater than 1000 dollars",
        "Display products sorted by price",
    ]

    print("\n📝 Processing natural language queries...\n")

    for query in queries:
        print(f"Query: '{query}'")

        # Process query
        parsed = processor.process(query)

        print(f"  ✓ Intent: {parsed.intent.value}")
        print(f"  ✓ Confidence: {parsed.confidence:.2f}")
        print(f"  ✓ Metric: {parsed.metric}")
        print(f"  ✓ Aggregate: {parsed.aggregate_function.value if parsed.aggregate_function else 'None'}")
        print(f"  ✓ Entities Found: {len(parsed.entities)}")
        print()

    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 2: SQL Query Generation
# ============================================================================


def example_sql_generation():
    """
    Example: Convert natural language to SQL queries

    Use Case: Non-technical users want to query databases
    Demonstrates: SQL generation from NL queries
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: SQL Query Generation")
    print("=" * 80)

    processor = NLQueryProcessor()

    # Business queries
    business_queries = [
        "What is the total revenue for last month?",
        "Show me the top 10 customers by sales",
        "Average order value by product category",
        "Count active subscriptions",
        "Find all users who registered this year",
    ]

    print("\n🔍 Generating SQL from natural language...\n")

    for query in business_queries:
        print(f"Question: {query}")
        print(f"Intent: {processor.process(query).intent.value}\n")

        # Generate SQL
        sql = processor.to_sql(query)

        print("Generated SQL:")
        print(f"  {sql}")
        print()
        print("-" * 80)
        print()

    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 3: Aggregation Pipeline Generation
# ============================================================================


def example_aggregation_pipeline():
    """
    Example: Generate MongoDB-style aggregation pipelines

    Use Case: NoSQL database queries from natural language
    Demonstrates: Aggregation pipeline generation
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Aggregation Pipeline Generation")
    print("=" * 80)

    processor = NLQueryProcessor()

    queries = [
        "Total sales by region",
        "Average revenue per customer",
        "Top 5 products by profit margin",
    ]

    print("\n📊 Generating aggregation pipelines...\n")

    for query in queries:
        print(f"Query: {query}\n")

        # Generate pipeline
        pipeline = processor.to_aggregation_pipeline(query)

        print("Aggregation Pipeline:")
        for i, stage in enumerate(pipeline, 1):
            stage_name = list(stage.keys())[0]
            print(f"  Stage {i}: {stage_name}")
            print(f"    {stage}")

        print()
        print("-" * 80)
        print()

    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 4: Time Range Queries
# ============================================================================


def example_time_range_queries():
    """
    Example: Queries with time ranges

    Use Case: Temporal analysis and trend queries
    Demonstrates: Time range extraction and parsing
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Time Range Queries")
    print("=" * 80)

    processor = NLQueryProcessor()

    time_queries = [
        "Show sales for today",
        "Revenue from last 7 days",
        "User signups this month",
        "Transactions from last week",
        "Year-over-year growth",
    ]

    print("\n📅 Processing time-based queries...\n")

    for query in time_queries:
        print(f"Query: '{query}'")

        parsed = processor.process(query)

        if parsed.time_range:
            start, end = parsed.time_range.to_absolute()
            days = (end - start).days

            print(f"  Time Range: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
            print(f"  Duration: {days} days")
        else:
            print(f"  Time Range: Not specified (default to last 30 days)")

        # Generate SQL
        sql = processor.to_sql(query)
        if "timestamp" in sql:
            print(f"  ✓ Time filter added to SQL")

        print()

    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 5: Advanced Analytics Queries
# ============================================================================


def example_advanced_analytics():
    """
    Example: Complex analytics queries

    Use Case: Executive dashboards and business intelligence
    Demonstrates: Multi-dimensional analysis
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Advanced Analytics Queries")
    print("=" * 80)

    processor = NLQueryProcessor()

    advanced_queries = [
        {
            "query": "What is the total revenue by product category for last quarter?",
            "description": "Multi-dimensional aggregate with time filter",
        },
        {
            "query": "Show me the top 10 customers by lifetime value",
            "description": "Ranking query with aggregate metric",
        },
        {
            "query": "Compare average order value between new and returning customers",
            "description": "Comparative analysis across segments",
        },
        {
            "query": "Find all transactions where amount exceeds 5000",
            "description": "Filter query with threshold",
        },
        {
            "query": "How has monthly recurring revenue trended over the past year?",
            "description": "Trend analysis with time series",
        },
    ]

    print("\n📈 Processing advanced analytics queries...\n")

    for item in advanced_queries:
        query = item["query"]
        description = item["description"]

        print(f"Scenario: {description}")
        print(f"Query: '{query}'")

        parsed = processor.process(query)

        print(f"\n  Analysis:")
        print(f"    Intent: {parsed.intent.value}")
        print(f"    Metric: {parsed.metric or 'N/A'}")
        print(f"    Dimensions: {', '.join(parsed.dimensions) if parsed.dimensions else 'None'}")
        print(f"    Aggregate: {parsed.aggregate_function.value if parsed.aggregate_function else 'None'}")

        if parsed.limit:
            print(f"    Limit: Top {parsed.limit}")

        if parsed.time_range:
            print(f"    Time Range: Yes")

        # Generate both SQL and pipeline
        sql = processor.to_sql(query)
        pipeline = processor.to_aggregation_pipeline(query)

        print(f"\n  SQL Length: {len(sql)} characters")
        print(f"  Pipeline Stages: {len(pipeline)}")

        print()
        print("-" * 80)
        print()

    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 6: Intent Classification
# ============================================================================


def example_intent_classification():
    """
    Example: Demonstrate all intent types

    Use Case: Understanding user's query intention
    Demonstrates: All 8 intent types
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Intent Classification")
    print("=" * 80)

    classifier = IntentClassifier()

    intent_examples = [
        ("AGGREGATE", "What is the total revenue?"),
        ("FILTER", "Show customers where revenue > 1000"),
        ("SORT", "Sort products by price descending"),
        ("COMPARE", "Compare Q1 revenue vs Q2 revenue"),
        ("TREND", "Show user growth trend over time"),
        ("TOP_N", "Display top 10 products by sales"),
        ("FORECAST", "Predict revenue for next month"),
        ("ANOMALY", "Find anomalies in transaction patterns"),
    ]

    print("\n🎯 Classifying query intents...\n")

    for expected_intent, query in intent_examples:
        intent, confidence = classifier.classify(query)

        status = "✓" if intent.value.upper() in expected_intent.upper() else "⚠"
        print(f"{status} Expected: {expected_intent:12} | Got: {intent.value:12} | Confidence: {confidence:.2f}")
        print(f"   Query: '{query}'")
        print()

    print("=" * 80)


# ============================================================================
# EXAMPLE 7: Entity Extraction
# ============================================================================


def example_entity_extraction():
    """
    Example: Extract entities from queries

    Use Case: Understanding query components
    Demonstrates: Metrics, dimensions, time, numbers, aggregates
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Entity Extraction")
    print("=" * 80)

    extractor = EntityExtractor()

    test_queries = [
        "What is the total revenue by product category for last 30 days?",
        "Show me customers with lifetime value greater than 5000",
        "Average order count per user in the US region",
    ]

    print("\n🔎 Extracting entities from queries...\n")

    for query in test_queries:
        print(f"Query: '{query}'")

        entities = extractor.extract(query)

        # Group entities by type
        by_type = {}
        for entity in entities:
            entity_type = entity.entity_type
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)

        print(f"\n  Entities Found: {len(entities)}")

        for entity_type, entity_list in by_type.items():
            print(f"\n  {entity_type.upper()}:")
            for entity in entity_list:
                print(f"    - {entity.value} (confidence: {entity.confidence:.2f})")

        print()
        print("-" * 80)
        print()

    print("=" * 80)


# ============================================================================
# EXAMPLE 8: Conversation Context
# ============================================================================


def example_conversation_context():
    """
    Example: Multi-turn conversation

    Use Case: Building upon previous queries
    Demonstrates: Context management
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Conversation Context")
    print("=" * 80)

    processor = NLQueryProcessor()

    conversation = [
        "What is the total revenue?",
        "Show me the breakdown by product",
        "Which products performed best?",
        "What about last month's numbers?",
    ]

    print("\n💬 Processing conversational queries...\n")

    for i, query in enumerate(conversation, 1):
        print(f"Turn {i}: User asks '{query}'")

        parsed = processor.process(query)

        print(f"  System understands:")
        print(f"    Intent: {parsed.intent.value}")
        print(f"    Metric: {parsed.metric or 'Same as before'}")

        # Show context length
        context = processor.get_conversation_context()
        print(f"    Context Length: {len(context)} queries")

        print()

    print("📊 Conversation Summary:")
    context = processor.get_conversation_context()
    print(f"   Total Queries Processed: {len(context)}")
    print(f"   Unique Intents: {len(set(q.intent for q in context))}")

    print()
    print("=" * 80)
    return processor


# ============================================================================
# EXAMPLE 9: Business Intelligence Queries
# ============================================================================


def example_business_intelligence():
    """
    Example: Common BI dashboard queries

    Use Case: Executive dashboards and KPI tracking
    Demonstrates: Real-world business scenarios
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Business Intelligence Queries")
    print("=" * 80)

    processor = NLQueryProcessor()

    bi_queries = {
        "Revenue Metrics": [
            "What is our MRR (Monthly Recurring Revenue)?",
            "Show total revenue for last quarter",
            "Revenue growth rate year-over-year",
        ],
        "Customer Metrics": [
            "How many active customers do we have?",
            "Customer churn rate this month",
            "Top 20 customers by lifetime value",
        ],
        "Product Metrics": [
            "Which products have the highest profit margin?",
            "Average order value by product category",
            "Products with declining sales",
        ],
        "Operational Metrics": [
            "Average response time for customer support",
            "Number of open tickets by priority",
            "Employee productivity metrics",
        ],
    }

    print("\n📊 Processing Business Intelligence Queries...\n")

    for category, queries in bi_queries.items():
        print(f"\n{category}:")
        print("=" * 60)

        for query in queries:
            parsed = processor.process(query)

            print(f"\n  Q: {query}")
            print(f"     Intent: {parsed.intent.value}")
            print(f"     Metric: {parsed.metric or 'Multiple/Complex'}")

            # Generate SQL (simplified output)
            sql = processor.to_sql(query)
            sql_preview = sql[:80] + "..." if len(sql) > 80 else sql
            print(f"     SQL: {sql_preview}")

    print("\n" + "=" * 80)
    return processor


# ============================================================================
# EXAMPLE 10: Custom Schema
# ============================================================================


def example_custom_schema():
    """
    Example: Use custom data schema

    Use Case: Domain-specific terminology
    Demonstrates: Schema customization for specific industries
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Custom Schema")
    print("=" * 80)

    # Define custom schema for e-commerce
    ecommerce_schema = {
        "metrics": [
            "revenue",
            "sales",
            "orders",
            "cart_value",
            "conversion_rate",
            "bounce_rate",
            "page_views",
            "session_duration",
        ],
        "dimensions": [
            "product",
            "category",
            "brand",
            "customer_segment",
            "channel",
            "device_type",
            "geography",
            "campaign",
        ],
    }

    processor = NLQueryProcessor(schema=ecommerce_schema)

    # E-commerce specific queries
    ecommerce_queries = [
        "What is the total cart value by customer segment?",
        "Show conversion rate by channel and device type",
        "Average session duration for mobile users",
        "Top 5 products by sales in electronics category",
    ]

    print("\n🛒 Processing E-commerce Queries with Custom Schema...\n")

    for query in ecommerce_queries:
        print(f"Query: '{query}'")

        parsed = processor.process(query)

        print(f"  Metric: {parsed.metric}")
        print(f"  Dimensions: {', '.join(parsed.dimensions) if parsed.dimensions else 'None'}")
        print(f"  Entities: {len(parsed.entities)}")

        # Show which custom schema terms were recognized
        recognized = [e.value for e in parsed.entities if e.entity_type in ["metric", "dimension"]]
        if recognized:
            print(f"  Recognized Terms: {', '.join(recognized)}")

        print()

    print("=" * 80)
    return processor


# ============================================================================
# MAIN: Run All Examples
# ============================================================================


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("NATURAL LANGUAGE QUERY - USAGE EXAMPLES")
    print("=" * 80)
    print("\nDemonstrating comprehensive NL query capabilities:")
    print("  1. Basic query processing")
    print("  2. SQL query generation")
    print("  3. Aggregation pipeline generation")
    print("  4. Time range queries")
    print("  5. Advanced analytics queries")
    print("  6. Intent classification")
    print("  7. Entity extraction")
    print("  8. Conversation context")
    print("  9. Business intelligence queries")
    print(" 10. Custom schema support")

    try:
        # Run examples
        example_basic_queries()
        example_sql_generation()
        example_aggregation_pipeline()
        example_time_range_queries()
        example_advanced_analytics()
        example_intent_classification()
        example_entity_extraction()
        example_conversation_context()
        example_business_intelligence()
        example_custom_schema()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY! ✅")
        print("=" * 80)
        print("\n💡 Key Capabilities:")
        print("   • 8 query intent types (aggregate, filter, sort, compare, trend, top_n, forecast, anomaly)")
        print("   • Entity extraction (metrics, dimensions, time ranges, numbers, aggregates)")
        print("   • SQL query generation for relational databases")
        print("   • Aggregation pipeline generation for NoSQL databases")
        print("   • Time range parsing (absolute and relative)")
        print("   • Conversation context management")
        print("   • Custom schema support for domain-specific terminology")
        print("   • Real-world business intelligence scenarios")
        print("\n📚 For more information, see:")
        print("   • src/analytics/nl_query.py")
        print("   • tests/unit/analytics/test_nl_query.py")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
