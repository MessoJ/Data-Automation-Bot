"""
Database Manager for handling all database operations.

This module manages database connections, schema creation/updates,
and data operations for storing and retrieving processed data.
"""

import logging
from typing import Dict, List, Any, Optional
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from datetime import datetime

import config as config
from utils.helpers import handle_exceptions

# Define base model class
Base = declarative_base()

# Define data model
class ProcessedData(Base):
    """Model representing processed data in the database."""
    
    __tablename__ = "processed_data"
    
    id = sa.Column(sa.Integer, primary_key=True)
    source_id = sa.Column(sa.String(100), nullable=False, index=True)
    data_type = sa.Column(sa.String(50), nullable=False)
    value = sa.Column(sa.Float)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    data_metadata = sa.Column(sa.JSON)  # Renamed attribute
    processed_at = sa.Column(sa.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<ProcessedData(id={self.id}, source_id='{self.source_id}', type='{self.data_type}')>"

# Add more models as needed
class DataSource(Base):
    """Model representing data sources."""
    
    __tablename__ = "data_sources"
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    description = sa.Column(sa.Text)
    api_endpoint = sa.Column(sa.String(200))
    is_active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    last_updated = sa.Column(sa.DateTime, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}')>"

# --- New domain models to support competitive features ---

class Customer(Base):
    """Customer entity used for orders and loyalty program."""

    __tablename__ = "customers"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(120), nullable=False)
    email = sa.Column(sa.String(200), unique=True, index=True)
    phone = sa.Column(sa.String(50))
    loyalty_points = sa.Column(sa.Integer, default=0)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Warehouse(Base):
    """Represents a branch/warehouse."""

    __tablename__ = "warehouses"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(120), nullable=False)
    address = sa.Column(sa.String(250))
    city = sa.Column(sa.String(120))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=True)


class InventoryItem(Base):
    """Inventory item stored at a warehouse."""

    __tablename__ = "inventory_items"

    id = sa.Column(sa.Integer, primary_key=True)
    sku = sa.Column(sa.String(100), unique=True, index=True)
    name = sa.Column(sa.String(200), nullable=False)
    quantity = sa.Column(sa.Integer, default=0)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey("warehouses.id"))
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)


class Coupon(Base):
    """Coupon management for discounts."""

    __tablename__ = "coupons"

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(50), unique=True, nullable=False, index=True)
    name = sa.Column(sa.String(120))
    discount_type = sa.Column(sa.String(20), default="percent")  # percent|fixed
    amount = sa.Column(sa.Float, default=0.0)
    active = sa.Column(sa.Boolean, default=True)
    start_date = sa.Column(sa.DateTime)
    end_date = sa.Column(sa.DateTime)
    usage_count = sa.Column(sa.Integer, default=0)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=True)


class Order(Base):
    """Order entity with simple tracking fields."""

    __tablename__ = "orders"

    id = sa.Column(sa.Integer, primary_key=True)
    order_number = sa.Column(sa.String(50), unique=True, index=True)
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("customers.id"))
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey("warehouses.id"))
    status = sa.Column(sa.String(50), default="pending")
    total_amount = sa.Column(sa.Float, default=0.0)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=True)


class Driver(Base):
    """Delivery driver for order assignments."""

    __tablename__ = "drivers"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(120), nullable=False)
    phone = sa.Column(sa.String(50))
    status = sa.Column(sa.String(50), default="available")  # available|on_delivery|inactive
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class DeliveryAssignment(Base):
    """Assignment connecting a driver to an order with tracking fields."""

    __tablename__ = "delivery_assignments"

    id = sa.Column(sa.Integer, primary_key=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), index=True)
    driver_id = sa.Column(sa.Integer, sa.ForeignKey("drivers.id"), index=True)
    status = sa.Column(sa.String(50), default="assigned")  # assigned|picked_up|delivering|delivered|failed
    pickup_time = sa.Column(sa.DateTime)
    dropoff_time = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)


class Notification(Base):
    """In-app notifications center."""

    __tablename__ = "notifications"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(200), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    level = sa.Column(sa.String(20), default="info")  # info|success|warning|error
    is_read = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class LoyaltyTransaction(Base):
    """Loyalty program transactions (earn/redeem)."""

    __tablename__ = "loyalty_transactions"

    id = sa.Column(sa.Integer, primary_key=True)
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("customers.id"), index=True)
    points_change = sa.Column(sa.Integer, nullable=False)
    reason = sa.Column(sa.String(200))
    created_at = sa.Column(sa.DateTime, default=datetime.now)


