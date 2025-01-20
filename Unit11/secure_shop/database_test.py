import unittest
from database import User, Company
from config import db

class DatabaseTestCase(unittest.TestCase):
    def test_user_model_constraints(self):
        user = User(email="test@example.com", forename="John", surname="Doe")
        db.session.add(user)
        db.session.rollback()
        self.assertEqual(user.email, "test@example.com")

    def test_company_name_validation(self):
        with self.assertRaises(Exception):
            company = Company(name="")
            db.session.add(company)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
