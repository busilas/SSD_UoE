from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Mock data to simulate a database
users = [
    {"id": 1, "email": "admin@example.com", "password": "admin123", "role": "admin", "company": "CompanyA"},
    {"id": 2, "email": "customer@example.com", "password": "cust123", "role": "customer", "company": "CompanyA"},
    {"id": 3, "email": "clerk@example.com", "password": "clerk123", "role": "clerk", "company": "CompanyB"}
]

sessions = {}  # Mock session storage

# Decorator for role-based access control
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or token not in sessions:
                return jsonify({"message": "Unauthorized"}), 401

            user = sessions[token]
            if user['role'] != required_role:
                return jsonify({"message": "Forbidden: Access is denied"}), 403

            return f(user, *args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Role-Based App!",
        "routes": {
            "/login": "POST - Login endpoint",
            "/logout": "POST - Logout endpoint",
            "/admin": "GET - Admin dashboard (requires admin role)",
            "/customer": "GET - Customer dashboard (requires customer role)",
            "/clerk": "GET - Clerk dashboard (requires clerk role)"
        }
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users if u['email'] == email and u['password'] == password), None)
    if user:
        token = f"token-{user['id']}"
        sessions[token] = user
        return jsonify({
            "message": f"Login successful. Welcome {user['role']}!",
            "role": user['role'],
            "token": token
        })
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    if token in sessions:
        del sessions[token]
        return jsonify({"message": "Logged out successfully"})
    return jsonify({"message": "Invalid session"}), 401

@app.route('/admin', methods=['GET'])
@role_required('admin')
def admin_dashboard(user):
    return jsonify({"message": f"Welcome to the Admin Dashboard, {user['email']}!"})

@app.route('/customer', methods=['GET'])
@role_required('customer')
def customer_dashboard(user):
    return jsonify({"message": f"Welcome to the Customer Dashboard, {user['email']}!"})

@app.route('/clerk', methods=['GET'])
@role_required('clerk')
def clerk_dashboard(user):
    return jsonify({"message": f"Welcome to the Clerk Dashboard, {user['email']}!"})

if __name__ == '__main__':
    app.run(debug=True)
