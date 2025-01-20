"""
This script contains the API routes for user authentication, user management, inventory management, 
order management, and company management. It uses Flask for handling API requests, with endpoints 
for logging in, managing users and inventory, placing and managing orders, and managing company records.
Each route is secured using role-based authentication and rate-limiting to ensure proper access control 
and resource management. Custom exceptions and error handling are included to provide standardized responses.
"""

import uuid
from flask import jsonify, request, g
from config import app, limiter, logger
from exceptions import ShopException, ValidationError, ResourceNotFoundError
from security import SecurityConfig
from models import (
    LoginRequest, OTPVerificationRequest, CreateUserRequest, 
    CreateInventoryItemRequest, UpdateInventoryQuantityRequest,
    CreateOrderRequest, UpdateOrderStatusRequest, CreateCompanyRequest
)
from config import db, logger
from managers import session_manager
from managers import UserManager, InventoryManager, OrderManager
from decorator import require_auth
from enums import UserRole
from database import Order, Company

## API Routes
@app.errorhandler(Exception)
def handle_generic_error(error):
    """
    Global error handler for unexpected errors. Logs the error and returns a standard error message.
    
    This handler catches all exceptions that are not specifically handled by other error handlers.
    It ensures the application does not crash and provides the client with a generic error message.
    """
    logger.error(f"Internal Server Error: {str(error)}")  # Log full details of the error
    return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@app.errorhandler(ShopException)