# --- Commerce core to compete with storefront platforms ---
class Store(Base):
    __tablename__ = "stores"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(150), nullable=False)
    domain = sa.Column(sa.String(200), unique=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class Product(Base):
    __tablename__ = "products"
    id = sa.Column(sa.Integer, primary_key=True)
    sku = sa.Column(sa.String(100), unique=True, index=True)
    name = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text)
    price = sa.Column(sa.Float, default=0.0)
    currency = sa.Column(sa.String(10), default="USD")
    active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    category = sa.Column(sa.String(120))
    image_url = sa.Column(sa.String(500))
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = sa.Column(sa.Integer, primary_key=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), index=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey("products.id"), index=True)
    quantity = sa.Column(sa.Integer, default=1)
    unit_price = sa.Column(sa.Float, default=0.0)


class Payment(Base):
    __tablename__ = "payments"
    id = sa.Column(sa.Integer, primary_key=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), index=True)
    provider = sa.Column(sa.String(50), default="stripe")
    status = sa.Column(sa.String(50), default="created")
    amount = sa.Column(sa.Float, default=0.0)
    currency = sa.Column(sa.String(10), default="USD")
    payment_metadata = sa.Column(sa.JSON)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class CartItem(Base):
    __tablename__ = "cart_items"
    id = sa.Column(sa.Integer, primary_key=True)
    session_id = sa.Column(sa.String(64), index=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey("products.id"), index=True)
    quantity = sa.Column(sa.Integer, default=1)
    unit_price = sa.Column(sa.Float, default=0.0)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=True)

