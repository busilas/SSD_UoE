"""
This module handles security and authentication configurations, token management, and related utilities.
It includes functionality for configuring JWT settings, password policies, multi-factor authentication (MFA),
and email settings for secure user authentication and account management.
"""

from datetime import datetime, timedelta, timezone
from decouple import config
import jwt

## Security and Authentication

# Security Configuration
class SecurityConfig:
    """
    Configuration class for security and authentication settings.

    Attributes:
        JWT_SECRET (str): Secret key for signing JWT tokens.
        PASSWORD_MIN_LENGTH (int): Minimum length for passwords.
        PASSWORD_PATTERN (str): Regex pattern to enforce password complexity.
        JWT_EXPIRATION (timedelta): Token expiration time.
        MAX_LOGIN_ATTEMPTS (int): Maximum allowed login attempts before lockout.
        LOCKOUT_DURATION (timedelta): Duration of account lockout after too many failed attempts.
        OTP_EXPIRATION (timedelta): Expiration time for OTPs.
        OTP_LENGTH (int): Length of the OTP code.
        SMTP_SERVER (str): SMTP server for sending emails.
        SMTP_PORT (int): Port for the SMTP server.
        SMTP_USERNAME (str): Username for SMTP authentication.
        SMTP_PASSWORD (str): Password for SMTP authentication.
        EMAIL_FROM (str): Sender email address for notifications.
    """
    # Security configurations are loaded from environment variables or default values.
    JWT_SECRET = config('JWT_SECRET', default='default_jwt_secret_key')
    PASSWORD_MIN_LENGTH = config('PASSWORD_MIN_LENGTH', default=12, cast=int)
    PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'
    JWT_EXPIRATION = timedelta(hours=config('JWT_EXPIRATION_HOURS', default=1, cast=int))
    MAX_LOGIN_ATTEMPTS = config('MAX_LOGIN_ATTEMPTS', default=3, cast=int)
    LOCKOUT_DURATION = timedelta(minutes=config('LOCKOUT_DURATION_MINUTES', default=15, cast=int))
    
    # MFA configurations for OTPs and email settings
    OTP_EXPIRATION = timedelta(minutes=5)
    OTP_LENGTH = 6
    SMTP_SERVER = config('SMTP_SERVER', default='smtp.gmail.com')
    SMTP_PORT = config('SMTP_PORT', default=587, cast=int)
    SMTP_USERNAME = config('SMTP_USERNAME', default='your-email@gmail.com')
    SMTP_PASSWORD = config('SMTP_PASSWORD', default='your-app-password')
    EMAIL_FROM = config('EMAIL_FROM', default='your-email@gmail.com')

    @staticmethod
    def get_config() -> dict:
        """
        Return the configuration as a dictionary for use in other files.

        Returns:
            dict: Configuration key-value pairs.
        """
        return {
            "JWT_SECRET": SecurityConfig.JWT_SECRET,
            "PASSWORD_MIN_LENGTH": SecurityConfig.PASSWORD_MIN_LENGTH,
            "PASSWORD_PATTERN": SecurityConfig.PASSWORD_PATTERN,
            "JWT_EXPIRATION": SecurityConfig.JWT_EXPIRATION,
            "MAX_LOGIN_ATTEMPTS": SecurityConfig.MAX_LOGIN_ATTEMPTS,
            "LOCKOUT_DURATION": SecurityConfig.LOCKOUT_DURATION,
            "OTP_EXPIRATION": SecurityConfig.OTP_EXPIRATION,
            "OTP_LENGTH": SecurityConfig.OTP_LENGTH,
            "SMTP_SERVER": SecurityConfig.SMTP_SERVER,
            "SMTP_PORT": SecurityConfig.SMTP_PORT,
            "SMTP_USERNAME": SecurityConfig.SMTP_USERNAME,
            "SMTP_PASSWORD": SecurityConfig.SMTP_PASSWORD,
            "EMAIL_FROM": SecurityConfig.EMAIL_FROM,
        }

# Authentication Service
class AuthService:
    """
    Service class for managing authentication tokens.

    Methods:
        create_token(data): Generates a JWT token with the given data and expiration.
        verify_token(token): Verifies and decodes a JWT token.
    """

    @staticmethod
    def create_token(data: dict) -> str:
        """
        Generate a JWT token with the given payload and expiration.

        Args:
            data (dict): Payload to include in the token.

        Returns:
            str: Encoded JWT token.
        """
        expiration = datetime.now(timezone.utc) + SecurityConfig.JWT_EXPIRATION  # Calculate expiration time
        data['exp'] = expiration  # Add expiration to the payload
        # Encode the payload using the secret and HS256 algorithm
        return jwt.encode(data, SecurityConfig.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token (str): JWT token to verify.

        Returns:
            dict: Decoded payload if the token is valid.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        # Decode the token using the secret and HS256 algorithm
        return jwt.decode(token, SecurityConfig.JWT_SECRET, algorithms=["HS256"])

    @staticmethod
    def get_service_functions() -> dict:
        """
        Return references to the authentication service methods for use in other files.

        Returns:
            dict: Method references for create_token and verify_token.
        """
        return {
            "create_token": AuthService.create_token,
            "verify_token": AuthService.verify_token,
        }
