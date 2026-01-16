#!/usr/bin/env python3
"""
Document Analysis Dashboard
============================

Interactive web dashboard for document analysis and visualization.

Features:
- Real-time document upload and processing
- Interactive visualizations (charts, graphs, word clouds)
- Knowledge graph visualization (D3.js/NetworkX)
- Entity and relation explorer
- Document statistics and analytics
- Batch processing monitoring
- Export capabilities (PDF, Excel, JSON)
- RESTful API backend

Tech Stack:
- Backend: Flask/FastAPI
- Frontend: HTML5, Bootstrap, JavaScript
- Visualization: Chart.js, D3.js, vis.js
- Database: SQLite/PostgreSQL

Usage:
    # Start dashboard server
    python doc-dashboard.py

    # Custom port
    python doc-dashboard.py --port 8080

    # Production mode
    python doc-dashboard.py --host 0.0.0.0 --port 80 --production

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from flask import Flask, jsonify, render_template_string, request, send_file
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("WARNING: Flask not installed. Install with: pip install flask flask-cors")

from werkzeug.utils import secure_filename

from src.core.database import DocumentDatabase
from src.core.logging_config import setup_logging

# Import our modules
from src.core.parser import DocumentParser
from src.ml.classifier import TfidfSVMClassifier
from src.ml.knowledge_graph import GraphFormat, KnowledgeGraphBuilder
from src.ml.ner import NEREngine
from src.ml.relation_extractor import RelationExtractor

# Setup logging
logger = setup_logging(__name__, log_level="INFO")

# Flask app setup
app = Flask(__name__) if FLASK_AVAILABLE else None
if app:
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size
    app.config["UPLOAD_FOLDER"] = "data/uploads"


# HTML Template for Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Analysis Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { background-color: #f5f5f5; padding: 20px; }
        .card { margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-card { text-align: center; padding: 20px; }
        .stats-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .upload-area { border: 2px dashed #007bff; padding: 40px; text-align: center; cursor: pointer; }
        .upload-area:hover { background-color: #e7f3ff; }
        #knowledge-graph { width: 100%; height: 600px; border: 1px solid #ddd; }
        .entity-badge { margin: 3px; }
        .relation-item { padding: 10px; margin: 5px 0; background: #f8f9fa; border-left: 3px solid #007bff; }
        .processing { display: none; }
        .spinner-border { width: 3rem; height: 3rem; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="mb-4">📊 Document Analysis Dashboard</h1>

        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stats-card">
                    <h6>Total Documents</h6>
                    <div class="stats-number" id="totalDocs">0</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <h6>Entities Extracted</h6>
                    <div class="stats-number" id="totalEntities">0</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <h6>Relations Found</h6>
                    <div class="stats-number" id="totalRelations">0</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card">
                    <h6>Processing Time</h6>
                    <div class="stats-number" id="processingTime">0s</div>
                </div>
            </div>
        </div>

        <!-- Upload Section -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">📤 Upload Document</h5>
                        <div class="upload-area" id="uploadArea">
                            <input type="file" id="fileInput" style="display: none;" accept=".pdf,.txt,.docx">
                            <p>Click or drag document here to upload</p>
                            <p class="text-muted">Supported: PDF, TXT, DOCX (Max 50MB)</p>
                        </div>
                        <div class="processing text-center mt-3" id="processingIndicator">
                            <div class="spinner-border text-primary" role="status"></div>
                            <p class="mt-2">Processing document...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div class="row">
            <!-- Entities Panel -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">🏷️ Extracted Entities</h5>
                        <div id="entitiesContainer">
                            <p class="text-muted">Upload a document to see extracted entities</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Relations Panel -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">🔗 Relations</h5>
                        <div id="relationsContainer">
                            <p class="text-muted">Upload a document to see extracted relations</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Classification & Topics -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">📂 Document Classification</h5>
                        <canvas id="classificationChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">🔖 Topics</h5>
                        <canvas id="topicsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Knowledge Graph -->
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">🕸️ Knowledge Graph</h5>
                        <div id="knowledge-graph"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Upload handling
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processingIndicator = document.getElementById('processingIndicator');

        uploadArea.onclick = () => fileInput.click();
        fileInput.onchange = handleFileUpload;

        uploadArea.ondrop = (e) => {
            e.preventDefault();
            handleFiles(e.dataTransfer.files);
        };
        uploadArea.ondragover = (e) => e.preventDefault();

        function handleFileUpload() {
            handleFiles(fileInput.files);
        }

        async function handleFiles(files) {
            if (files.length === 0) return;

            const formData = new FormData();
            formData.append('file', files[0]);

            processingIndicator.style.display = 'block';
            const startTime = Date.now();

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });

                const results = await response.json();
                const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);

                updateDashboard(results, processingTime);
            } catch (error) {
                alert('Error processing document: ' + error.message);
            } finally {
                processingIndicator.style.display = 'none';
            }
        }

        function updateDashboard(results, processingTime) {
            // Update statistics
            document.getElementById('totalDocs').textContent = '1';
            document.getElementById('totalEntities').textContent = results.statistics.entity_count;
            document.getElementById('totalRelations').textContent = results.statistics.relation_count;
            document.getElementById('processingTime').textContent = processingTime + 's';

            // Update entities
            updateEntities(results.entities);

            // Update relations
            updateRelations(results.relations);

            // Update classification chart
            updateClassificationChart(results.classification);

            // Update topics chart
            updateTopicsChart(results.topics);

            // Update knowledge graph
            if (results.knowledge_graph) {
                updateKnowledgeGraph(results.knowledge_graph);
            }
        }

        function updateEntities(entities) {
            const container = document.getElementById('entitiesContainer');
            const entityByType = {};

            entities.forEach(e => {
                if (!entityByType[e.type]) entityByType[e.type] = [];
                entityByType[e.type].push(e);
            });

            container.innerHTML = '';
            for (const [type, items] of Object.entries(entityByType)) {
                const heading = document.createElement('h6');
                heading.textContent = type;
                heading.className = 'mt-3';
                container.appendChild(heading);

                items.forEach(e => {
                    const badge = document.createElement('span');
                    badge.className = `badge bg-primary entity-badge`;
                    badge.textContent = `${e.text} (${(e.confidence * 100).toFixed(0)}%)`;
                    container.appendChild(badge);
                });
            }
        }

        function updateRelations(relations) {
            const container = document.getElementById('relationsContainer');
            container.innerHTML = '';

            if (relations.length === 0) {
                container.innerHTML = '<p class="text-muted">No relations found</p>';
                return;
            }

            relations.forEach(r => {
                const div = document.createElement('div');
                div.className = 'relation-item';
                div.innerHTML = `
                    <strong>${r.source}</strong>
                    <span class="badge bg-secondary mx-2">${r.relation}</span>
                    <strong>${r.target}</strong>
                    <small class="text-muted float-end">${(r.confidence * 100).toFixed(0)}%</small>
                `;
                container.appendChild(div);
            });
        }

        function updateClassificationChart(classification) {
            const ctx = document.getElementById('classificationChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Confidence', 'Uncertainty'],
                    datasets: [{
                        data: [classification.confidence * 100, (1 - classification.confidence) * 100],
                        backgroundColor: ['#007bff', '#dee2e6']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: `Category: ${classification.category}`
                        }
                    }
                }
            });
        }

        function updateTopicsChart(topics) {
            const ctx = document.getElementById('topicsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: topics.map(t => t.tag),
                    datasets: [{
                        label: 'Score',
                        data: topics.map(t => t.score * 100),
                        backgroundColor: '#007bff'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        function updateKnowledgeGraph(graphData) {
            const width = document.getElementById('knowledge-graph').offsetWidth;
            const height = 600;

            // Clear existing graph
            d3.select('#knowledge-graph').html('');

            // Create SVG
            const svg = d3.select('#knowledge-graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            // Prepare data for D3
            const nodes = graphData.nodes.map(n => ({ id: n.id, label: n.text, type: n.type }));
            const links = graphData.edges.map(e => ({
                source: e.source,
                target: e.target,
                label: e.relation_type
            }));

            // Create force simulation
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(150))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));

            // Draw edges
            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-width', 2);

            // Draw edge labels
            const linkLabel = svg.append('g')
                .selectAll('text')
                .data(links)
                .enter().append('text')
                .text(d => d.label)
                .attr('font-size', 10)
                .attr('fill', '#666');

            // Draw nodes
            const node = svg.append('g')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('r', 10)
                .attr('fill', d => {
                    if (d.type === 'PERSON') return '#ff6b6b';
                    if (d.type === 'ORGANIZATION') return '#4ecdc4';
                    if (d.type === 'LOCATION') return '#95e1d3';
                    return '#999';
                })
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            // Draw node labels
            const nodeLabel = svg.append('g')
                .selectAll('text')
                .data(nodes)
                .enter().append('text')
                .text(d => d.label)
                .attr('font-size', 12)
                .attr('dx', 15)
                .attr('dy', 4);

            // Update positions on simulation tick
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                linkLabel
                    .attr('x', d => (d.source.x + d.target.x) / 2)
                    .attr('y', d => (d.source.y + d.target.y) / 2);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                nodeLabel
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });

            // Drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }
    </script>
</body>
</html>
"""


