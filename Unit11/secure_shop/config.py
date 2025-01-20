"""
This module sets up the Flask application for a shop management system, including:
- Application configuration and initialization
- Integration with extensions such as SQLAlchemy, Flask-Limiter, Flask-Talisman, and Flask-CORS
- Logging configuration with JSON format for security logs
- Redis connection setup with a fallback to a mock client for development
"""

import logging
import json
from datetime import datetime, UTC
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import redis
from unittest.mock import MagicMock

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration from environment variables
app.config['SECRET_KEY'] = config('SECRET_KEY', default='default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL', default='sqlite:///shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REDIS_URL'] = config('REDIS_URL', default='redis://localhost:6379/0')

# Initialize extensions
db = SQLAlchemy(app)
talisman = Talisman(app, force_https=config('FORCE_HTTPS', default=True, cast=bool))
limiter = Limiter(app=app, key_func=get_remote_address)

# Configure main application logging
logging.basicConfig(
    level=config('LOG_LEVEL', default='INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config('LOG_FILE', default='shop.log')
)
logger = logging.getLogger(__name__)

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# File handler for security logs
security_handler = logging.FileHandler('security.log')
security_handler.setLevel(logging.INFO)

# JSON Formatter for security logs
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name
        }
        return json.dumps(log_entry)

# Apply JSON formatter to security handler
security_handler.setFormatter(JSONFormatter())
security_logger.addHandler(security_handler)

# Make security_logger available at module level
__all__ = ['app', 'db', 'logger', 'security_logger', 'limiter', 'talisman']

# Initialize Redis
try:
    redis_client = redis.from_url(app.config['REDIS_URL'])
except redis.exceptions.ConnectionError:
    redis_client = MagicMock()
    print("Warning: Redis connection failed. Using mock Redis for development.")