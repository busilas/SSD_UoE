import unittest
from config import app, db, redis_client

class ConfigTestCase(unittest.TestCase):
    def test_secret_key_exists(self):
        self.assertTrue('SECRET_KEY' in app.config)

    def test_database_uri_set(self):
        self.assertTrue('SQLALCHEMY_DATABASE_URI' in app.config)

    def test_redis_client_connection(self):
        self.assertIsNotNone(redis_client)

if __name__ == '__main__':
    unittest.main()
