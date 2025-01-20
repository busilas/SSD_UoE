"""
This module defines custom exceptions for a shop management application. 
These exceptions are used to handle specific error scenarios, ensuring 
better error management and clarity in the codebase.

By using these custom exceptions, developers can provide more meaningful 
error messages and implement precise exception handling mechanisms.
"""

# Single-line comment: Base class for all shop-related exceptions
class ShopException(Exception):
    """
    Base exception for shop operations. All other exceptions in this module 
    inherit from this class, providing a unified structure for error handling.
    """
    @staticmethod
    def get_base_exception():
        """
        Returns the base exception class for shop operations.
        """
        return ShopException


# Single-line comment: Exception raised for authentication failures
class AuthenticationError(ShopException):
    """
    Raised when authentication fails, such as incorrect credentials 
    or unauthorized access attempts.
    """
    @staticmethod
    def get_error_type():
        """
        Returns the specific error type for authentication failures.
        """
        return AuthenticationError


# Single-line comment: Exception raised for authorization issues
class AuthorizationError(ShopException):
    """
    Raised when a user lacks the required permissions to perform an action.
    """
    @staticmethod
    def get_error_type():
        """
        Returns the specific error type for authorization issues.
        """
        return AuthorizationError

# Single-line comment: Exception raised when a resource is not found
class ResourceNotFoundError(ShopException):
    """
    Raised when a requested resource (e.g., product, user, or order) 
    cannot be found in the system.
    """
    @staticmethod
    def get_error_type():
        """
        Returns the specific error type for resource not found scenarios.
        """
        return ResourceNotFoundError

# Single-line comment: Exception raised for input validation errors
class ValidationError(ShopException):
    """
    Raised when input validation fails, ensuring that only valid data 
    is processed by the application.
    """
    @staticmethod
    def get_error_type():
        """
        Returns the specific error type for validation errors.
        """
        return ValidationError