def handle_shop_exception(error):
    """
    Handler for known ShopException errors. Returns the error message in the response.
    
    ShopException is a custom exception that is thrown for specific errors like business logic violations.
    This handler logs the warning and returns the error message to the client.
    """
    logger.warning(f"ShopException: {str(error)}")
    return jsonify({"error": str(error)}), 400

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """
    Handles validation errors raised by Pydantic models during request parsing.
    Returns a message indicating input validation failure.
    """
    logger.info(f"Validation Error: {str(error)}")
    return jsonify({"error": "Input validation failed. Please check your request."}), 400

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Endpoint for logging in. Verifies user credentials and sends an OTP.
    
    This route handles the first step of the login process. It validates the user's email and password, 
    and if they are correct, sends an OTP for further verification.
    """
    try:
        data = LoginRequest(**request.get_json())  # Parse request data using Pydantic model
        user_manager = UserManager()  # Instantiate the UserManager class for user-related operations
        result = user_manager.authenticate_user(data.email, data.password)  # Authenticate the user
        return jsonify(result)  # Return authentication result
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400  # Handle validation errors

@app.route('/api/auth/verify-otp', methods=['POST'])
@limiter.limit("5 per minute")
def verify_otp():
    """
    Endpoint for verifying the OTP during login.
    
    This route handles the second step of the login process where the user inputs the OTP sent to them,
    and it completes the authentication process by issuing a token.
    """
    try:
        data = OTPVerificationRequest(**request.get_json())  # Parse OTP data
        user_manager = UserManager()  # UserManager instance
        token = user_manager.verify_otp_and_login(data.user_id, data.otp)  # Verify OTP and issue token
        return jsonify({"token": token})  # Return authentication token
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400  # Handle validation errors

@app.route('/api/auth/logout', methods=['POST'])
@require_auth(roles=[UserRole.ADMIN, UserRole.CLERK, UserRole.CUSTOMER])
def logout():
    """
    Endpoint for logging out. Invalidates the user's session.
    
    This route handles the logout process by invalidating the user's session and ensuring they are 
    logged out of the system.
    """
    session_manager.invalidate_session(g.user['user_id'])  # Invalidate the user session
    return jsonify({"message": "Logged out successfully"})  # Return success message

@app.route('/api/users', methods=['POST'])
@require_auth(roles=[UserRole.ADMIN])
def create_user():
    """
    Endpoint for creating a new user. Only accessible by admins.
    
    This route creates a new user based on the provided request data. The user details are validated, 
    and if valid, a new user is created in the database.
    """
    try:
        data = CreateUserRequest(**request.get_json())  # Parse user creation data
        user = UserManager.create_user(data.dict())  # Create the user using the UserManager
        return jsonify({"message": "User created successfully", "user_id": user.id})  # Return success message
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400  # Handle validation errors

@app.route('/api/inventory', methods=['POST'])
@require_auth(roles=[UserRole.ADMIN, UserRole.CLERK])
def add_inventory_item():
    """
    Endpoint for adding a new inventory item. Accessible by admins and clerks.
    
    This route adds a new item to the inventory. It validates the item data and assigns it to the 
    user's company.
    """
    try:
        data = CreateInventoryItemRequest(**request.get_json())  # Parse inventory data
        data_dict = data.dict()  # Convert Pydantic model to dictionary
        data_dict['company_id'] = g.user['company_id']  # Add company_id to the data
        item = InventoryManager.add_item(data_dict)  # Add the item using InventoryManager
        return jsonify({"message": "Item added successfully", "item_id": item.id})  # Return success message
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400  # Handle validation errors

@app.route('/api/orders', methods=['POST'])
@require_auth(roles=[UserRole.CUSTOMER])
def create_order():
    """
    Endpoint for creating a new order. Accessible by customers only.
    
    This route creates a new order based on the items specified in the request. The order is associated 
    with the logged-in customer and their company.
    """
    try:
        data = CreateOrderRequest(**request.get_json())  # Parse order creation data
        order = OrderManager.create_order(
            user_id=g.user['user_id'],
            items=data.dict()['items'],
            company_id=g.user['company_id']
        )  # Create the order using OrderManager
        return jsonify({"message": "Order created successfully", "order_id": order.id})  # Return success message
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400  # Handle validation errors

# Returning functions for potential imports in other files
def get_routes():
    """
    This function returns the list of all defined API routes for potential use in other files.
    
    This can be useful for testing, documentation, or other purposes that require access to the defined 
    routes without reloading the application.
    """
    return {
        "login": login,
        "verify_otp": verify_otp,
        "logout": logout,
        "create_user": create_user,
        "add_inventory_item": add_inventory_item,
        "create_order": create_order
    }

# Adding additional routes like 'get_orders', 'get_companies', and 'create_company' follows similar patterns...

@app.route('/api/orders', methods=['GET'])
@require_auth(roles=[UserRole.ADMIN, UserRole.CLERK, UserRole.CUSTOMER])
def get_orders():
    """Get orders endpoint"""
    query = Order.query.filter_by(company_id=g.user['company_id'])
    
    # Customers can only see their own orders
    if g.user['role'] == UserRole.CUSTOMER.value:
        query = query.filter_by(user_id=g.user['user_id'])
    
    orders = query.all()
    return jsonify({
        "orders": [{
            "id": order.id,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "items": [{
                "name": item.item.name,
                "quantity": item.quantity,
                "price": item.price_at_time
            } for item in order.items]
        } for order in orders]
    })

@app.route('/api/companies', methods=['GET'])
@require_auth(roles=[UserRole.ADMIN])
def get_companies():
    """Get companies endpoint"""
    companies = Company.query.all()
    return jsonify({
        "companies": [{
            "id": company.id,
            "name": company.name
        } for company in companies]
    })

@app.route('/api/companies', methods=['POST'])
@require_auth(roles=[UserRole.ADMIN])
def create_company():
    """Create new company endpoint"""
    try:
        data = CreateCompanyRequest(**request.get_json())
        company = Company(
            id=f"company_{str(uuid.uuid4())[:8]}",
            name=data.name,
            description=data.description
        )
        db.session.add(company)
        db.session.commit()
        logger.info(f"Created company: {company.id}")
        return jsonify({
            "message": "Company created successfully",
            "company_id": company.id
        })
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