class DocumentDashboard:
    """Document analysis dashboard backend."""

    def __init__(self):
        """Initialize dashboard components."""
        self.parser = DocumentParser()
        self.ner_engine = NEREngine(use_spacy=True)
        self.classifier = TfidfSVMClassifier()
        self.relation_extractor = RelationExtractor(use_spacy=True)
        self.graph_builder = KnowledgeGraphBuilder(use_spacy=True)

        # Create upload directory
        os.makedirs("data/uploads", exist_ok=True)

        logger.info("DocumentDashboard initialized")

    def process_uploaded_file(self, file) -> Dict[str, Any]:
        """
        Process uploaded file and return analysis results.

        Args:
            file: Uploaded file object

        Returns:
            Analysis results dictionary
        """
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join("data/uploads", filename)
        file.save(filepath)

        logger.info(f"Processing uploaded file: {filename}")

        # Parse document
        parsed = self.parser.parse(filepath)
        text = parsed.get("text", "")

        # Extract entities
        entities = self.ner_engine.extract_entities(text)

        # Classify
        classification = self.classifier.predict(text)

        # Extract relations
        relations = self.relation_extractor.extract_relations(text)

        # Build knowledge graph
        graph = self.graph_builder.build_from_text(text)

        # Build results
        results = {
            "filename": filename,
            "processed_at": datetime.now().isoformat(),
            "statistics": {
                "text_length": len(text),
                "word_count": len(text.split()),
                "entity_count": len(entities),
                "relation_count": len(relations),
            },
            "classification": {
                "category": classification.category.value if hasattr(classification, "category") else "UNKNOWN",
                "confidence": getattr(classification, "confidence", 0.0),
            },
            "entities": [{"text": e.text, "type": e.type.value, "confidence": e.confidence} for e in entities],
            "topics": [],  # Placeholder for topic modeling
            "relations": [
                {
                    "source": r.source_entity,
                    "relation": r.relation_type.value,
                    "target": r.target_entity,
                    "confidence": r.confidence,
                }
                for r in relations
            ],
            "knowledge_graph": json.loads(graph.export(GraphFormat.JSON)),
        }

        return results


