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
    theme_key = sa.Column(sa.String(50), default="default")
    settings = sa.Column(sa.JSON)


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


# --- New auth and rules models ---
class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(200), unique=True, index=True, nullable=False)
    password_hash = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class StoreUser(Base):
    __tablename__ = "store_users"
    id = sa.Column(sa.Integer, primary_key=True)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), index=True, nullable=False)
    role = sa.Column(sa.String(20), default="staff")  # owner|admin|staff
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class DiscountRule(Base):
    __tablename__ = "discount_rules"
    id = sa.Column(sa.Integer, primary_key=True)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=False)
    rule_type = sa.Column(sa.String(20), nullable=False)  # category|product
    target_value = sa.Column(sa.String(120), nullable=False)  # category name or product id as string
    discount_type = sa.Column(sa.String(20), default="percent")  # percent|fixed
    amount = sa.Column(sa.Float, default=0.0)
    active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"
    id = sa.Column(sa.Integer, primary_key=True)
    store_id = sa.Column(sa.Integer, sa.ForeignKey("stores.id"), index=True, nullable=False)
    name = sa.Column(sa.String(120), nullable=False)
    method_type = sa.Column(sa.String(30), default="flat_rate")  # flat_rate|free_over
    rate = sa.Column(sa.Float, default=0.0)
    threshold = sa.Column(sa.Float)  # used for free_over
    provider = sa.Column(sa.String(50))  # placeholder for provider hooks
    active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)

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
    def add_to_cart(self, session_id: str, product_id: int, qty: int = 1, store_id: Optional[int] = None) -> None:
        with self.get_session() as session:
            product = session.query(Product).get(product_id)
            if not product:
                raise ValueError("Product not found")
            item = CartItem(
                session_id=session_id,
                product_id=product_id,
                quantity=qty,
                unit_price=product.price,
                store_id=store_id or product.store_id,
            )
            session.add(item)

    def _calculate_discounts(self, session, store_id: Optional[int], cart_rows: List[Any]) -> Dict[str, Any]:
        discount_total = 0.0
        breakdown: List[Dict[str, Any]] = []
        if not store_id:
            return {"discount_total": 0.0, "breakdown": []}
        rules = (
            session.query(DiscountRule)
            .filter(DiscountRule.store_id == store_id, DiscountRule.active == True)
            .all()
        )
        # Build product lookup
        for item, prod in cart_rows:
            line_total = (item.quantity or 1) * (item.unit_price or 0.0)
            applicable = []
            for r in rules:
                if r.rule_type == "category" and prod.category and prod.category == r.target_value:
                    applicable.append(r)
                elif r.rule_type == "product" and str(prod.id) == str(r.target_value):
                    applicable.append(r)
            for r in applicable:
                if r.discount_type == "percent":
                    d = line_total * (r.amount / 100.0)
                else:
                    d = min(line_total, r.amount)
                if d > 0:
                    discount_total += d
                    breakdown.append({
                        "rule_id": r.id,
                        "type": r.rule_type,
                        "target": r.target_value,
                        "amount": round(d, 2),
                    })
        return {"discount_total": round(discount_total, 2), "breakdown": breakdown}

    def _calculate_shipping(self, session, store_id: Optional[int], subtotal_after_discounts: float) -> Dict[str, Any]:
        if not store_id:
            return {"shipping": 0.0, "method": None}
        method = (
            session.query(ShippingMethod)
            .filter(ShippingMethod.store_id == store_id, ShippingMethod.active == True)
            .order_by(ShippingMethod.created_at.asc())
            .first()
        )
        if not method:
            return {"shipping": 0.0, "method": None}
        shipping_cost = 0.0
        if method.method_type == "flat_rate":
            shipping_cost = method.rate or 0.0
        elif method.method_type == "free_over":
            threshold = method.threshold or 0.0
            if subtotal_after_discounts >= threshold:
                shipping_cost = 0.0
            else:
                shipping_cost = method.rate or 0.0
        return {"shipping": round(shipping_cost, 2), "method": {
            "id": method.id,
            "name": method.name,
            "type": method.method_type,
            "rate": method.rate,
            "threshold": method.threshold,
            "provider": method.provider,
        }}

    def list_cart(self, session_id: str, store_id: Optional[int] = None, apply_discounts: bool = True, include_shipping: bool = True) -> Dict[str, Any]:
        with self.get_session() as session:
            q = (
                session.query(CartItem, Product)
                .join(Product, CartItem.product_id == Product.id)
                .filter(CartItem.session_id == session_id)
            )
            if store_id:
                q = q.filter(CartItem.store_id == store_id)
            rows = q.all()
            items = []
            subtotal = 0.0
            for item, prod in rows:
                line_total = (item.quantity or 1) * (item.unit_price or 0.0)
                subtotal += line_total
                items.append({
                    'id': item.id,
                    'product_id': prod.id,
                    'name': prod.name,
                    'category': prod.category,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'line_total': round(line_total, 2)
                })
            discounts_total = 0.0
            discount_breakdown: List[Dict[str, Any]] = []
            if apply_discounts and rows:
                disc = self._calculate_discounts(session, store_id, rows)
                discounts_total = disc["discount_total"]
                discount_breakdown = disc["breakdown"]
            subtotal_after_discounts = max(0.0, subtotal - discounts_total)
            shipping_cost = 0.0
            shipping_method = None
            if include_shipping and rows:
                ship = self._calculate_shipping(session, store_id, subtotal_after_discounts)
                shipping_cost = ship["shipping"]
                shipping_method = ship["method"]
            grand_total = round(subtotal_after_discounts + shipping_cost, 2)
            return {
                'items': items,
                'subtotal': round(subtotal, 2),
                'discounts_total': round(discounts_total, 2),
                'discounts': discount_breakdown,
                'shipping': round(shipping_cost, 2),
                'shipping_method': shipping_method,
                'total': grand_total,
            }

    def remove_cart_item(self, session_id: str, item_id: int) -> None:
        with self.get_session() as session:
            row = session.query(CartItem).filter(CartItem.session_id == session_id, CartItem.id == item_id).first()
            if row:
                session.delete(row)

    def clear_cart(self, session_id: str, store_id: Optional[int] = None) -> None:
        with self.get_session() as session:
            q = session.query(CartItem).filter(CartItem.session_id == session_id)
            if store_id:
                q = q.filter(CartItem.store_id == store_id)
            for row in q.all():
                session.delete(row)

    # Store helpers
    def create_store(self, name: str, domain: Optional[str] = None, theme_key: str = "default", settings: Optional[Dict[str, Any]] = None) -> int:
        with self.get_session() as session:
            store = Store(name=name, domain=domain, theme_key=theme_key, settings=settings or {})
            session.add(store)
            session.flush()
            return store.id

    def list_stores(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            items = session.query(Store).order_by(Store.created_at.desc()).limit(limit).all()
            return [
                {
                    'id': s.id,
                    'name': s.name,
                    'domain': s.domain,
                    'theme_key': s.theme_key,
                    'created_at': s.created_at.isoformat(),
                } for s in items
            ]

    def get_store_by_id_or_domain(self, identifier: str) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            store = None
            if identifier.isdigit():
                store = session.query(Store).get(int(identifier))
            else:
                store = session.query(Store).filter(Store.domain == identifier).first()
            if not store:
                return None
            return {
                'id': store.id,
                'name': store.name,
                'domain': store.domain,
                'theme_key': store.theme_key or 'default',
                'created_at': store.created_at.isoformat(),
            }

    def update_store(self, store_id: int, data: Dict[str, Any]) -> bool:
        with self.get_session() as session:
            s = session.query(Store).get(store_id)
            if not s:
                return False
            for k in ['name', 'domain', 'theme_key']:
                if k in data:
                    setattr(s, k, data[k])
            if 'settings' in data and isinstance(data['settings'], dict):
                s.settings = (s.settings or {})
                s.settings.update(data['settings'])
            session.add(s)
            return True

    # Order helpers
    def create_order_from_cart(self, session_id: str, store_id: int, email: Optional[str], name: Optional[str] = None) -> Optional[int]:
        with self.get_session() as session:
            # Compute cart
            q = (
                session.query(CartItem, Product)
                .join(Product, CartItem.product_id == Product.id)
                .filter(CartItem.session_id == session_id, CartItem.store_id == store_id)
            )
            rows = q.all()
            if not rows:
                return None
            # Customer
            cust = None
            if email:
                cust = session.query(Customer).filter(Customer.email == email).first()
            if not cust:
                cust = Customer(name=name or "Guest", email=email)
                session.add(cust)
                session.flush()
            # Warehouse selection (first for store)
            wh = (
                session.query(Warehouse)
                .filter(Warehouse.store_id == store_id)
                .order_by(Warehouse.created_at.asc())
                .first()
            )
            # Totals
            subtotal = sum((item.quantity or 1) * (item.unit_price or 0.0) for item, _ in rows)
            # Discounts
            discounts_info = self._calculate_discounts(session, store_id, rows)
            subtotal_after_discounts = max(0.0, subtotal - (discounts_info["discount_total"]))
            shipping_info = self._calculate_shipping(session, store_id, subtotal_after_discounts)
            grand_total = round(subtotal_after_discounts + (shipping_info["shipping"] or 0.0), 2)
            # Create order
            order = Order(
                order_number=f"ORD-{int(datetime.now().timestamp())}",
                customer_id=cust.id,
                warehouse_id=wh.id if wh else None,
                status="paid",
                total_amount=grand_total,
                store_id=store_id,
            )
            session.add(order)
            session.flush()
            # Items + inventory decrement (naive: first warehouse)
            for item, prod in rows:
                oi = OrderItem(order_id=order.id, product_id=prod.id, quantity=item.quantity or 1, unit_price=item.unit_price or prod.price or 0.0)
                session.add(oi)
                # decrement inventory
                if wh and prod.sku:
                    inv = (
                        session.query(InventoryItem)
                        .filter(InventoryItem.warehouse_id == wh.id, InventoryItem.sku == prod.sku)
                        .first()
                    )
                    if not inv:
                        inv = InventoryItem(sku=prod.sku, name=prod.name, warehouse_id=wh.id, quantity=0)
                    inv.quantity = max(0, (inv.quantity or 0) - (item.quantity or 1))
                    session.add(inv)
            # Clear cart
            for item, _ in rows:
                session.delete(item)
            return order.id

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
