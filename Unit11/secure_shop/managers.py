"""
This module provides core management classes for handling Multi-Factor Authentication (MFA), 
session management, user operations, inventory management, and order processing. Each class 
encapsulates specific functionalities to support secure and efficient operations in an 
e-commerce system. Redis is used for session and OTP management, and all actions are logged 
for monitoring and auditing purposes.
"""

import hashlib
import re
import redis
import bcrypt
import jwt
import pyotp
import smtplib
from datetime import datetime, UTC
from threading import Lock
from config import db, redis_client, logger, security_logger
from security import SecurityConfig
from exceptions import ValidationError, AuthenticationError, ResourceNotFoundError
from enums import UserRole, OrderStatus, AccountStatus
from database import User, Company, InventoryItem, Order, OrderItem
from typing import List, Dict


## MFA Manager
class MFAManager:
    """
    Manages the generation, storage, and verification of One-Time Passwords (OTPs) for MFA.
    """
    def __init__(self, redis_client):
        self._lock = Lock()
        try:
            redis_client.ping()  # Test Redis connection
            self._redis = redis_client
            print("Connected to Redis for MFA.")
        except (redis.exceptions.ConnectionError, AttributeError):
            print("Warning: Redis unavailable. Using in-memory storage for MFA.")
            self._redis = None
            self._in_memory_otps = {}

    def generate_otp(self, user_id: int) -> str:
        """
        Generate and store a new OTP for a user.
        """
        otp = pyotp.random_base32()[:SecurityConfig.OTP_LENGTH]
        with self._lock:
            if self._redis:
                self._redis.setex(
                    f"otp:{user_id}",
                    SecurityConfig.OTP_EXPIRATION.total_seconds(),
                    otp
                )
            else:
                expiry = datetime.now() + SecurityConfig.OTP_EXPIRATION
                self._in_memory_otps[user_id] = {'otp': otp, 'expiry': expiry}
        return otp

    def verify_otp(self, user_id: int, otp: str) -> bool:
        """
        Verify a user's OTP.
        """
        with self._lock:
            if self._redis:
                stored_otp = self._redis.get(f"otp:{user_id}")
                if not stored_otp:
                    return False
                self._redis.delete(f"otp:{user_id}")
                return stored_otp.decode() == otp
            else:
                stored_data = self._in_memory_otps.get(user_id)
                if not stored_data or datetime.now() > stored_data['expiry']:
                    self._in_memory_otps.pop(user_id, None)
                    return False
                return stored_data['otp'] == otp

    def send_otp_email(self, email: str, otp: str):
        """
        Send OTP to the user's email.
        """
        print(f"\nDevelopment Mode: OTP for {email} is: {otp}")
        logger.info(f"Generated OTP for {email}: {otp}")

def get_mfa_manager(redis_client):
    """
    Returns an instance of MFAManager.
    """
    return MFAManager(redis_client)


## Session Manager
class SessionManager:
    """
    Manages user sessions, ensuring secure token storage and validation.
    """
    def __init__(self, redis_client):
        self._lock = Lock()
        try:
            redis_client.ping()
            self._redis = redis_client
            print("Connected to Redis.")
        except redis.exceptions.ConnectionError:
            print("Warning: Redis unavailable. Using in-memory sessions.")
            self._redis = None
            self._in_memory_sessions = {}

    def create_session(self, user_id: int, token: str):
        """
        Create a new session for a user.
        """
        with self._lock:
            if self._redis:
                self._redis.setex(f"session:{user_id}", SecurityConfig.JWT_EXPIRATION.total_seconds(), token)
            else:
                self._in_memory_sessions[user_id] = {
                    "token": token,
                    "expiration": datetime.now() + SecurityConfig.JWT_EXPIRATION
                }

    def invalidate_session(self, user_id: int):
        """
        Invalidate a user's session.
        """
        with self._lock:
            if self._redis:
                self._redis.delete(f"session:{user_id}")
            else:
                self._in_memory_sessions.pop(user_id, None)

    def is_session_valid(self, user_id: int, token: str) -> bool:
        """
        Check if a session is valid.
        """
        with self._lock:
            if self._redis:
                stored_token = self._redis.get(f"session:{user_id}")
                return stored_token and stored_token.decode() == token
            else:
                session = self._in_memory_sessions.get(user_id)
                if session and session["token"] == token and session["expiration"] > datetime.now():
                    return True
                self._in_memory_sessions.pop(user_id, None)
                return False

def get_session_manager(redis_client):
    """
    Returns an instance of SessionManager.
    """
    return SessionManager(redis_client)

session_manager = SessionManager(redis_client)

