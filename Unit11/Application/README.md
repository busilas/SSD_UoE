# Secure CLI CRUD Application with Flask API

## Overview
This project implements a secure CLI and REST API-based application for managing user registration and inventory operations. The system prioritizes security, input validation, and modular design while adhering to best practices for API development.

## Features
- **Role-Based Access Control (RBAC)**: Supports roles like admin, clerk, and customer.
- **Secure Authentication**: Implements password hashing with bcrypt.
- **Input Validation**: Uses regex for data validation.
- **REST API**: Built with Flask to manage user registration and company ID validation.
- **JSON-Based Database**: Lightweight data persistence using JSON files.

## Project Structure
```
.
├── main.py                     # Flask application with API endpoints
├── utils/
│   ├── db_utils.py             # Utility functions for database management
│   ├── auth_utils.py           # Authentication and user management utilities
│   ├── validation_utils.py     # Input validation utilities
└── README.md                   # Documentation file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/secure-cli-crud.git
   cd secure-cli-crud
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate an encryption key (if not already present):
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > key.key
   ```

### Running the Application
1. Start the Flask server:
   ```bash
   python main.py
   ```
2. Access the API endpoints:
   - `POST /register`: Register a new user.
   - `GET /validate_company/<company_id>`: Validate a company ID.

### Example API Requests

#### Register a User
```bash
curl -X POST http://127.0.0.1:5000/register \
-H "Content-Type: application/json" \
-d '{"username": "john_doe", "password": "securePass123", "role": "admin", "company_id": "12345"}'
```

#### Validate a Company ID
```bash
curl http://127.0.0.1:5000/validate_company/12345
```

## Utilities
### `utils/db_utils.py`
- Functions for loading and saving data to JSON files.

### `utils/auth_utils.py`
- Functions for password hashing, user authentication, and user creation.

### `utils/validation_utils.py`
- Functions for input validation using regex.

## Security Features
- **Password Hashing**: Uses bcrypt for strong password security.
- **Input Validation**: Prevents injection attacks through rigorous validation.
- **Logging**: Logs all critical operations and errors.

## Future Enhancements
- Add more endpoints for CRUD operations on inventory.
- Implement rate-limiting to mitigate brute force attacks.
- Introduce unit and integration tests for robust validation.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributors
- [Andrius Busilas](# Secure CLI CRUD Application with Flask API

## Overview
This project implements a secure CLI and REST API-based application for managing user registration and inventory operations. The system prioritizes security, input validation, and modular design while adhering to best practices for API development.

## Features
- **Role-Based Access Control (RBAC)**: Supports roles like admin, clerk, and customer.
- **Secure Authentication**: Implements password hashing with bcrypt.
- **Input Validation**: Uses regex for data validation.
- **REST API**: Built with Flask to manage user registration and company ID validation.
- **JSON-Based Database**: Lightweight data persistence using JSON files.

## Project Structure
```
.
├── main.py                     # Flask application with API endpoints
├── utils/
│   ├── db_utils.py             # Utility functions for database management
│   ├── auth_utils.py           # Authentication and user management utilities
│   ├── validation_utils.py     # Input validation utilities
└── README.md                   # Documentation file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/secure-cli-crud.git
   cd secure-cli-crud
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate an encryption key (if not already present):
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > key.key
   ```

### Running the Application
1. Start the Flask server:
   ```bash
   python main.py
   ```
2. Access the API endpoints:
   - `POST /register`: Register a new user.
   - `GET /validate_company/<company_id>`: Validate a company ID.

### Example API Requests

#### Register a User
```bash
curl -X POST http://127.0.0.1:5000/register \
-H "Content-Type: application/json" \
-d '{"username": "john_doe", "password": "securePass123", "role": "admin", "company_id": "12345"}'
```

#### Validate a Company ID
```bash
curl http://127.0.0.1:5000/validate_company/12345
```

## Utilities
### `utils/db_utils.py`
- Functions for loading and saving data to JSON files.

### `utils/auth_utils.py`
- Functions for password hashing, user authentication, and user creation.

### `utils/validation_utils.py`
- Functions for input validation using regex.

## Security Features
- **Password Hashing**: Uses bcrypt for strong password security.
- **Input Validation**: Prevents injection attacks through rigorous validation.
- **Logging**: Logs all critical operations and errors.

## Future Enhancements
- Add more endpoints for CRUD operations on inventory.
- Implement rate-limiting to mitigate brute force attacks.
- Introduce unit and integration tests for robust validation.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributors
- [Andrius Busilas](https://github.com/busilas)

