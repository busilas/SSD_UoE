import unittest
from config import app

class ApiRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_login_route_invalid(self):
        response = self.client.post('/api/auth/login', json={"email": "invalid", "password": "wrong"})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
