# SecureShop: Enterprise Inventory Management System

A secure, multi-tenant inventory management system with role-based access control, two-factor authentication, and comprehensive API support.

## Features

- **Multi-tenant Architecture**: Support for multiple companies with isolated data
- **Role-based Access Control**: Admin, Clerk, and Customer role levels
- **Two-Factor Authentication**: Email-based OTP verification
- **Secure Session Management**: JWT-based authentication with Redis session store
- **Rate Limiting**: Protection against brute force attacks
- **CLI and API Interfaces**: Flexible access options
- **Comprehensive Logging**: Detailed system activity tracking

## System Requirements

- Python 3.8+
- Redis Server
- PostgreSQL/SQLite
- SMTP Server (for OTP delivery)

!!!!!!!!!!!!!!!!!!!Is kito failo!!!!!!!!!!!!!!!!!
## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/busilas/SSD_UoE/tree/main/Unit11/secure_shop
   cd secure_shop
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export SECRET_KEY=<your-secret-key>
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Start the application.
2. Log in with one of the default credentials (admin, clerk, or customer).
3. Perform actions based on your role.
4. Access the REST API for company verification at `http://localhost:5000/api/verify/<company_id>`.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (copy `.env.example` to `.env`):
```bash
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
REDIS_URL=redis://localhost:6379/0
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_app_password
```

## Project Structure

```
src/
├── main.py            # Application entry point
├── config.py          # Application configuration and initialization
├── database.py        # ORM models and database schema
├── security.py        # Security configurations and utilities
├── managers.py        # Business logic and core operations
├── enums.py           # Enumerations for roles, statuses, etc.
├── exceptions.py      # Custom exception classes
├── api_routes.py      # Flask API route definitions
├── cli.py             # Command-line interface for admin and user actions
├── decorator.py       # Authentication and authorization decorators
└── tests/             # Test suite

```

## Security Features

### Authentication
- Secure password hashing with bcrypt
- JWT token-based authentication
- Email-based two-factor authentication
- Session management with Redis
- Rate limiting on authentication endpoints

### Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Data Protection
- HTTPS enforcement with Flask-Talisman
- SQL injection protection with SQLAlchemy
- Input validation with Pydantic
- CORS configuration
- Rate limiting on sensitive endpoints

## API Endpoints

### Authentication
```
POST /api/auth/login          # Initial login
POST /api/auth/verify-otp     # OTP verification
POST /api/auth/logout         # Logout
```

### User Management
```
POST /api/users              # Create user (Admin only)
```

### Inventory Management
```
POST /api/inventory          # Add inventory item
PUT  /api/inventory/<id>     # Update inventory item
```

### Order Management
```
POST /api/orders             # Create order
PUT  /api/orders/<id>/status # Update order status
GET  /api/orders            # List orders
```

### Company Management
```
GET  /api/companies         # List companies
POST /api/companies        # Create company
```

## CLI Interface

### Admin Menu
- Company management
- User management
- System logs viewing

### Clerk Menu
- Inventory management
- Order processing
- Stock updates

### Customer Menu
- Product browsing
- Cart management
- Order tracking

## Development Setup

1. Set up development environment:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

2. Run tests:
```bash
pytest tests/
```

3. Start development server:
```bash
python main.py
```

## Default Roles and Credentials

The system creates a default admin account and company on first run:

| Role      | Username            | Password     |
|-----------|---------------------|--------------|
| Admin     | admin@example.com   | Admin@1234   |

- Email: admin@example.com (configurable via DEFAULT_ADMIN_EMAIL)
- Password: Admin@1234 (configurable via DEFAULT_ADMIN_PASSWORD)

**Important Security Notes:**
- Change these credentials immediately after first login
- The system will require an OTP code after password verification
- In development mode, the OTP code will be printed to the console
- In production, the OTP code will be sent to the configured email address

## Error Handling

The system implements a hierarchical exception system:
- ShopException (Base)
  - AuthenticationError
  - AuthorizationError
  - ResourceNotFoundError
  - ValidationError

All errors are logged and return appropriate HTTP status codes.

## Production Deployment

### Requirements
- Production-grade WSGI server (e.g., Gunicorn)
- Redis instance for session management
- Production database (PostgreSQL recommended)
- SMTP server for OTP delivery
- SSL certificate for HTTPS

### Deployment Steps
1. Set up production environment variables
2. Configure database with proper indexes
3. Set up Redis with persistence
4. Configure SMTP for production
5. Set up logging to appropriate location
6. Enable HTTPS
7. Configure rate limiting for production load

## License

This project is licensed under the MIT License - see the LICENSE file for details.

