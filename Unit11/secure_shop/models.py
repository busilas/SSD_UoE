"""
This module defines the data models used for various operations such as user management, 
order management, inventory management, and company creation. It leverages Pydantic models 
for validation and transformation, ensuring data integrity and consistency across different 
operations such as login, user creation, and order handling.
"""

from pydantic import BaseModel, Field, EmailStr, StringConstraints, field_validator
from typing import List, Dict, Optional, Annotated
from enums import UserRole, OrderStatus


## Models

# Login Request Models
class LoginRequest(BaseModel):
    """
    This class represents the data model for user login requests.
    
    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password (12-100 characters long).
    """
    email: EmailStr
    password: Annotated[str, Field(min_length=12, max_length=100)]

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"LoginRequest": LoginRequest}


class OTPVerificationRequest(BaseModel):
    """
    This class represents the data model for OTP verification requests.

    Attributes:
        user_id (int): The user ID for OTP verification.
        otp (str): A 6-digit OTP for verification.
    """
    user_id: int
    otp: Annotated[str, Field(min_length=6, max_length=6)]

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"OTPVerificationRequest": OTPVerificationRequest}


# User Management Models
class CreateUserRequest(BaseModel):
    """
    This class represents the data model for user creation requests.
    
    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password (12-100 characters long).
        forename (str): The user's first name.
        surname (str): The user's last name.
        role (UserRole): The role of the user (Admin, User, etc.).
        company_id (str): The company ID the user is associated with.
    """
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=12, max_length=100)]
    forename: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    surname: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    role: UserRole
    company_id: str

    @field_validator('password', mode="after")
    def validate_password_complexity(cls, v: str) -> str:
        """
        Validates that the password contains at least one uppercase letter,
        one lowercase letter, one digit, and one special character.

        Args:
            v (str): The password string to validate.

        Returns:
            str: The validated password string.

        Raises:
            ValueError: If the password does not meet complexity requirements.
        """
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"CreateUserRequest": CreateUserRequest}


# Inventory Management Models
class CreateInventoryItemRequest(BaseModel):
    """
    This class represents the data model for creating new inventory items.

    Attributes:
        name (str): The name of the inventory item (1-255 characters long).
        description (str, optional): The description of the inventory item (max 1000 characters).
        category (str): The category the item belongs to (1-100 characters long).
        quantity (int): The quantity of the inventory item (must be >= 0).
        price (float): The price of the inventory item (must be > 0).
    """
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Optional[Annotated[str, Field(max_length=1000)]]
    category: Annotated[str, Field(min_length=1, max_length=100)]
    quantity: Annotated[int, Field(ge=0)]  # Greater than or equal to 0
    price: Annotated[float, Field(gt=0)]  # Greater than 0

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"CreateInventoryItemRequest": CreateInventoryItemRequest}


class UpdateInventoryQuantityRequest(BaseModel):
    """
    This class represents the data model for updating the quantity of an inventory item.

    Attributes:
        quantity (int): The new quantity of the inventory item (must be >= 0).
    """
    quantity: Annotated[int, Field(ge=0)]  # Greater than or equal to 0

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"UpdateInventoryQuantityRequest": UpdateInventoryQuantityRequest}


# Order Management Models
class OrderItemRequest(BaseModel):
    """
    This class represents an individual item in an order request.

    Attributes:
        item_id (str): The ID of the item.
        quantity (int): The quantity of the item ordered (must be > 0).
    """
    item_id: str
    quantity: Annotated[int, Field(gt=0)]  # Greater than 0

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"OrderItemRequest": OrderItemRequest}


class CreateOrderRequest(BaseModel):
    """
    This class represents the data model for creating an order request.

    Attributes:
        items (List[OrderItemRequest]): A list of items in the order.
    """
    items: List[OrderItemRequest]

    @field_validator('items', mode='after')
    def validate_items_not_empty(cls, v: List[OrderItemRequest]) -> List[OrderItemRequest]:
        """
        Validates that the order contains at least one item.

        Args:
            v (List[OrderItemRequest]): List of order items.

        Returns:
            List[OrderItemRequest]: The validated list of items.

        Raises:
            ValueError: If the order contains no items.
        """
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"CreateOrderRequest": CreateOrderRequest}


class UpdateOrderStatusRequest(BaseModel):
    """
    This class represents the data model for updating the status of an order.

    Attributes:
        status (OrderStatus): The new status of the order.
    """
    status: OrderStatus

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"UpdateOrderStatusRequest": UpdateOrderStatusRequest}


# Company Management Models
class CreateCompanyRequest(BaseModel):
    """
    This class represents the data model for creating a new company.

    Attributes:
        name (str): The name of the company (1-255 characters long).
        description (str, optional): The description of the company (max 1000 characters).
    """
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Optional[Annotated[str, Field(max_length=1000)]]

    @staticmethod
    def get_model_functions() -> dict:
        """
        Return function references for this model to be used in other files.

        Returns:
            dict: A dictionary containing method references for the class.
        """
        return {"CreateCompanyRequest": CreateCompanyRequest}
