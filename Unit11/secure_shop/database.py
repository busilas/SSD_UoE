"""
This module defines the database models for a shop management application. 
The models include `User`, `Company`, `InventoryItem`, `Order`, and `OrderItem`. 
Each model represents a table in the database and contains relationships, validations, 
and default creation functions for essential entities like an admin user and a company.
"""

import uuid
import bcrypt
import hashlib
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from config import db, config
from exceptions import ValidationError
from enums import OrderStatus, AccountStatus, UserRole
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from decouple import config

# Database Models
class User(db.Model):
    """
    Represents a user in the system with attributes like email, name, role, and status. 
    Relationships include associated orders and a company.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    email_hash = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    forename = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    status = Column(SQLEnum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))

    # Relationships
    company = relationship("Company", back_populates="users")
    orders = relationship("Order", back_populates="user")

    @staticmethod
    def get_model():
        """Returns the User model for import."""
        return User


class Company(db.Model):
    """
    Represents a company in the system, including attributes like name, description, 
    and status. Relationships include associated users and inventory items.
    """
    __tablename__ = 'companies'

    id = Column(String(50), primary_key=True, default=lambda: f"company_{str(uuid.uuid4())[:8]}")
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="company", cascade="all, delete-orphan")

    @validates('name')
    def validate_name(self, key, name):
        """Validates the company's name, ensuring it is not empty and under 255 characters."""
        if not name or not name.strip():
            raise ValidationError("Company name cannot be empty")
        if len(name) > 255:
            raise ValidationError("Company name must be less than 255 characters")
        return name.strip()

    @validates('status')
    def validate_status(self, key, status):
        """Validates the company's status, ensuring it is active, inactive, or suspended."""
        valid_statuses = ['active', 'inactive', 'suspended']
        if status.lower() not in valid_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return status.lower()

    @staticmethod
    def get_model():
        """Returns the Company model for import."""
        return Company


class InventoryItem(db.Model):
    """
    Represents an inventory item in the system, including details like name, 
    category, quantity, and price. Associated with a company.
    """
    __tablename__ = 'inventory_items'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    category = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))

    # Relationships
    company = relationship("Company", back_populates="inventory_items")

    @staticmethod
    def get_model():
        """Returns the InventoryItem model for import."""
        return InventoryItem


class Order(db.Model):
    """
    Represents an order in the system, including the user, company, and status. 
    Related to order items.
    """
    __tablename__ = 'orders'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PLACED)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    @staticmethod
    def get_model():
        """Returns the Order model for import."""
        return Order


class OrderItem(db.Model):
    """
    Represents an item within an order, including quantity and price at the time of order. 
    Related to both an order and an inventory item.
    """
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(String(36), ForeignKey('orders.id'), nullable=False)
    item_id = Column(String(36), ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    item = relationship("InventoryItem")

    @staticmethod
    def get_model():
        """Returns the OrderItem model for import."""
        return OrderItem


# Default Admin User
def create_default_admin():
    """Creates a default admin user if one doesn't already exist."""
    admin_email = config('DEFAULT_ADMIN_EMAIL', default='admin@example.com')
    admin_password = config('DEFAULT_ADMIN_PASSWORD', default='Admin@1234')

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        print(f"Admin user already exists: {admin_email}")
        return

    # Hash the password
    password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    
    # Create admin user
    admin_user = User(
        email=admin_email,
        email_hash=hashlib.sha256(admin_email.encode()).hexdigest(),
        password_hash=password_hash,
        forename='Admin',
        surname='User',
        role=UserRole.ADMIN,
        status=AccountStatus.ACTIVE,
        company_id='default_company'
    )
    
    db.session.add(admin_user)
    db.session.commit()
    print(f"Default admin created with email: {admin_email}")


# Default Company
def create_default_company():
    """Creates a default company if it doesn't exist."""
    company_id = 'default_company'
    company_name = 'Default Company'

    existing_company = Company.query.get(company_id)
    if not existing_company:
        default_company = Company(
            id=company_id,
            name=company_name,
            created_at=datetime.now(UTC)
        )
        db.session.add(default_company)
        db.session.commit()
        print(f"Default company created: {company_name}")
