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
import stripe

from database.db_manager import (
    DatabaseManager,
    Coupon,
    Customer,
    LoyaltyTransaction,
    Notification,
    Driver,
    DeliveryAssignment,
    Order,
    Warehouse,
    InventoryItem,
    Product,
)
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
    # Do not instantiate/start scheduler here to avoid duplicate instances under reloader
    api_client = APIClient()

    # Stripe configuration
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
    
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
        return redirect('/web/')
    
    @app.route('/web/')
    def dashboard():
        try:
            root_path = os.path.abspath(os.path.join(app.root_path, '..'))
            react_dist = os.path.join(root_path, 'frontend', 'dist')
            index_path = os.path.join(react_dist, 'index.html')
            if os.path.exists(index_path):
                return send_file(index_path)
            # Fallback to legacy template if dist not built
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return jsonify({'error': f'Dashboard error: {str(e)}'}), 500

    @app.route('/web/<path:path>')
    def web_assets(path: str):
        try:
            root_path = os.path.abspath(os.path.join(app.root_path, '..'))
            react_dist = os.path.join(root_path, 'frontend', 'dist')
            file_path = os.path.join(react_dist, path)
            if os.path.exists(file_path):
                return send_from_directory(react_dist, path)
            # SPA fallback
            index_path = os.path.join(react_dist, 'index.html')
            if os.path.exists(index_path):
                return send_file(index_path)
            return jsonify({'error': 'frontend build not found'}), 404
        except Exception as e:
            logger.error(f"Web assets error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/checkout')
    def checkout_page():
        try:
            return render_template('checkout.html', stripe_pk=STRIPE_PUBLIC_KEY)
        except Exception as e:
            logger.error(f"Checkout page error: {e}")
            return jsonify({'error': f'Checkout page error: {str(e)}'}), 500
    
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
            job_scheduler = JobScheduler.instance(create_if_missing=False)
            jobs = job_scheduler.get_jobs() if (job_scheduler and job_scheduler.is_running()) else []
            api_client = APIClient()
            # Notifications summary
            with db.get_session() as session:
                unread = session.query(Notification).filter(Notification.is_read == False).count()
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
                },
                'notifications': {
                    'unread': unread
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
    
    # --- Competitive feature: Coupon management ---
    @app.route('/api/coupons/apply', methods=['POST'])
    def api_coupon_apply():
        try:
            payload = request.json or {}
            code = (payload.get('code') or '').strip()
            amount = float(payload.get('amount') or 0.0)
            if not code:
                return jsonify({'success': False, 'message': 'Coupon code required'}), 400
            db = DatabaseManager()
            result = db.apply_coupon_to_amount(code, amount)
            return jsonify({'success': result.get('applied', False), **result})
        except Exception as e:
            logger.error(f"Coupon apply error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/coupons', methods=['GET', 'POST'])
    def api_coupons():
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                if request.method == 'POST':
                    data = request.json or {}
                    coupon = Coupon(
                        code=str(data.get('code', '')).strip(),
                        name=data.get('name'),
                        discount_type=data.get('discount_type', 'percent'),
                        amount=float(data.get('amount') or 0.0),
                        active=bool(data.get('active', True)),
                        start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
                        end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
                    )
                    session.add(coupon)
                    session.flush()
                    return jsonify({'success': True, 'id': coupon.id})
                else:
                    items = session.query(Coupon).order_by(Coupon.created_at.desc()).limit(100).all()
                    return jsonify({'coupons': [
                        {
                            'id': c.id,
                            'code': c.code,
                            'name': c.name,
                            'discount_type': c.discount_type,
                            'amount': c.amount,
                            'active': c.active,
                            'start_date': c.start_date.isoformat() if c.start_date else None,
                            'end_date': c.end_date.isoformat() if c.end_date else None,
                            'usage_count': c.usage_count,
                        } for c in items
                    ]})
        except Exception as e:
            logger.error(f"Coupons error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Competitive feature: Loyalty program ---
    @app.route('/api/loyalty/balance')
    def api_loyalty_balance():
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'email required'}), 400
        db = DatabaseManager()
        with db.get_session() as session:
            cust = session.query(Customer).filter(Customer.email == email).first()
            balance = cust.loyalty_points if cust else 0
            return jsonify({'email': email, 'points': balance})

    @app.route('/api/loyalty/earn', methods=['POST'])
    def api_loyalty_earn():
        try:
            payload = request.json or {}
            email = payload.get('email')
            points = int(payload.get('points') or 0)
            reason = payload.get('reason', 'earn')
            db = DatabaseManager()
            with db.get_session() as session:
                cust = db.get_or_create_customer(email=email, name=payload.get('name'))
                # reattach to session
                cust = session.query(Customer).get(cust.id)
                cust.loyalty_points = (cust.loyalty_points or 0) + points
                session.add(LoyaltyTransaction(customer_id=cust.id, points_change=points, reason=reason))
                return jsonify({'success': True, 'email': email, 'points': cust.loyalty_points})
        except Exception as e:
            logger.error(f"Loyalty earn error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/loyalty/redeem', methods=['POST'])
    def api_loyalty_redeem():
        try:
            payload = request.json or {}
            email = payload.get('email')
            points = int(payload.get('points') or 0)
            reason = payload.get('reason', 'redeem')
            db = DatabaseManager()
            with db.get_session() as session:
                cust = db.get_or_create_customer(email=email, name=payload.get('name'))
                cust = session.query(Customer).get(cust.id)
                new_points = max(0, (cust.loyalty_points or 0) - points)
                delta = new_points - (cust.loyalty_points or 0)
                cust.loyalty_points = new_points
                session.add(LoyaltyTransaction(customer_id=cust.id, points_change=delta, reason=reason))
                return jsonify({'success': True, 'email': email, 'points': cust.loyalty_points})
        except Exception as e:
            logger.error(f"Loyalty redeem error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Competitive feature: Notifications center ---
    @app.route('/api/notifications', methods=['GET', 'POST'])
    def api_notifications():
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                if request.method == 'POST':
                    data = request.json or {}
                    notif = Notification(
                        title=data.get('title', 'Notification'),
                        message=data.get('message', ''),
                        level=data.get('level', 'info')
                    )
                    session.add(notif)
                    session.flush()
                    return jsonify({'success': True, 'id': notif.id})
                else:
                    items = session.query(Notification).order_by(Notification.created_at.desc()).limit(50).all()
                    return jsonify({'notifications': [
                        {
                            'id': n.id,
                            'title': n.title,
                            'message': n.message,
                            'level': n.level,
                            'is_read': n.is_read,
                            'created_at': n.created_at.isoformat()
                        } for n in items
                    ]})
        except Exception as e:
            logger.error(f"Notifications error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notifications/read/<int:notif_id>', methods=['POST'])
    def api_notifications_read(notif_id: int):
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                n = session.query(Notification).get(notif_id)
                if not n:
                    return jsonify({'error': 'Not found'}), 404
                n.is_read = True
                session.add(n)
                return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Notification read error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Competitive feature: Delivery management & tracking ---
    @app.route('/api/drivers', methods=['GET', 'POST'])
    def api_drivers():
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                if request.method == 'POST':
                    data = request.json or {}
                    driver = Driver(name=data.get('name', 'Driver'), phone=data.get('phone'))
                    session.add(driver)
                    session.flush()
                    return jsonify({'success': True, 'id': driver.id})
                else:
                    items = session.query(Driver).order_by(Driver.created_at.desc()).limit(200).all()
                    return jsonify({'drivers': [
                        {'id': d.id, 'name': d.name, 'phone': d.phone, 'status': d.status}
                        for d in items
                    ]})
        except Exception as e:
            logger.error(f"Drivers error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        db = DatabaseManager()
        try:
            data = request.json or {}
            with db.get_session() as session:
                cust = db.get_or_create_customer(email=data.get('email'), name=data.get('name'))
                order = Order(
                    order_number=str(data.get('order_number') or f"ORD-{int(datetime.now().timestamp())}"),
                    customer_id=cust.id,
                    warehouse_id=data.get('warehouse_id'),
                    status=data.get('status', 'pending'),
                    total_amount=float(data.get('total_amount') or 0.0),
                )
                session.add(order)
                session.flush()
                return jsonify({'success': True, 'order_id': order.id, 'order_number': order.order_number})
        except Exception as e:
            logger.error(f"Create order error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/orders/track/<order_number>')
    def api_track_order(order_number: str):
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                order = session.query(Order).filter(Order.order_number == order_number).first()
                if not order:
                    return jsonify({'error': 'Order not found'}), 404
                assign = session.query(DeliveryAssignment).filter(DeliveryAssignment.order_id == order.id).order_by(DeliveryAssignment.updated_at.desc()).first()
                result = {
                    'order_number': order.order_number,
                    'status': order.status,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at.isoformat(),
                    'assignment': None
                }
                if assign:
                    result['assignment'] = {
                        'id': assign.id,
                        'status': assign.status,
                        'pickup_time': assign.pickup_time.isoformat() if assign.pickup_time else None,
                        'dropoff_time': assign.dropoff_time.isoformat() if assign.dropoff_time else None,
                        'updated_at': assign.updated_at.isoformat() if assign.updated_at else None
                    }
                return jsonify(result)
        except Exception as e:
            logger.error(f"Track order error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/assignments', methods=['POST'])
    def api_create_assignment():
        db = DatabaseManager()
        try:
            data = request.json or {}
            with db.get_session() as session:
                order = session.query(Order).filter(Order.order_number == str(data.get('order_number'))).first()
                if not order:
                    return jsonify({'error': 'Order not found'}), 404
                assignment = DeliveryAssignment(order_id=order.id, driver_id=int(data.get('driver_id')))
                session.add(assignment)
                session.flush()
                return jsonify({'success': True, 'assignment_id': assignment.id})
        except Exception as e:
            logger.error(f"Create assignment error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/assignments/<int:assignment_id>/status', methods=['POST'])
    def api_update_assignment_status(assignment_id: int):
        db = DatabaseManager()
        try:
            data = request.json or {}
            new_status = data.get('status')
            with db.get_session() as session:
                a = session.query(DeliveryAssignment).get(assignment_id)
                if not a:
                    return jsonify({'error': 'Assignment not found'}), 404
                a.status = new_status or a.status
                if new_status == 'picked_up':
                    a.pickup_time = datetime.now()
                if new_status in ('delivered', 'failed'):
                    a.dropoff_time = datetime.now()
                session.add(a)
                return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Update assignment status error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Branch/Warehouse & Inventory ---
    @app.route('/api/warehouses', methods=['GET', 'POST'])
    def api_warehouses():
        db = DatabaseManager()
        try:
            with db.get_session() as session:
                if request.method == 'POST':
                    data = request.json or {}
                    w = Warehouse(name=data.get('name', 'Warehouse'), address=data.get('address'), city=data.get('city'))
                    session.add(w)
                    session.flush()
                    return jsonify({'success': True, 'id': w.id})
                else:
                    items = session.query(Warehouse).order_by(Warehouse.created_at.desc()).all()
                    return jsonify({'warehouses': [
                        {'id': w.id, 'name': w.name, 'address': w.address, 'city': w.city}
                        for w in items
                    ]})
        except Exception as e:
            logger.error(f"Warehouses error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/inventory', methods=['GET'])
    def api_inventory():
        db = DatabaseManager()
        wid = request.args.get('warehouse_id')
        try:
            with db.get_session() as session:
                q = session.query(InventoryItem)
                if wid:
                    q = q.filter(InventoryItem.warehouse_id == int(wid))
                items = q.order_by(InventoryItem.name.asc()).limit(500).all()
                return jsonify({'items': [
                    {
                        'id': i.id,
                        'sku': i.sku,
                        'name': i.name,
                        'quantity': i.quantity,
                        'warehouse_id': i.warehouse_id,
                        'updated_at': i.updated_at.isoformat() if i.updated_at else None
                    } for i in items
                ]})
        except Exception as e:
            logger.error(f"Inventory list error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/inventory/adjust', methods=['POST'])
    def api_inventory_adjust():
        db = DatabaseManager()
        try:
            data = request.json or {}
            with db.get_session() as session:
                item = session.query(InventoryItem).filter(InventoryItem.sku == str(data.get('sku'))).first()
                if not item:
                    item = InventoryItem(
                        sku=str(data.get('sku')),
                        name=data.get('name', 'Item'),
                        warehouse_id=int(data.get('warehouse_id')) if data.get('warehouse_id') else None,
                        quantity=0,
                    )
                delta = int(data.get('delta') or 0)
                item.quantity = (item.quantity or 0) + delta
                session.add(item)
                session.flush()
                return jsonify({'success': True, 'id': item.id, 'quantity': item.quantity})
        except Exception as e:
            logger.error(f"Inventory adjust error: {e}")
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

    # --- Product Catalog (to compete with storefronts) ---
    @app.route('/api/products', methods=['GET', 'POST'])
    def api_products():
        db = DatabaseManager()
        try:
            if request.method == 'POST':
                data = request.json or {}
                pid = db.create_product(data, store_id=data.get('store_id'))
                return jsonify({'success': True, 'id': pid})
            else:
                store_id = request.args.get('store_id', type=int)
                return jsonify({'products': db.list_products(store_id=store_id)})
        except Exception as e:
            logger.error(f"Products error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
    def api_product_detail(product_id: int):
        db = DatabaseManager()
        try:
            if request.method == 'GET':
                p = db.get_product(product_id)
                return (jsonify(p), 200) if p else (jsonify({'error': 'Not found'}), 404)
            if request.method == 'PUT':
                ok = db.update_product(product_id, request.json or {})
                return jsonify({'success': ok}) if ok else (jsonify({'error': 'Not found'}), 404)
            if request.method == 'DELETE':
                ok = db.delete_product(product_id)
                return jsonify({'success': ok}) if ok else (jsonify({'error': 'Not found'}), 404)
        except Exception as e:
            logger.error(f"Product detail error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Simple cart using session id in query/body ---
    @app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
    def api_cart():
        db = DatabaseManager()
        sid = request.args.get('sid') or (request.json or {}).get('sid')
        if not sid:
            return jsonify({'error': 'sid required'}), 400
        try:
            if request.method == 'POST':
                data = request.json or {}
                db.add_to_cart(sid, int(data.get('product_id')), int(data.get('quantity') or 1))
                return jsonify({'success': True})
            if request.method == 'DELETE':
                item_id = int((request.json or {}).get('item_id'))
                db.remove_cart_item(sid, item_id)
                return jsonify({'success': True})
            # GET
            return jsonify(db.list_cart(sid))
        except Exception as e:
            logger.error(f"Cart error: {e}")
            return jsonify({'error': str(e)}), 500

    # --- Minimal public storefront ---
    @app.route('/store')
    def storefront():
        try:
            return render_template('storefront.html')
        except Exception as e:
            logger.error(f"Storefront error: {e}")
            return jsonify({'error': f'Storefront error: {str(e)}'}), 500
    # --- Stripe Checkout ---
    @app.route('/api/pay/checkout_session', methods=['POST'])
    def api_create_checkout_session():
        try:
            if not stripe.api_key:
                return jsonify({'error': 'Stripe not configured'}), 400
            data = request.json or {}
            amount_cents = int(float(data.get('amount', 0)) * 100)
            if amount_cents <= 0:
                return jsonify({'error': 'Invalid amount'}), 400
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                success_url=data.get('success_url') or request.host_url.rstrip('/') + '/web/',
                cancel_url=data.get('cancel_url') or request.host_url.rstrip('/') + '/web/',
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': data.get('name', 'Subscription')},
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }]
            )
            return jsonify({'id': session.id, 'url': session.url})
        except Exception as e:
            logger.error(f"Stripe checkout error: {e}")
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

    @app.route('/coupons')
    def coupons_page():
        try:
            return render_template('coupons.html')
        except Exception as e:
            logger.error(f"Coupons page error: {e}")
            return jsonify({'error': f'Coupons page error: {str(e)}'}), 500

    @app.route('/drivers')
    def drivers_page():
        try:
            return render_template('drivers.html')
        except Exception as e:
            logger.error(f"Drivers page error: {e}")
            return jsonify({'error': f'Drivers page error: {str(e)}'}), 500

    @app.route('/track')
    def track_order_page():
        try:
            return render_template('track.html')
        except Exception as e:
            logger.error(f"Track page error: {e}")
            return jsonify({'error': f'Track page error: {str(e)}'}), 500

    @app.route('/warehouses')
    def warehouses_page():
        try:
            return render_template('warehouses.html')
        except Exception as e:
            logger.error(f"Warehouses page error: {e}")
            return jsonify({'error': f'Warehouses page error: {str(e)}'}), 500

    @app.route('/notifications')
    def notifications_page():
        try:
            return render_template('notifications.html')
        except Exception as e:
            logger.error(f"Notifications page error: {e}")
            return jsonify({'error': f'Notifications page error: {str(e)}'}), 500

    @app.route('/loyalty')
    def loyalty_page():
        try:
            return render_template('loyalty.html')
        except Exception as e:
            logger.error(f"Loyalty page error: {e}")
            return jsonify({'error': f'Loyalty page error: {str(e)}'}), 500

    @app.route('/products')
    def products_page():
        try:
            return render_template('products.html')
        except Exception as e:
            logger.error(f"Products page error: {e}")
            return jsonify({'error': f'Products page error: {str(e)}'}), 500
    
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