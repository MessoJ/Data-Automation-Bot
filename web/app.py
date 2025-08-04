"""
Flask application factory and configuration.

This module creates and configures the Flask application for the 
Data Automation Bot web interface.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import json

# Import bot components
from database.db_manager import DatabaseManager
from reporting.report_generator import ReportGenerator
from scheduler.job_scheduler import JobScheduler
from api.api_client import APIClient
import config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Enable CORS for API endpoints
    CORS(app)
    
    # Initialize components
    db_manager = DatabaseManager()
    report_generator = ReportGenerator()
    job_scheduler = JobScheduler()
    api_client = APIClient()
    
    @app.route('/')
    def dashboard():
        """Main dashboard page."""
        return render_template('dashboard.html')
    
    @app.route('/api/status')
    def api_status():
        """Get system status and metrics."""
        try:
            # Get recent data count
            recent_data = db_manager.get_data(limit=100)
            
            # Get data from last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            recent_count = len(db_manager.get_data(start_date=yesterday, limit=10000))
            
            # Get scheduler status
            scheduler_running = job_scheduler.is_running()
            jobs = job_scheduler.get_jobs()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'connected': True,
                    'total_records': len(recent_data),
                    'recent_24h': recent_count
                },
                'scheduler': {
                    'running': scheduler_running,
                    'jobs_count': len(jobs),
                    'jobs': [{'id': job.id, 'next_run': job.next_run_time.isoformat() if job.next_run_time else None} for job in jobs]
                },
                'api': {
                    'base_url': config.API_BASE_URL,
                    'configured': bool(config.API_KEY)
                }
            }
            return jsonify(status)
        except Exception as e:
            logging.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/data')
    def api_data():
        """Get data records with optional filtering."""
        try:
            # Get query parameters
            data_type = request.args.get('type')
            limit = int(request.args.get('limit', 100))
            days = int(request.args.get('days', 7))
            
            # Calculate date range
            start_date = datetime.now() - timedelta(days=days)
            
            # Fetch data
            data = db_manager.get_data(
                data_type=data_type,
                start_date=start_date,
                limit=limit
            )
            
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
            logging.error(f"Error fetching data: {e}")
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
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by creation time, newest first
            reports.sort(key=lambda x: x['created'], reverse=True)
            
            return jsonify({'reports': reports})
        except Exception as e:
            logging.error(f"Error listing reports: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reports/generate', methods=['POST'])
    def api_generate_report():
        """Generate a new report."""
        try:
            data = request.get_json()
            report_type = data.get('type', 'daily')
            format_type = data.get('format', 'html')
            data_type_filter = data.get('data_type')
            
            if report_type == 'daily':
                report_path = report_generator.generate_daily_report(
                    data_type=data_type_filter,
                    report_format=format_type
                )
            elif report_type == 'weekly':
                report_path = report_generator.generate_weekly_report(
                    data_type=data_type_filter,
                    report_format=format_type
                )
            elif report_type == 'trend':
                days = data.get('days', 30)
                if not data_type_filter:
                    return jsonify({'error': 'data_type required for trend reports'}), 400
                report_path = report_generator.generate_trend_report(
                    data_type=data_type_filter,
                    days=days,
                    report_format=format_type
                )
            else:
                return jsonify({'error': 'Invalid report type'}), 400
            
            return jsonify({
                'success': True,
                'report_path': os.path.basename(report_path),
                'message': f'{report_type.title()} report generated successfully'
            })
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reports/download/<filename>')
    def api_download_report(filename):
        """Download a report file."""
        try:
            reports_dir = config.REPORT_OUTPUT_DIR
            filepath = os.path.join(reports_dir, filename)
            
            if not os.path.exists(filepath):
                return jsonify({'error': 'Report not found'}), 404
            
            return send_file(filepath, as_attachment=True)
        except Exception as e:
            logging.error(f"Error downloading report: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs')
    def api_jobs():
        """Get scheduled jobs information."""
        try:
            jobs = job_scheduler.get_jobs()
            job_list = []
            
            for job in jobs:
                job_info = {
                    'id': job.id,
                    'name': job.name or job.id,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                    'kwargs': job.kwargs,
                }
                job_list.append(job_info)
            
            return jsonify({
                'jobs': job_list,
                'scheduler_running': job_scheduler.is_running()
            })
        except Exception as e:
            logging.error(f"Error getting jobs: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs/<job_id>/pause', methods=['POST'])
    def api_pause_job(job_id):
        """Pause a scheduled job."""
        try:
            success = job_scheduler.pause_job(job_id)
            if success:
                return jsonify({'success': True, 'message': f'Job {job_id} paused'})
            else:
                return jsonify({'error': f'Failed to pause job {job_id}'}), 400
        except Exception as e:
            logging.error(f"Error pausing job: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/jobs/<job_id>/resume', methods=['POST'])
    def api_resume_job(job_id):
        """Resume a paused job."""
        try:
            success = job_scheduler.resume_job(job_id)
            if success:
                return jsonify({'success': True, 'message': f'Job {job_id} resumed'})
            else:
                return jsonify({'error': f'Failed to resume job {job_id}'}), 400
        except Exception as e:
            logging.error(f"Error resuming job: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config')
    def api_config():
        """Get configuration information (non-sensitive)."""
        try:
            config_info = {
                'api': {
                    'base_url': config.API_BASE_URL,
                    'timeout': config.API_TIMEOUT,
                    'configured': bool(config.API_KEY)
                },
                'database': {
                    'host': config.DB_HOST,
                    'port': config.DB_PORT,
                    'name': config.DB_NAME,
                    'user': config.DB_USER
                },
                'scheduler': {
                    'interval': config.SCHEDULER_INTERVAL,
                    'retry_attempts': config.RETRY_ATTEMPTS,
                    'retry_delay': config.RETRY_DELAY
                },
                'reporting': {
                    'output_dir': config.REPORT_OUTPUT_DIR,
                    'default_format': config.DEFAULT_REPORT_FORMAT
                }
            }
            return jsonify(config_info)
        except Exception as e:
            logging.error(f"Error getting config: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Additional routes for other pages
    @app.route('/reports')
    def reports_page():
        """Reports management page."""
        return render_template('reports.html')
    
    @app.route('/jobs')
    def jobs_page():
        """Jobs management page."""
        return render_template('jobs.html')
    
    @app.route('/config')
    def config_page():
        """Configuration page."""
        return render_template('config.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('error.html', error_code=404, error_message='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('error.html', error_code=500, error_message='Internal server error'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)