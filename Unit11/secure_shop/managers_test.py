import unittest
from config import app, db
from managers import UserManager, InventoryManager
from exceptions import ValidationError

class ManagersTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the application context and database before each test."""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Ensure the database is created for testing
        db.create_all()

    def tearDown(self):
        """Tear down the application context and database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user_invalid_password(self):
        with self.assertRaises(ValidationError):
            UserManager.create_user({"email": "test@example.com", "password": "weak"})

    def test_add_inventory_item(self):
        item_data = {
            "name": "Laptop",
            "category": "Electronics",
            "quantity": 10,
            "price": 1200.00,
            "company_id": "test_company"
        }
        item = InventoryManager.add_item(item_data)
        self.assertEqual(item.name, "Laptop")

if __name__ == '__main__':
    unittest.main()