class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, conn_string: str = None):
        """
        Initialize the database manager.
        
        Args:
            conn_string: Database connection string. Defaults to config value.
        """
        self.conn_string = conn_string or config.DB_CONN_STRING
        self.engine = None
        self.Session = None
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize the SQLAlchemy engine and session factory."""
        logging.info(f"Initializing database with connection string: {self.conn_string}")
        
        # Ensure SQLite connection string format
        if self.conn_string.startswith('sqlite'):
            # Add check_same_thread=False for SQLite to work with Flask
            if '?' not in self.conn_string:
                self.conn_string += '?check_same_thread=False'
            logging.info(f"Using SQLite connection: {self.conn_string}")
        else:
            logging.info(f"Using database connection: {self.conn_string}")
            
        self.engine = sa.create_engine(self.conn_string)
        self.Session = sessionmaker(bind=self.engine)
        
    @contextmanager
    def get_session(self):
        """Get a database session using context manager for automatic cleanup."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    @handle_exceptions
    def initialize_database(self):
        """Create database tables if they don't exist."""
        logging.info("Initializing database schema")
        Base.metadata.create_all(self.engine)
        logging.info("Database schema initialized successfully")

    # --- Utility helpers for common operations ---
    def get_or_create_customer(self, email: str, name: str = "Guest"):
        """Fetch a customer by email or create a new one."""
        with self.get_session() as session:
            cust = None
            if email:
                cust = session.query(Customer).filter(Customer.email == email).first()
            if not cust:
                cust = Customer(name=name or "Guest", email=email)
                session.add(cust)
                session.flush()
            return cust

    def apply_coupon_to_amount(self, code: str, amount: float) -> Dict[str, Any]:
        """Apply a coupon to a cart/order amount and return calculation details."""
        now = datetime.now()
        with self.get_session() as session:
            coupon: Optional[Coupon] = (
                session.query(Coupon)
                .filter(Coupon.code == code, Coupon.active == True)
                .first()
            )
            if not coupon:
                return {"applied": False, "message": "Invalid or inactive coupon", "total": amount}
            if coupon.start_date and coupon.start_date > now:
                return {"applied": False, "message": "Coupon not yet active", "total": amount}
            if coupon.end_date and coupon.end_date < now:
                return {"applied": False, "message": "Coupon expired", "total": amount}

            discount = 0.0
            if coupon.discount_type == "percent":
                discount = min(amount, amount * (coupon.amount / 100.0))
            else:
                discount = min(amount, coupon.amount)

            new_total = round(max(0.0, amount - discount), 2)
            coupon.usage_count = (coupon.usage_count or 0) + 1
            session.add(coupon)
            return {
                "applied": True,
                "code": coupon.code,
                "discount": round(discount, 2),
                "total": new_total,
                "discount_type": coupon.discount_type,
            }

    # Products API helpers
    def create_product(self, data: Dict[str, Any], store_id: Optional[int] = None) -> int:
        with self.get_session() as session:
            product = Product(
                sku=data.get('sku'),
                name=data.get('name'),
                description=data.get('description'),
                price=float(data.get('price') or 0.0),
                currency=data.get('currency', 'USD'),
                active=bool(data.get('active', True)),
                category=data.get('category'),
                image_url=data.get('image_url'),
                store_id=store_id
            )
            session.add(product)
            session.flush()
            return product.id

    def list_products(self, limit: int = 200, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            query = session.query(Product)
            if store_id:
                query = query.filter(Product.store_id == store_id)
            items = query.order_by(Product.created_at.desc()).limit(limit).all()
            return [
                {
                    'id': p.id,
                    'sku': p.sku,
                    'name': p.name,
                    'description': p.description,
                    'price': p.price,
                    'currency': p.currency,
                    'active': p.active,
                    'category': p.category,
                    'image_url': p.image_url,
                } for p in items
            ]

    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            p = session.query(Product).get(product_id)
            if not p:
                return None
            return {
                'id': p.id,
                'sku': p.sku,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'currency': p.currency,
                'active': p.active,
            }

    def update_product(self, product_id: int, data: Dict[str, Any]) -> bool:
        with self.get_session() as session:
            p = session.query(Product).get(product_id)
            if not p:
                return False
            for key in ['sku', 'name', 'description', 'currency']:
                if key in data:
                    setattr(p, key, data[key])
            if 'price' in data:
                p.price = float(data['price'])
            if 'active' in data:
                p.active = bool(data['active'])
            session.add(p)
            return True

    def delete_product(self, product_id: int) -> bool:
        with self.get_session() as session:
            p = session.query(Product).get(product_id)
            if not p:
                return False
            session.delete(p)
            return True

    # Cart helpers
    def add_to_cart(self, session_id: str, product_id: int, qty: int = 1) -> None:
        with self.get_session() as session:
            product = session.query(Product).get(product_id)
            if not product:
                raise ValueError("Product not found")
            item = CartItem(session_id=session_id, product_id=product_id, quantity=qty, unit_price=product.price)
            session.add(item)

    def list_cart(self, session_id: str) -> Dict[str, Any]:
        with self.get_session() as session:
            rows = session.query(CartItem, Product).join(Product, CartItem.product_id == Product.id).filter(CartItem.session_id == session_id).all()
            items = []
            total = 0.0
            for item, prod in rows:
                line_total = (item.quantity or 1) * (item.unit_price or 0.0)
                total += line_total
                items.append({
                    'id': item.id,
                    'product_id': prod.id,
                    'name': prod.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'line_total': line_total
                })
            return {'items': items, 'total': round(total, 2)}

    def remove_cart_item(self, session_id: str, item_id: int) -> None:
        with self.get_session() as session:
            row = session.query(CartItem).filter(CartItem.session_id == session_id, CartItem.id == item_id).first()
            if row:
                session.delete(row)
    
    @handle_exceptions
    def store_data(self, data_records: List[Dict[str, Any]]):
        """
        Store processed data records in the database.
        
        Args:
            data_records: List of processed data records to store.
        """
        if not data_records:
            logging.warning("No data records to store")
            return
            
        logging.info(f"Storing {len(data_records)} records in database")
        
        # Convert dictionary records to ORM objects
        db_objects = []
        for record in data_records:
            db_obj = ProcessedData(
                source_id=record.get("source_id", "unknown"),
                data_type=record.get("data_type", "unknown"),
                value=record.get("value"),
                timestamp=record.get("timestamp", datetime.now()),
                data_metadata=record.get("metadata", {})
            )
            db_objects.append(db_obj)
        
        # Store in batches to avoid memory issues with large datasets
        batch_size = config.DATA_BATCH_SIZE
        with self.get_session() as session:
            for i in range(0, len(db_objects), batch_size):
                batch = db_objects[i:i + batch_size]
                session.add_all(batch)
                session.flush()
                logging.debug(f"Stored batch of {len(batch)} records")
        
        logging.info(f"Successfully stored {len(data_records)} records in database")
    
    @handle_exceptions
    def get_data(self, data_type: Optional[str] = None, 
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve data from the database with optional filtering.
        
        Args:
            data_type: Filter by data type.
            start_date: Filter by start date.
            end_date: Filter by end date.
            limit: Maximum number of records to return.
            
        Returns:
            List of data records as dictionaries.
        """
        with self.get_session() as session:
            query = session.query(ProcessedData)
            
            # Apply filters
            if data_type:
                query = query.filter(ProcessedData.data_type == data_type)
            if start_date:
                query = query.filter(ProcessedData.timestamp >= start_date)
            if end_date:
                query = query.filter(ProcessedData.timestamp <= end_date)
                
            # Apply limit and order
            query = query.order_by(ProcessedData.timestamp.desc()).limit(limit)
            
            # Execute query
            results = query.all()
            
            # Convert ORM objects to dictionaries
            data_records = []
            for result in results:
                data_records.append({
                    "id": result.id,
                    "source_id": result.source_id,
                    "data_type": result.data_type,
                    "value": result.value,
                    "timestamp": result.timestamp,
                    "metadata": result.data_metadata,
                    "processed_at": result.processed_at
                })
            
            return data_records
