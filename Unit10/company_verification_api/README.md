
# Role-Based Access Control API

This is a Flask-based API for managing role-based access control. It includes authentication and authorization mechanisms and serves specific dashboards for users with different roles: admin, customer, and clerk.

## Features

- User login and logout with session management.
- Role-based access to specific endpoints:
  - Admin dashboard
  - Customer dashboard
  - Clerk dashboard
- Secure token-based authentication.
- Mock data simulating a user database.

## Requirements

- Python 3.x
- Flask

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/role-based-api.git
   cd role-based-api
   ```

2. **Install dependencies**:
   ```bash
   pip install flask
   ```

3. **Run the application**:
   ```bash
   python company_verification_api.py
   ```

4. **Access the application**:
   - API will be available at `http://127.0.0.1:5000`.

## API Endpoints

### 1. Home (`GET /`)
Returns available routes and information about the API.

### 2. Login (`POST /login`)
Authenticate a user and generate a session token.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Response
```json
{
  "message": "Login successful. Welcome [role]!",
  "role": "user_role",
  "token": "token-1"
}
```

### 3. Logout (`POST /logout`)
Invalidate the user's session token.

#### Headers
```
Authorization: token-1
```

#### Response
```json
{
  "message": "Logged out successfully"
}
```

### 4. Admin Dashboard (`GET /admin`)
Access the admin dashboard. Requires the `admin` role.

#### Headers
```
Authorization: token-1
```

#### Response
```json
{
  "message": "Welcome to the Admin Dashboard, user@example.com!"
}
```

### 5. Customer Dashboard (`GET /customer`)
Access the customer dashboard. Requires the `customer` role.

#### Headers
```
Authorization: token-2
```

#### Response
```json
{
  "message": "Welcome to the Customer Dashboard, user@example.com!"
}
```

### 6. Clerk Dashboard (`GET /clerk`)
Access the clerk dashboard. Requires the `clerk` role.

#### Headers
```
Authorization: token-3
```

#### Response
```json
{
  "message": "Welcome to the Clerk Dashboard, user@example.com!"
}
```

## Mock Data

The application uses the following mock data for demonstration purposes:

| ID  | Email                 | Password   | Role      | Company    |
|-----|-----------------------|------------|-----------|------------|
| 1   | admin@example.com     | admin123   | admin     | CompanyA   |
| 2   | customer@example.com  | cust123    | customer  | CompanyA   |
| 3   | clerk@example.com     | clerk123   | clerk     | CompanyB   |



