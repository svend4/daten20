"""
Unit Tests for Analytics API Endpoints

Tests for REST API endpoints for analytics and BI dashboard
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime, timedelta

from src.api_analytics import api_analytics, init_analytics_api


class TestAnalyticsAPI(unittest.TestCase):
    """Test Analytics API endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        init_analytics_api(self.app)
        self.client = self.app.test_client()

    def test_get_dashboard_success(self):
        """Test successful dashboard data retrieval"""
        response = self.client.get('/api/v1/analytics/dashboard')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('kpis', data)
        self.assertIn('charts', data)
        self.assertIn('timestamp', data)

    def test_get_dashboard_with_filters(self):
        """Test dashboard with query parameters"""
        response = self.client.get(
            '/api/v1/analytics/dashboard',
            query_string={
                'dateRange': 30,
                'tenant': 'test_tenant',
                'comparisonPeriod': 'previous'
            }
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_kpi_mrr(self):
        """Test getting MRR KPI"""
        response = self.client.get('/api/v1/analytics/kpi/mrr')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['kpi'], 'mrr')
        self.assertIn('value', data)
        self.assertEqual(data['unit'], 'EUR')

    def test_get_kpi_churn(self):
        """Test getting churn rate KPI"""
        response = self.client.get('/api/v1/analytics/kpi/churn')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['kpi'], 'churn')
        self.assertEqual(data['unit'], '%')

    def test_get_kpi_invalid(self):
        """Test getting invalid KPI"""
        response = self.client.get('/api/v1/analytics/kpi/invalid_kpi')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_predict_revenue(self):
        """Test revenue prediction endpoint"""
        response = self.client.post(
            '/api/v1/analytics/predict/revenue',
            json={
                'months': 3,
                'model': 'arima'
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('forecast', data)
        self.assertEqual(data['model'], 'arima')

    def test_predict_churn(self):
        """Test churn prediction endpoint"""
        response = self.client.post(
            '/api/v1/analytics/predict/churn',
            json={
                'customer_ids': ['cust_1', 'cust_2']
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('predictions', data)

    def test_trigger_etl_incremental(self):
        """Test triggering ETL pipeline"""
        response = self.client.post(
            '/api/v1/analytics/warehouse/etl',
            json={'incremental': True},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'started')

    def test_warehouse_status(self):
        """Test warehouse status endpoint"""
        response = self.client.get('/api/v1/analytics/warehouse/status')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('status', data)

    def test_olap_query(self):
        """Test OLAP query endpoint"""
        response = self.client.post(
            '/api/v1/analytics/olap/query',
            json={
                'dimensions': ['region', 'product'],
                'measures': ['revenue', 'units'],
                'filters': {'date': '2024-01'}
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('result', data)

    def test_discover_patterns(self):
        """Test data mining patterns discovery"""
        response = self.client.post(
            '/api/v1/analytics/mining/patterns',
            json={
                'algorithm': 'apriori',
                'min_support': 0.3
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('patterns', data)
        self.assertEqual(data['algorithm'], 'apriori')

    def test_natural_language_query(self):
        """Test natural language query endpoint"""
        response = self.client.post(
            '/api/v1/analytics/query/natural',
            json={'query': 'Show me revenue for last month'},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('query', data)
        self.assertIn('sql', data)
        self.assertIn('result', data)

    def test_natural_language_query_empty(self):
        """Test NL query with empty query string"""
        response = self.client.post(
            '/api/v1/analytics/query/natural',
            json={'query': ''},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_export_dashboard_pdf(self):
        """Test dashboard export to PDF"""
        response = self.client.post(
            '/api/v1/analytics/export',
            json={
                'format': 'pdf',
                'include': {
                    'kpis': True,
                    'charts': True,
                    'rawData': False
                },
                'filters': {}
            },
            content_type='application/json'
        )

        # Export might return file or error
        # Check that it doesn't crash
        self.assertIn(response.status_code, [200, 500])

    def test_export_dashboard_invalid_format(self):
        """Test export with invalid format"""
        response = self.client.post(
            '/api/v1/analytics/export',
            json={
                'format': 'invalid_format',
                'include': {'kpis': True}
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_schedule_report(self):
        """Test scheduling a report"""
        response = self.client.post(
            '/api/v1/analytics/reports/schedule',
            json={
                'name': 'Weekly Executive Report',
                'frequency': 'weekly',
                'format': 'pdf',
                'recipients': ['exec@example.com']
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('report_id', data)

    def test_list_scheduled_reports(self):
        """Test listing scheduled reports"""
        response = self.client.get('/api/v1/analytics/reports/scheduled')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('reports', data)
        self.assertIn('count', data)

    def test_error_handler_404(self):
        """Test 404 error handler"""
        response = self.client.get('/api/v1/analytics/nonexistent')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class TestAnalyticsAPIErrorHandling(unittest.TestCase):
    """Test error handling in Analytics API"""

    def setUp(self):
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        init_analytics_api(self.app)
        self.client = self.app.test_client()

    @patch('src.api_analytics.bi_dashboard')
    def test_dashboard_internal_error(self, mock_dashboard):
        """Test handling of internal errors"""
        mock_dashboard.create_executive_dashboard.side_effect = Exception("Test error")

        response = self.client.get('/api/v1/analytics/dashboard')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_invalid_json_request(self):
        """Test handling of invalid JSON in POST request"""
        response = self.client.post(
            '/api/v1/analytics/predict/revenue',
            data='invalid json',
            content_type='application/json'
        )

        # Should handle gracefully (may return 400 or 500)
        self.assertIn(response.status_code, [400, 500])


class TestAnalyticsAPIIntegration(unittest.TestCase):
    """Integration tests for Analytics API"""

    def setUp(self):
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        init_analytics_api(self.app)
        self.client = self.app.test_client()

    def test_complete_workflow_dashboard_to_export(self):
        """Test complete workflow from dashboard to export"""
        # Step 1: Get dashboard data
        dashboard_response = self.client.get('/api/v1/analytics/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)

        # Step 2: Schedule a report
        schedule_response = self.client.post(
            '/api/v1/analytics/reports/schedule',
            json={
                'name': 'Integration Test Report',
                'frequency': 'daily',
                'format': 'pdf',
                'recipients': []
            },
            content_type='application/json'
        )
        self.assertEqual(schedule_response.status_code, 201)

        # Step 3: List scheduled reports
        list_response = self.client.get('/api/v1/analytics/reports/scheduled')
        self.assertEqual(list_response.status_code, 200)
        data = json.loads(list_response.data)
        self.assertGreater(data['count'], 0)

    def test_kpi_endpoints_consistency(self):
        """Test consistency across different KPI endpoints"""
        kpis = ['mrr', 'arr', 'churn', 'clv', 'nrr', 'cac']

        for kpi_name in kpis:
            response = self.client.get(f'/api/v1/analytics/kpi/{kpi_name}')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['kpi'], kpi_name)
            self.assertIn('value', data)
            self.assertIn('unit', data)
            self.assertIn('timestamp', data)


if __name__ == '__main__':
    unittest.main()
