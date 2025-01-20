"""
This module provides an authentication decorator for securing Flask endpoints. 
It ensures that incoming requests include a valid JWT token, checks session validity, 
and verifies user roles for authorization. The decorator is designed for easy integration 
with role-based access control in a Flask application.
"""

from functools import wraps
from flask import request, g
import jwt
from security import SecurityConfig
from exceptions import AuthenticationError, AuthorizationError
from enums import UserRole
from managers import session_manager
from typing import List

# Authentication Decorator
def require_auth(roles: List[UserRole]):
    """
    A decorator to enforce authentication and authorization on Flask routes.
    
    Args:
        roles (List[UserRole]): List of user roles allowed to access the route.

    Returns:
        function: The wrapped function if the user is authenticated and authorized.

    Raises:
        AuthenticationError: If the token is missing, invalid, or expired.
        AuthorizationError: If the user's role is not permitted to access the route.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Retrieve the 'Authorization' header
            token = request.headers.get('Authorization')
            
            if not token or not token.startswith('Bearer '):  # Ensure token exists and is correctly formatted
                raise AuthenticationError("Missing or invalid token")  # Raise error if token is invalid
                
            try:
                # Extract the actual token part after 'Bearer '
                token = token.split('Bearer ')[1]
                
                # Decode the JWT using the application's secret key
                payload = jwt.decode(token, SecurityConfig.JWT_SECRET, algorithms=["HS256"])
                
                # Validate the session
                if not session_manager.is_session_valid(payload['user_id'], token):
                    raise AuthenticationError("Invalid session")  # Raise error if session is invalid
                
                # Check if the user's role is in the allowed roles
                if UserRole(payload['role']) not in roles:
                    raise AuthorizationError("Insufficient permissions")  # Raise error if role is unauthorized
                
                # Store user info in Flask's global `g` object for use in the endpoint
                g.user = payload
                return f(*args, **kwargs)  # Execute the wrapped function if authentication succeeds
            
            # Handle specific JWT errors
            except jwt.ExpiredSignatureError:
                raise AuthenticationError("Token has expired")  # Token expired error
            except jwt.InvalidTokenError:
                raise AuthenticationError("Invalid token")  # Generic token error
            
        return decorated
    return decorator

# Return Function
def get_require_auth():
    """
    Provides the `require_auth` decorator for importing in other modules.
    
    Returns:
        function: The `require_auth` decorator.
    """
    return require_auth
