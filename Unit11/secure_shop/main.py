"""
This script serves as the entry point for initializing and running the application. It performs 
database setup, creates default data (such as a company and an admin user), starts an API server 
in a separate thread, and runs a command-line interface (CLI) to interact with the system.
"""

from threading import Thread
from config import app, db, config
from database import create_default_company, create_default_admin
from cli import CLI

## Application Entry Point
def main():
    """
    The main function is the entry point for starting the application. It handles 
    the following tasks:
    1. Initializes the database and creates necessary tables.
    2. Creates default company and admin records.
    3. Starts the API server in a separate thread to handle incoming requests.
    4. Runs a command-line interface (CLI) for managing the application.

    This function encapsulates the core setup and execution flow for the application.

    Steps:
    - Database tables are created within the application context.
    - Default data is added to ensure the system starts with essential records.
    - API server is launched asynchronously to allow parallel execution.
    - CLI menu is displayed for interaction.
    """
    # Create database tables and initialize default data
    with app.app_context():  # Ensure database operations are within app context
        db.create_all()  # Creates all tables defined in the models
        create_default_company()  # Initializes a default company record
        create_default_admin()  # Initializes a default admin user record

    # Start API server in a separate thread
    api_thread = Thread(target=app.run, kwargs={
        #'host': config('HOST', default='0.0.0.0'),  # Default host is '0.0.0.0' for external access
        'host': config('HOST', default='127.0.0.1'), # Default host is '127.0.0.1' for Bandit access
        'port': config('PORT', default=5000, cast=int),  # Default port is 5000
        'debug': config('DEBUG', default=False, cast=bool)  # Debug mode can be enabled via config
    })
    api_thread.daemon = True  # Ensures the thread exits when the main program ends
    api_thread.start()  # Start the API server asynchronously in the background

    # Run the CLI interface
    with app.app_context():  # Add app context for CLI commands
        cli = CLI()  # Create an instance of the CLI interface
        cli.display_menu()  # Display the CLI menu to the user

    # Returning any useful functions or references for future imports
    return {
        "main": main,
        "api_thread": api_thread,
        "cli": cli
    }

# Ensuring that the application starts only when the script is executed directly (not imported)
if __name__ == '__main__':
    main()
