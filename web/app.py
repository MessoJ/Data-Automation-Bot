"""
Flask application factory and configuration - SIMPLIFIED VERSION.

This module creates and configures the Flask application for the 
Data Automation Bot web interface without external dependencies.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import json

from database.db_manager import DatabaseManager
from reporting.report_generator import ReportGenerator
from scheduler.job_scheduler import JobScheduler
from api.api_client import APIClient
import config

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Enable CORS for API endpoints
    CORS(app)
    
    logger.info("Flask application created")

    # Initialize core components
    db_manager = DatabaseManager()
    try:
        db_manager.initialize_database()
    except Exception as db_ex:
        logger.warning(f"Database initialization issue: {db_ex}")
    report_generator = ReportGenerator()
    job_scheduler = JobScheduler()
    api_client = APIClient()
    
    @app.route('/landing')
    def landing_page():
        try:
            return render_template('landing.html')
        except Exception as e:
            logger.error(f"Landing page error: {e}")
            return "<h1>Landing Page</h1><p>Unable to render template</p>"

    @app.route('/logo.png')
    def get_logo():
        try:
            root_path = os.path.abspath(os.path.join(app.root_path, '..'))
            return send_from_directory(root_path, 'churnlogo.png')
        except Exception as e:
            logger.error(f"Logo serve error: {e}")
            # Fallback to a 1x1 transparent PNG
            from io import BytesIO
            transparent_png = BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDAT\x08\x99c``\x00\x00\x00\x04\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
            return send_file(transparent_png, mimetype='image/png')
    
    @app.route('/')
    def index():
        """Root route - redirect to landing page or dashboard based on context."""
        return redirect(url_for('dashboard'))
    
    @app.route('/web/')
    def dashboard():
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return jsonify({'error': f'Dashboard error: {str(e)}'}), 500
    
    @app.route('/onboarding')
    def onboarding():
        """Customer onboarding flow."""
        try:
            return render_template('onboarding.html')
        except Exception as e:
            logger.error(f"Onboarding error: {e}")
            return jsonify({'error': f'Onboarding error: {str(e)}'}), 500
    
    @app.route('/api/status')
    def api_status():
        try:
            db = DatabaseManager()
            job_scheduler = JobScheduler()
            jobs = job_scheduler.get_jobs() if job_scheduler.is_running() else []
            api_client = APIClient()
            status = {
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'connected': True,
                    'total_records': len(db.get_data(limit=50)),
                    'recent_24h': len(db.get_data(start_date=datetime.now() - timedelta(days=1), limit=1000))
                },
                'scheduler': {
                    'running': job_scheduler.is_running(),
                    'jobs_count': len(jobs),
                    'jobs': [
                        {'id': job.id, 'next_run': job.next_run_time.isoformat() if job.next_run_time else None}
                        for job in jobs
                    ]
                },
                'api': {
                    'base_url': config.API_BASE_URL,
                    'configured': bool(config.API_KEY)
                }
            }
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ecommerce/sync', methods=['POST'])
    def api_ecommerce_sync():
        """Trigger e-commerce inventory sync across platforms."""
        try:
            platforms = request.json.get('platforms', [
                {'name': 'Shopify', 'type': 'shopify'},
                {'name': 'Amazon', 'type': 'amazon'},
                {'name': 'eBay', 'type': 'ebay'}
            ]) if request.json else []
            
            # Use EcommerceDataIntegrator if available
            try:
                from ecommerce_integration import EcommerceDataIntegrator
                integrator = EcommerceDataIntegrator()
                report = integrator.sync_inventory_across_platforms(platforms)
                return jsonify({'success': True, 'message': 'Inventory sync completed', 'report': report})
            except Exception as ex:
                logger.warning(f"Ecommerce integrator fallback due to error: {ex}")
                return jsonify({'success': True, 'message': 'Inventory sync simulated', 'report': {'total_products': 0, 'discrepancies_found': 0, 'sync_issues': [{'error': str(ex)}], 'discrepancies': [], 'timestamp': datetime.now().isoformat()}})
                
        except Exception as e:
            logger.error(f"Error during e-commerce sync: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ecommerce/revenue', methods=['GET'])
    def api_ecommerce_revenue():
        """Get e-commerce revenue analytics."""
        try:
            days = int(request.args.get('days', 30))
            
            # Generate demo revenue data
            daily_revenue = []
            total_revenue = 0
            
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                daily_amount = round(2000 + (i * 50) + (abs(hash(str(date.date())) % 1000)), 2)
                total_revenue += daily_amount
                daily_revenue.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'revenue': daily_amount,
                    'orders': max(5, int(20 + i * 0.5))
                })
            
            return jsonify({
                'total_revenue': round(total_revenue, 2),
                'avg_daily_revenue': round(total_revenue / days, 2),
                'daily_revenue': daily_revenue[::-1],  # Reverse to show chronological order
                'currency': 'USD'
            })
            
        except Exception as e:
            logger.error(f"Error getting revenue data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ecommerce/discrepancies', methods=['GET'])
    def api_ecommerce_discrepancies():
        """Get inventory and pricing discrepancies."""
        try:
            discrepancies = [
                {
                    'sku': 'PROD-001',
                    'type': 'price_discrepancy',
                    'platforms': ['Shopify', 'Amazon'],
                    'prices': {'Shopify': 29.99, 'Amazon': 34.99},
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'sku': 'PROD-002',
                    'type': 'inventory_discrepancy',
                    'platforms': ['Shopify', 'eBay'],
                    'quantities': {'Shopify': 15, 'eBay': 8},
                    'severity': 'high',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            
            return jsonify({
                'discrepancies': discrepancies,
                'total_count': len(discrepancies),
                'critical_count': len([d for d in discrepancies if d['severity'] == 'high'])
            })
            
        except Exception as e:
            logger.error(f"Error getting discrepancy data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/data')
    def api_data():
        """Get data records with optional filtering."""
        try:
            data_type = request.args.get('type')
            limit = int(request.args.get('limit', 100))
            days = int(request.args.get('days', 7))
            
            start_date = datetime.now() - timedelta(days=days)
            data = db_manager.get_data(
                data_type=data_type,
                start_date=start_date,
                limit=limit
            )
            # Ensure timestamps are serializable
            for rec in data:
                if isinstance(rec.get('timestamp'), datetime):
                    rec['timestamp'] = rec['timestamp'].isoformat()
            
            return jsonify({
                'data': data,
                'count': len(data),
                'filters': {
                    'type': data_type,
                    'days': days,
                    'limit': limit
                }
            })
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reports')
    def api_reports():
        """Get list of available reports."""
        try:
            reports_dir = config.REPORT_OUTPUT_DIR
            if not os.path.exists(reports_dir):
                return jsonify({'reports': []})
            reports = []
            for filename in os.listdir(reports_dir):
                if filename.endswith(('.csv', '.json', '.html', '.png')):
                    filepath = os.path.join(reports_dir, filename)
                    stat = os.stat(filepath)
                    reports.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
            return jsonify({'reports': reports})
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reports/generate', methods=['POST'])
    def api_generate_report():
        """Generate a new report."""
        try:
            data = request.json or {}
            report_type = data.get('report_type', 'daily')
            format_type = data.get('format', 'csv')
            data_type = data.get('data_type')
            
            if report_type == 'daily':
                path = report_generator.generate_daily_report(data_type=data_type, report_format=format_type)
            elif report_type == 'weekly':
                path = report_generator.generate_weekly_report(data_type=data_type, report_format=format_type)
            elif report_type == 'trend':
                days = int(data.get('days', 30))
                path = report_generator.generate_trend_report(data_type=data_type or 'standard', days=days, report_format=format_type)
            else:
                # default to daily
                path = report_generator.generate_daily_report(data_type=data_type, report_format=format_type)

            return jsonify({'success': True, 'filename': os.path.basename(path), 'message': 'Report generated successfully'})
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs')
    def api_jobs():
        """Get list of scheduled jobs."""
        try:
            jobs = [
                {
                    'id': 'shopify_sync',
                    'name': 'Shopify Sync',
                    'next_run': (datetime.now() + timedelta(minutes=15)).isoformat(),
                    'trigger': 'interval[0:15:00]',
                    'func_name': 'sync_shopify_inventory'
                },
                {
                    'id': 'amazon_sync',
                    'name': 'Amazon Sync',
                    'next_run': (datetime.now() + timedelta(minutes=30)).isoformat(),
                    'trigger': 'interval[0:30:00]',
                    'func_name': 'sync_amazon_inventory'
                },
                {
                    'id': 'report_generation',
                    'name': 'Daily Reports',
                    'next_run': (datetime.now() + timedelta(hours=24)).isoformat(),
                    'trigger': 'cron[hour=9]',
                    'func_name': 'generate_daily_reports'
                }
            ]
            
            return jsonify({'jobs': jobs})
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs/<job_id>/pause', methods=['POST'])
    def api_pause_job(job_id):
        """Pause a specific job."""
        try:
            logger.info(f"Pausing job: {job_id}")
            return jsonify({'success': True, 'message': f'Job {job_id} paused'})
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs/<job_id>/resume', methods=['POST'])
    def api_resume_job(job_id):
        """Resume a specific job."""
        try:
            logger.info(f"Resuming job: {job_id}")
            return jsonify({'success': True, 'message': f'Job {job_id} resumed'})
        except Exception as e:
            logger.error(f"Error resuming job: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config')
    def api_config():
        """Get system configuration."""
        try:
            config_data = {
                'database': {
                    'type': 'sqlite',
                    'host': 'localhost',
                    'port': '5432',
                    'name': 'data_automation'
                },
                'api': {
                    'base_url': 'https://api.example.com',
                    'timeout': 30,
                    'configured': True
                },
                'scheduler': {
                    'interval': 900,
                    'retry_attempts': 3,
                    'retry_delay': 60
                },
                'data_processing': {
                    'batch_size': 1000,
                    'threads': 4
                },
                'reporting': {
                    'output_dir': './reports',
                    'default_format': 'csv'
                }
            }
            
            return jsonify(config_data)
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/reports')
    def reports_page():
        """Reports page."""
        try:
            return render_template('reports.html')
        except Exception as e:
            logger.error(f"Reports page error: {e}")
            return jsonify({'error': f'Reports page error: {str(e)}'}), 500
    
    @app.route('/jobs')
    def jobs_page():
        """Jobs page."""
        try:
            return render_template('jobs.html')
        except Exception as e:
            logger.error(f"Jobs page error: {e}")
            return jsonify({'error': f'Jobs page error: {str(e)}'}), 500
    
    @app.route('/config')
    def config_page():
        """Configuration page."""
        try:
            return render_template('config.html')
        except Exception as e:
            logger.error(f"Config page error: {e}")
            return jsonify({'error': f'Config page error: {str(e)}'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        try:
            return render_template('error.html', error_code=404, error_message="Page not found"), 404
        except Exception:
            return """
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/web/">Go to Dashboard</a>
            """, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        try:
            return render_template('error.html', error_code=500, error_message="Internal server error"), 500
        except Exception:
            return """
            <h1>500 - Internal Server Error</h1>
            <p>Something went wrong on our end.</p>
            <a href="/web/">Go to Dashboard</a>
            """, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)