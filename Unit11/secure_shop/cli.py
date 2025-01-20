"""
This is the command-line interface (CLI) for the SecureShop system, which is designed to 
allow Admins, Clerks, and Customers to interact with the platform through a terminal interface. 
The menu allows users to perform tasks such as logging in, managing inventory, viewing orders, 
and performing authentication via OTP (one-time password). It provides robust error handling 
and session management to ensure a secure and smooth user experience.
"""

import uuid
import jwt
import logging
import traceback
from datetime import datetime, UTC
from config import db, config, logger
from security import SecurityConfig
from managers import UserManager, SessionManager, MFAManager, InventoryManager, OrderManager
from exceptions import ValidationError, AuthenticationError
from enums import UserRole, OrderStatus, AccountStatus
from managers import session_manager
from database import User, Company, InventoryItem, Order, OrderItem


## CLI Interface
class CLI:
    """Command-Line Interface for SecureShop.

    This class handles user interactions, including login and navigation
    of role-specific menus. Logs events and errors to a dedicated file.

    Attributes:
        current_user (dict): Information about the currently logged-in user.
        user_manager (UserManager): Manages user-related operations.
        logger (logging.Logger): Logs events and errors to 'cli.log'.
    """

    def __init__(self):
        """Initialize the CLI interface and set up logging."""
        self.current_user = None  # Store the currently logged-in user's details
        self.user_manager = UserManager()  # Initialize user manager for authentication

        # Configure CLI-specific logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG for detailed logs

        # Create a file handler for logging
        handler = logging.FileHandler('cli.log')  # Log events to 'cli.log'
        handler.setLevel(logging.DEBUG)

        # Create and set a log message format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)  # Add handler to the logger

        self.logger.info("CLI interface initialized")  # Log initialization message

    def display_menu(self):
        """Display the main menu and handle user input.

        Provides options for login and exiting the application.
        Includes error handling for invalid input and unexpected issues.
        """
        while True:
            try:
                # Display the main menu options
                print("\n=== SecureShop ===")
                print("1. Login")
                print("2. Exit")

                # Get user input for menu choice
                choice = input("\nChoice: ").strip()

                if choice == "1":
                    try:
                        self.handle_login()  # Attempt to handle user login
                    except Exception as e:
                        # Log and display any errors that occur during login
                        self.logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
                        print(f"Login error: {str(e)}")
                elif choice == "2":
                    # Exit the application
                    print("\nThank you for using SecureShop. Goodbye!")
                    break
                else:
                    # Handle invalid menu choice
                    print("\nInvalid choice. Please enter 1 or 2.")
            except KeyboardInterrupt:
                # Gracefully handle a keyboard interrupt (Ctrl+C)
                print("\n\nShutting down safely...")
                break
            except Exception as e:
                # Log and display unexpected errors
                self.logger.error(f"Menu error: {str(e)}\n{traceback.format_exc()}")
                print("\nAn unexpected error occurred. Please try again.")

    def handle_login(self):
        """Authenticate the user and handle login flow.

        Prompts the user for email and password, performs authentication,
        and verifies OTP. Allows up to three attempts before locking out.

        Logs detailed information about login attempts and errors.

        Raises:
            AuthenticationError: If authentication fails.
        """
        MAX_ATTEMPTS = 3  # Maximum allowed login attempts
        attempts = 0  # Track the number of login attempts

        while attempts < MAX_ATTEMPTS:
            try:
                self.logger.debug("Starting login attempt")  # Log the start of a login attempt

                # Prompt user for email and password
                email = input("Email: ").strip()
                password = input("Password: ").strip()

                if not email or not password:
                    # Check if email or password is empty
                    print("Email and password cannot be empty.")
                    continue

                self.logger.debug(f"Attempting authentication for email: {email}")  # Log email
                auth_result = self.user_manager.authenticate_user(email, password)  # Authenticate user
                self.logger.debug(f"Authentication successful, got auth result: {auth_result}")

                # Prompt user for OTP
                otp = input("Enter verification code: ").strip()

                # Verify OTP and login
                token = self.user_manager.verify_otp_and_login(auth_result['user_id'], otp)

                # Decode JWT token to get user details
                decoded_token = jwt.decode(token, SecurityConfig.JWT_SECRET, algorithms=["HS256"])

                # Store current user details
                self.current_user = {
                    'user_id': decoded_token['user_id'],
                    'email': decoded_token['email'],
                    'role': decoded_token['role'],
                    'company_id': decoded_token['company_id']
                }

                self.logger.debug(f"Login successful for user: {self.current_user['email']}")  # Log success
                print("Login successful.")

                # Navigate to role-specific menu
                if self.current_user['role'] == UserRole.ADMIN.value:
                    self.display_admin_menu()  # Admin menu
                elif self.current_user['role'] == UserRole.CLERK.value:
                    self.display_clerk_menu()  # Clerk menu
                elif self.current_user['role'] == UserRole.CUSTOMER.value:
                    self.display_customer_menu()  # Customer menu
                return

            except AuthenticationError as e:
                # Handle authentication failure
                self.logger.warning(f"Authentication failed: {str(e)}")  # Log warning
                attempts += 1
                remaining = MAX_ATTEMPTS - attempts
                print(f"Authentication failed: {str(e)}")
                if remaining > 0:
                    print(f"You have {remaining} attempts remaining.")  # Notify remaining attempts
                continue

            except Exception as e:
                # Handle unexpected errors during login
                self.logger.error(f"Unexpected login error: {str(e)}\n{traceback.format_exc()}")
                print(f"An error occurred: {str(e)}")
                attempts += 1
                continue

        if attempts >= MAX_ATTEMPTS:
            # Notify user of too many failed attempts
            self.logger.warning("Maximum login attempts exceeded")
            print("Too many failed login attempts. Please try again later.")

    # Display Admin Menu
    def display_admin_menu(self):
        """
        Displays the admin menu interface, allowing the admin to perform various operations 
        related to company and user management, as well as system log viewing. 
        """
        while True:
            # Display the main menu options for admin
            print("\n=== Admin Menu ===")
            print("1. Add Company")
            print("2. Edit Company")
            print("3. Delete Company")
            print("4. Create User")
            print("5. Edit User")
            print("6. View Users")
            print("7. Delete User")
            print("8. View System Logs")
            print("9. Logout")

            try:
                choice = input("Choice: ")

                if choice == "1":
                    try:
                        # Add a new company
                        name = input("Enter company name: ").strip()
                        # Ensure the company name is not empty
                        if not name:
                            print("Company name cannot be empty.")
                            continue
                            
                        # Create and save the company object   
                        description = input("Enter company description (optional): ").strip()
                        company_id = f"company_{str(uuid.uuid4())[:8]}"  # Generate a unique company ID
                        
                        # Create new company with all required fields
                        company = Company(
                            id=company_id,
                            name=name,
                            description=description if description else None,
                            status="active",  # Default status is active
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC)
                        )
                        
                        db.session.add(company)
                        db.session.commit()  # Commit changes to the database
                        print(f"Company '{name}' added successfully with ID: {company_id}")
                        self.logger.info(f"Created new company: {name} ({company_id})")
                    except ValidationError as e:
                        # Handle validation errors
                        print(f"Validation error: {str(e)}")
                        db.session.rollback()
                    except Exception as e:
                        # Handle other exceptions during company creation
                        print(f"Error creating company: {str(e)}")
                        self.logger.error(f"Company creation error: {str(e)}\n{traceback.format_exc()}")
                        db.session.rollback()

                elif choice == "2":
                    try:
                        # Edit existing company details
                        companies = Company.query.all()  # Fetch all companies
                        print("\nAvailable Companies:")
                        for company in companies:
                            print(f"ID: {company.id}, Name: {company.name}, Status: {company.status}")
                            
                        company_id = input("\nEnter company ID to edit: ").strip()
                        company = Company.query.get(company_id)  # Fetch the company by ID
                        
                        if company:
                            # Display current company details
                            print("\nCurrent Values:")
                            print(f"Name: {company.name}")
                            print(f"Description: {company.description}")
                            print(f"Status: {company.status}")
                            
                            # Allow editing of company attributes
                            new_name = input("\nEnter new name (or press Enter to keep current): ").strip()
                            new_desc = input("Enter new description (or press Enter to keep current): ").strip()
                            new_status = input("Enter new status (active/inactive/suspended, or press Enter to keep current): ").strip().lower()
                            
                            # Update fields if new values are provided
                            if new_name:
                                company.name = new_name
                            if new_desc:
                                company.description = new_desc
                            if new_status in ['active', 'inactive', 'suspended']:
                                company.status = new_status
                                
                            company.updated_at = datetime.now(UTC)  # Update the timestamp
                            db.session.commit()  # Commit changes to the database
                            print(f"Company '{company_id}' updated successfully.")
                            self.logger.info(f"Updated company: {company_id}")
                        else:
                            # Handle case where company is not found
                            print("Company not found.")
                    except Exception as e:
                        # Handle errors during company update
                        print(f"Error updating company: {str(e)}")
                        self.logger.error(f"Company update error: {str(e)}\n{traceback.format_exc()}")
                        db.session.rollback()

                elif choice == "3":
                    try:
                        # Delete an existing company
                        companies = Company.query.all()  # Fetch all companies
                        print("\nAvailable Companies:")
                        for company in companies:
                            print(f"ID: {company.id}, Name: {company.name}")
                        
                        company_id = input("\nEnter company ID to delete: ").strip()
                        if company_id == 'default_company':
                            # Prevent deletion of the default company
                            print("Cannot delete the default company.")
                            continue
                            
                        company = Company.query.get(company_id)  # Fetch the company by ID
                        if company:
                            # Ensure the company has no associated users before deletion
                            if company.users:
                                print("Cannot delete company with existing users. Please reassign or delete users first.")
                                continue
                                
                            db.session.delete(company)  # Delete the company
                            db.session.commit()  # Commit the changes
                            print(f"Company '{company_id}' deleted successfully.")
                            self.logger.info(f"Deleted company: {company_id}")
                        else:
                            # Handle case where company is not found
                            print("Company not found.")
                    except Exception as e:
                        # Handle errors during company deletion
                        print(f"Error deleting company: {str(e)}")
                        self.logger.error(f"Company deletion error: {str(e)}\n{traceback.format_exc()}")
                        db.session.rollback()

                elif choice == "4":
                    try:
                        # Create a new user
                        print("\n=== Create New User ===")
                        email = input("Enter user email: ").strip()
                        password = input("Enter password: ").strip()
                        forename = input("Enter first name: ").strip()
                        surname = input("Enter last name: ").strip()
                        
                        # Display available roles for the user
                        print("\nAvailable roles:")
                        for role in UserRole:
                            print(f"- {role.value}")
                        role = input("Enter role: ").strip().upper()
                        
                        # Display active companies for user assignment
                        companies = Company.query.filter_by(status='active').all()
                        print("\nAvailable Companies:")
                        for company in companies:
                            print(f"ID: {company.id}, Name: {company.name}")
                        
                        company_id = input("\nEnter company ID (press Enter for default company): ").strip()
                        if not company_id:
                            company_id = 'default_company'
                        
                        # Ensure all required fields are provided
                        if not all([email, password, forename, surname, role]):
                            print("All fields are required.")
                            continue
                        
                        user_data = {
                            "email": email,
                            "password": password,
                            "forename": forename,
                            "surname": surname,
                            "role": role,
                            "company_id": company_id
                        }
                        
                        # Create the user and commit the transaction
                        user = UserManager.create_user(user_data)
                        print(f"User '{email}' created successfully.")
                        self.logger.info(f"Created new user: {email}")
                    except ValidationError as e:
                        # Handle validation errors
                        print(f"Validation error: {str(e)}")
                    except Exception as e:
                        # Handle general errors during user creation
                        print(f"Error creating user: {str(e)}")
                        self.logger.error(f"User creation error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "5":
                    try:
                        # Edit an existing user details
                        users = User.query.all()  # Display available users
                        print("\nAvailable Users:")
                        for user in users:
                            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role.value}, Status: {user.status.value}")
                        
                        user_id = input("\nEnter user ID to edit: ").strip()
                        user = User.query.get(int(user_id))  # Fetch user by ID
                        
                        if user:
                            # Display current user values
                            print("\nCurrent Values:")
                            print(f"Email: {user.email}")
                            print(f"Name: {user.forename} {user.surname}")
                            print(f"Role: {user.role.value}")
                            print(f"Status: {user.status.value}")
                            
                            # Prompt to update user details
                            new_forename = input("\nEnter new first name (or press Enter to keep current): ").strip()
                            new_surname = input("Enter new last name (or press Enter to keep current): ").strip()
                            new_role = input("Enter new role (or press Enter to keep current): ").strip().upper()
                            new_status = input("Enter new status (ACTIVE/SUSPENDED/INACTIVE, or press Enter to keep current): ").strip().upper()
                            
                            # Update the user attributes if new values are provided
                            if new_forename:
                                user.forename = new_forename
                            if new_surname:
                                user.surname = new_surname
                            if new_role in UserRole._value2member_map_:
                                user.role = UserRole(new_role)
                            if new_status in AccountStatus._value2member_map_:
                                user.status = AccountStatus(new_status)
                                
                            user.updated_at = datetime.now(UTC)  # Update timestamp
                            db.session.commit()  # Commit changes to the database
                            print(f"User '{user.email}' updated successfully.")
                            self.logger.info(f"Updated user: {user.email}")
                        else:
                            print("User not found.")
                    except Exception as e:
                        # Handle errors during user update
                        print(f"Error updating user: {str(e)}")
                        self.logger.error(f"User update error: {str(e)}\n{traceback.format_exc()}")
                        db.session.rollback()

                elif choice == "6":
                    try:
                        # Display all users
                        users = User.query.all()
                        print("\n=== Users ===")
                        print("ID  | Email | Role | Status | Company | Name")
                        print("-" * 80)
                        for user in users:
                            print(f"{user.id:<4} | {user.email:<20} | {user.role.value:<8} | {user.status.value:<8} | "
                                  f"{user.company.name:<15} | {user.forename} {user.surname}")
                    except Exception as e:
                        # Handle errors during user listing
                        print(f"Error viewing users: {str(e)}")
                        self.logger.error(f"User view error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "7":
                    try:
                        # Delete a user from the system by their ID
                        users = User.query.all()  # Display available users
                        print("\nAvailable Users:")
                        for user in users:
                            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role.value}")
                        
                        user_id = input("\nEnter user ID to delete: ").strip()
                        user = User.query.get(int(user_id))  # Fetch user by ID
                        
                        if user:
                            # Prevent deletion of the default admin user
                            if user.email == config('DEFAULT_ADMIN_EMAIL', default='admin@example.com'):
                                print("Cannot delete the default admin user.")
                                continue
                                
                            db.session.delete(user)  # Delete the user
                            db.session.commit()  # Commit the changes
                            print(f"User '{user.email}' deleted successfully.")
                            self.logger.info(f"Deleted user: {user.email}")
                        else:
                            print("User not found.")
                    except Exception as e:
                        # Handle errors during user deletion
                        print(f"Error deleting user: {str(e)}")
                        self.logger.error(f"User deletion error: {str(e)}\n{traceback.format_exc()}")
                        db.session.rollback()

                elif choice == "8":
                    try:
                        # Display the system logs
                        print("\n=== System Logs ===")  # Display last 10 log entries
                        print("Last 10 entries:")
                        with open("shop.log", "r") as log_file:
                            lines = log_file.readlines()  # Read all lines from the log file
                            for line in lines[-10:]:
                                print(line.strip())

                        # Prompt for more log entries if needed        
                        view_more = input("\nView more logs? (y/n): ").strip().lower()
                        if view_more == 'y':
                            print("\nComplete logs:")
                            for line in lines:
                                print(line.strip())
                    except FileNotFoundError:
                        # Handle case where the log file is not found
                        print("No log file found.")
                    except Exception as e:
                        # Handle errors during log reading
                        print(f"Error reading logs: {str(e)}")
                        self.logger.error(f"Log reading error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "9":
                    # Logs out and terminates the session
                    print("Logging out...")
                    self.current_user = None  # Clear the current user session
                    break  # Exit the loop to log out

                else:
                    # Handle invalid choice from the menu
                    print("Invalid choice. Please try again.")

            except Exception as e:
                # Log and display errors occurring in the menu loop
                self.logger.error(f"Error in admin menu: {str(e)}\n{traceback.format_exc()}")
                print("An error occurred. Please try again.")

    # Display Clerk Menu
    def display_clerk_menu(self):
        while True:
            try:
                # Display Clerk Menu options
                print("\n=== Clerk Menu ===")
                print("1. Add Inventory Item")
                print("2. Update Inventory")
                print("3. View Inventory")
                print("4. View Orders")
                print("5. Update Order Status")
                print("6. Logout")

                # Get user choice
                choice = input("\nChoice: ").strip()

                if choice == "1":
                    """Add a new inventory item to the system."""
                    try:
                        # Prompt for item details
                        print("\n=== Add New Item ===")
                        name = input("Enter item name: ").strip()
                        if not name:
                            print("Item name cannot be empty.")
                            continue
                            
                        description = input("Enter item description (optional): ").strip()
                        category = input("Enter item category: ").strip()
                        if not category:
                            print("Category cannot be empty.")
                            continue

                        # Validate quantity input
                        try:
                            quantity = int(input("Enter quantity: ").strip())
                            if quantity < 0:
                                print("Quantity cannot be negative.")
                                continue
                        except ValueError:
                            print("Quantity must be a number.")
                            continue

                        # Validate price input
                        try:
                            price = float(input("Enter price: ").strip())
                            if price <= 0:
                                print("Price must be greater than 0.")
                                continue
                        except ValueError:
                            print("Price must be a number.")
                            continue

                        # Collect item data and attempt to add the item to the inventory
                        item_data = {
                            "name": name,
                            "description": description,
                            "category": category,
                            "quantity": quantity,
                            "price": price,
                            "company_id": self.current_user["company_id"]
                        }
                        
                        # Call inventory manager to add the item
                        item = InventoryManager.add_item(item_data)
                        print(f"\nItem '{name}' added successfully with ID: {item.id}")
                        self.logger.info(f"Clerk {self.current_user['email']} added new item: {name}")
                    except ValidationError as e:
                        # Handle validation errors
                        print(f"Validation error: {str(e)}")
                    except Exception as e:
                        # Handle general errors during item addition
                        print(f"Error adding item: {str(e)}")
                        self.logger.error(f"Item addition error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "2":
                    """Update an existing inventory item's quantity."""
                    try:
                        # Display current inventory for the user
                        print("\n=== Update Inventory ===")
                        inventory = InventoryItem.query.filter_by(
                            company_id=self.current_user["company_id"]
                        ).all()
                        
                        if not inventory:
                            print("No items in inventory.")
                            continue
                            
                        # Show available inventory items
                        print("\nCurrent Inventory:")
                        print("ID | Name | Current Quantity | Price")
                        print("-" * 50)
                        for item in inventory:
                            print(f"{item.id} | {item.name} | {item.quantity} | ${item.price:.2f}")

                        # Get the ID of the item to update
                        item_id = input("\nEnter item ID to update: ").strip()
                        item = InventoryItem.query.get(item_id)
                        
                        if not item:
                            print("Item not found.")
                            continue
                            
                        # Get the new quantity for the selected item
                        try:
                            new_quantity = int(input("Enter new quantity: ").strip())
                            if new_quantity < 0:
                                print("Quantity cannot be negative.")
                                continue
                                
                            # Update the item's quantity in the inventory
                            item = InventoryManager.update_quantity(item_id, new_quantity)
                            print(f"\nQuantity updated successfully for '{item.name}'")
                            self.logger.info(
                                f"Clerk {self.current_user['email']} updated quantity for item {item_id}"
                            )
                        except ValueError:
                            # Handle invalid quantity input
                            print("Quantity must be a number.")
                    except Exception as e:
                        # Handle errors during inventory update
                        print(f"Error updating inventory: {str(e)}")
                        self.logger.error(f"Inventory update error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "3":
                    """View all inventory items."""
                    try:
                        # Display all inventory items
                        print("\n=== Inventory List ===")
                        inventory = InventoryItem.query.filter_by(
                            company_id=self.current_user["company_id"]
                        ).all()
                        
                        if not inventory:
                            print("No items in inventory.")
                            continue
                            
                        # Display formatted inventory list
                        print("\nID | Name | Category | Quantity | Price | Description")
                        print("-" * 80)
                        for item in inventory:
                            desc = (item.description[:30] + '...') if item.description and len(item.description) > 30 else item.description or 'N/A'
                            print(f"{item.id} | {item.name} | {item.category} | {item.quantity} | ${item.price:.2f} | {desc}")
                    except Exception as e:
                        # Handle errors when viewing inventory
                        print(f"Error viewing inventory: {str(e)}")
                        self.logger.error(f"Inventory view error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "4":
                    """View all orders placed by customers."""
                    try:
                        # Display current orders for the user
                        print("\n=== Orders List ===")
                        orders = Order.query.filter_by(
                            company_id=self.current_user["company_id"]
                        ).all()
                        
                        if not orders:
                            print("No orders found.")
                            continue
                            
                        # Show the orders and their basic information
                        print("\nOrder ID | Status | Items | Total Value | Date")
                        print("-" * 80)
                        for order in orders:
                            items_count = len(order.items)
                            total_value = sum(item.price_at_time * item.quantity for item in order.items)
                            created_at = order.created_at.strftime("%Y-%m-%d %H:%M")
                            print(f"{order.id} | {order.status.value} | {items_count} items | ${total_value:.2f} | {created_at}")
                            
                        # Get order ID for detailed view if the user wants
                        order_id = input("\nEnter order ID for details (or press Enter to skip): ").strip()
                        if order_id:
                            order = Order.query.get(order_id)
                            if order:
                                # Display detailed information about the selected order
                                print(f"\nOrder Details for {order_id}:")
                                print("Item | Quantity | Price | Total")
                                print("-" * 50)
                                for item in order.items:
                                    total = item.price_at_time * item.quantity
                                    print(f"{item.item.name} | {item.quantity} | ${item.price_at_time:.2f} | ${total:.2f}")
                            else:
                                print("Order not found.")
                    except Exception as e:
                        # Handle errors during order viewing
                        print(f"Error viewing orders: {str(e)}")
                        self.logger.error(f"Order view error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "5":
                    """Update the status of an order."""
                    try:
                        # Display current orders for status update
                        print("\n=== Update Order Status ===")
                        orders = Order.query.filter_by(
                            company_id=self.current_user["company_id"]
                        ).all()
                        
                        if not orders:
                            print("No orders found.")
                            continue
                            
                        # Show order information
                        print("\nCurrent Orders:")
                        print("Order ID | Current Status | Date")
                        print("-" * 50)
                        for order in orders:
                            created_at = order.created_at.strftime("%Y-%m-%d %H:%M")
                            print(f"{order.id} | {order.status.value} | {created_at}")

                        # Get order ID to update its status
                        order_id = input("\nEnter order ID to update: ").strip()
                        order = Order.query.get(order_id)
                        
                        if not order:
                            print("Order not found.")
                            continue
                            
                        # Show available statuses for the order
                        print("\nAvailable statuses:")
                        for status in OrderStatus:
                            print(f"- {status.value}")
                            
                        # Get the new status input from the user
                        new_status = input("Enter new status: ").strip().upper()
                        if new_status not in OrderStatus._value2member_map_:
                            print("Invalid status.")
                            continue
                            
                        # Update order status and log the change
                        order = OrderManager.update_status(order_id, OrderStatus(new_status))
                        print(f"\nOrder status updated successfully to {new_status}")
                        self.logger.info(
                            f"Clerk {self.current_user['email']} updated order {order_id} status to {new_status}"
                        )
                    except Exception as e:
                        # Handle errors during order status update
                        print(f"Error updating order status: {str(e)}")
                        self.logger.error(f"Order status update error: {str(e)}\n{traceback.format_exc()}")

                elif choice == "6":
                    """Logs the clerk out of the system."""
                    print("\nLogging out...")
                    session_manager.invalidate_session(self.current_user["user_id"])
                    self.current_user = None
                    break  # Exit the menu loop

                else:
                    # Handle invalid menu choices
                    print("\nInvalid choice. Please try again.")

            except KeyboardInterrupt:
                # Handle safe logout on keyboard interrupt
                print("\n\nLogging out safely...")
                session_manager.invalidate_session(self.current_user["user_id"])
                self.current_user = None
                break
            except Exception as e:
                # Log any unexpected errors
                self.logger.error(f"Clerk menu error: {str(e)}\n{traceback.format_exc()}")
                print("\nAn unexpected error occurred. Please try again.")

    # Display Cusrtomer Menu
    def display_customer_menu(self):
        cart = []  # Initialize an empty cart for the customer

        while True:
            try:
                # Display Customer Menu options
                print("\n=== Customer Menu ===")
                print("1. View Products")
                print("2. Add to Cart")
                print("3. View Cart")
                print("4. Checkout")
                print("5. View Orders")
                print("6. Cancel Order")
                print("7. Logout")

                # Get user's menu choice
                choice = input("Choice: ")

                if choice == "1":
                    """View all products available in the inventory."""
                    # Query the inventory for products related to the current user's company
                    products = InventoryItem.query.filter_by(company_id=self.current_user["company_id"]).all()
                    print("=== Products ===")
                    for product in products:
                        # Display product details such as ID, name, price, and available quantity
                        print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}, Quantity: {product.quantity}")

                elif choice == "2":
                    """Add a product to the cart."""
                    # Get product ID and quantity to add to the cart
                    product_id = input("Enter product ID to add to cart: ")
                    quantity = int(input("Enter quantity: "))

                    # Query the product from the inventory
                    product = InventoryItem.query.get(product_id)
                    if product and product.quantity >= quantity:
                        # If the product exists and there's sufficient quantity, add to the cart
                        cart.append({"product_id": product_id, "name": product.name, "quantity": quantity})
                        print(f"Added {quantity} of {product.name} to cart.")
                    else:
                        # If product not found or insufficient stock, notify the user
                        print("Product not found or insufficient quantity.")

                elif choice == "3":
                    """View the contents of the cart."""
                    # Display the contents of the cart
                    print("=== Cart ===")
                    for item in cart:
                        # Show each item in the cart with its name and quantity
                        print(f"Product: {item['name']}, Quantity: {item['quantity']}")

                elif choice == "4":
                    """Checkout and place an order."""
                    if cart:
                        # If the cart is not empty, proceed with checkout and order placement
                        OrderManager.create_order(self.current_user["user_id"], cart, self.current_user["company_id"])
                        print("Checkout successful. Order placed.")
                        cart.clear()  # Clear the cart after successful checkout
                    else:
                        # If the cart is empty, notify the user
                        print("Cart is empty.")

                elif choice == "5":
                    """View all the orders placed by the customer."""
                    # Retrieve the customer's orders from the database
                    orders = Order.query.filter_by(user_id=self.current_user["user_id"]).all()
                    print("=== Your Orders ===")
                    for order in orders:
                        # Display each order's ID and status
                        print(f"Order ID: {order.id}, Status: {order.status}")

                elif choice == "6":
                    """Cancel a specific order."""
                    # Prompt the user to input the order ID they wish to cancel
                    order_id = input("Enter order ID to cancel: ")
                    if OrderManager.cancel_order(order_id):
                        # If the order was successfully canceled, notify the user
                        print(f"Order '{order_id}' canceled successfully.")
                    else:
                        # If the order could not be canceled, notify the user
                        print("Failed to cancel order.")

                elif choice == "7":
                    """Log the customer out of the system."""
                    print("Logging out...")
                    break  # Exit the loop and logout the customer

                else:
                    # Handle invalid menu choices
                    print("Invalid choice. Please try again.")

            except Exception as e:
                # Catch and log unexpected errors during the menu interaction
                logger.error(f"Error in customer menu: {str(e)}")
                print("An error occurred. Please try again.")