## User Manager
class UserManager:
    """
    Handles user-related operations, including creation and authentication.
    """
    def __init__(self):
        self.mfa_manager = MFAManager(redis_client)

    @staticmethod
    def create_user(data: Dict) -> User:
        """
        Create a new user with hashed credentials.
        """
        # Validate password
        if not re.match(SecurityConfig.PASSWORD_PATTERN, data['password']):
            raise ValidationError("Password does not meet security requirements")
        # Hash email and password
        email_hash = hashlib.sha256(data['email'].encode()).hexdigest()
        password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())

        user = User(
            email=data['email'],
            email_hash=email_hash,
            password_hash=password_hash.decode(),
            forename=data['forename'],
            surname=data['surname'],
            role=UserRole(data['role']),
            company_id=data['company_id']
        )

        db.session.add(user)
        db.session.commit()
        logger.info(f"Created new user: {data['email']}")
        return user


    def authenticate_user(self, email: str, password: str) -> Dict:
        """First step of authentication - verify credentials"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            security_logger.warning(f"Failed login attempt: email={email}")
            raise AuthenticationError("Invalid credentials")
        
        if user.status != AccountStatus.ACTIVE:
            security_logger.warning(f"Inactive account login attempt: email={email}")
            raise AuthenticationError("Account is inactive")
        
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            security_logger.warning(f"Failed login attempt: email={email}, user_id={user.id}")
            raise AuthenticationError("Invalid credentials")
        
        # Successful login (partial, before OTP verification)
        security_logger.info(f"Successful login: email={email}, user_id={user.id}")
        otp = self.mfa_manager.generate_otp(user.id)
        self.mfa_manager.send_otp_email(user.email, otp)
        
        # Return user data as a dictionary
        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "company_id": user.company_id,
            "requires_otp": True
        }


    def verify_otp_and_login(self, user_id: int, otp: str) -> str:
        """Second step of authentication - verify OTP and generate token"""
        if not self.mfa_manager.verify_otp(user_id, otp):
            raise AuthenticationError("Invalid or expired authentication code")
        
        user = User.query.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        token = jwt.encode(
            {
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "company_id": user.company_id,
                "exp": datetime.now(UTC) + SecurityConfig.JWT_EXPIRATION
            },
            SecurityConfig.JWT_SECRET,
            algorithm="HS256"
        )
        
        session_manager.create_session(user.id, token)
        logger.info(f"User completed MFA: {user.email}")
        return token

def get_user_manager():
    """
    Returns an instance of UserManager.
    """
    return UserManager()


## Inventory Management
class InventoryManager:
    @staticmethod
    def add_item(data: Dict) -> InventoryItem:
        """Add new item to inventory"""
        item = InventoryItem(
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            quantity=data['quantity'],
            price=data['price'],
            company_id=data['company_id']
        )
        
        db.session.add(item)
        db.session.commit()
        logger.info(f"Added inventory item: {data['name']}")
        return item

    @staticmethod
    def update_quantity(item_id: str, quantity: int) -> InventoryItem:
        """Update item quantity"""
        item = InventoryItem.query.get(item_id)
        if not item:
            raise ResourceNotFoundError("Item not found")
        
        item.quantity = quantity
        item.updated_at = datetime.now(UTC)
        db.session.commit()
        logger.info(f"Updated quantity for item {item_id}: {quantity}")
        return item

# Order Management
class OrderManager:
    @staticmethod
    def create_order(user_id: int, items: List[Dict], company_id: str) -> Order:
        """Create a new order"""
        order = Order(user_id=user_id, company_id=company_id)
        db.session.add(order)
        
        for item_data in items:
            item = InventoryItem.query.get(item_data['item_id'])
            if not item:
                db.session.rollback()
                raise ResourceNotFoundError(f"Item not found: {item_data['item_id']}")
                
            if item.quantity < item_data['quantity']:
                db.session.rollback()
                raise ValidationError(f"Insufficient quantity for item: {item.name}")
                
            order_item = OrderItem(
                order=order,
                item_id=item.id,
                quantity=item_data['quantity'],
                price_at_time=item.price
            )
            db.session.add(order_item)
            
            item.quantity -= item_data['quantity']
            
        db.session.commit()
        logger.info(f"Created order: {order.id}")
        return order

    @staticmethod
    def update_status(order_id: str, status: OrderStatus) -> Order:
        """Update order status"""
        order = Order.query.get(order_id)
        if not order:
            raise ResourceNotFoundError("Order not found")
            
        order.status = status
        order.updated_at = datetime.now(UTC)
        db.session.commit()
        logger.info(f"Updated order status: {order_id} -> {status.value}")
        return order