# Flask routes
if FLASK_AVAILABLE:
    dashboard = DocumentDashboard()

    @app.route("/")
    def index():
        """Render dashboard homepage."""
        return render_template_string(DASHBOARD_HTML)

    @app.route("/api/process", methods=["POST"])
    def process_document():
        """Process uploaded document."""
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        try:
            results = dashboard.process_uploaded_file(file)
            return jsonify(results)
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stats")
    def get_stats():
        """Get dashboard statistics."""
        # Placeholder - implement database queries
        return jsonify({"total_documents": 0, "total_entities": 0, "total_relations": 0})


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Document Analysis Dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if not FLASK_AVAILABLE:
        print("ERROR: Flask is required to run the dashboard")
        print("Install with: pip install flask flask-cors")
        return

    print(
        f"""
╔════════════════════════════════════════════════════════════════╗
║        Document Analysis Dashboard v1.0.0                      ║
╠════════════════════════════════════════════════════════════════╣
║  📊 Interactive document analysis and visualization            ║
║  🕸️  Knowledge graph explorer                                  ║
║  🔍 Entity and relation extraction                             ║
║  📈 Real-time analytics                                        ║
╠════════════════════════════════════════════════════════════════╣
║  Server: http://{args.host}:{args.port}
║  Mode: {'Production' if args.production else 'Development'}
╚════════════════════════════════════════════════════════════════╝
    """
    )

    # Run Flask server
    app.run(host=args.host, port=args.port, debug=args.debug and not args.production)


if __name__ == "__main__":
    main()
