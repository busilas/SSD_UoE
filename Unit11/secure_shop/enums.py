"""
This module defines enumeration classes for representing various status types 
and roles in an application. These enums standardize and restrict the possible 
values for order statuses, account statuses, and user roles, ensuring consistency 
throughout the application.
"""

# Importing Enum for creating enumeration classes
from enum import Enum

# Single-line comment: Defining possible statuses for orders
class OrderStatus(str, Enum):
    """
    Represents the various stages of an order's lifecycle.
    """
    PLACED = "PLACED"  # Order has been placed by the customer
    PROCESSED = "PROCESSED"  # Order is being prepared
    SHIPPED = "SHIPPED"  # Order has been shipped
    DELIVERED = "DELIVERED"  # Order has been delivered
    COMPLETED = "COMPLETED"  # Order has been completed
    CANCELED = "CANCELED"  # Order has been canceled

    @staticmethod
    def get_statuses():
        """
        Returns a list of all possible order statuses.
        """
        return [status.value for status in OrderStatus]


# Single-line comment: Defining possible statuses for accounts
class AccountStatus(str, Enum):
    """
    Represents the different states an account can have.
    """
    ACTIVE = "ACTIVE"  # Account is active and operational
    SUSPENDED = "SUSPENDED"  # Account is temporarily disabled
    INACTIVE = "INACTIVE"  # Account is not currently in use

    @staticmethod
    def get_statuses():
        """
        Returns a list of all possible account statuses.
        """
        return [status.value for status in AccountStatus]


# Single-line comment: Defining possible roles for users
class UserRole(str, Enum):
    """
    Represents the different roles a user can have in the system.
    """
    ADMIN = "ADMIN"  # User has administrative privileges
    CLERK = "CLERK"  # User is a clerk handling operations
    CUSTOMER = "CUSTOMER"  # User is a customer interacting with the system

    @staticmethod
    def get_roles():
        """
        Returns a list of all possible user roles.
        """
        return [role.value for role in UserRole]
