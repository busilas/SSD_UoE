import unittest
from security import AuthService, SecurityConfig
import jwt
import time

class SecurityTestCase(unittest.TestCase):
    def test_create_and_verify_token(self):
        token = AuthService.create_token({"user_id": 1})
        decoded = jwt.decode(token, SecurityConfig.JWT_SECRET, algorithms=["HS256"])
        self.assertEqual(decoded["user_id"], 1)

    def test_expired_token(self):
        # Manually create an expired token
        payload = {"user_id": 1, "exp": int(time.time()) - 10}
        expired_token = jwt.encode(payload, SecurityConfig.JWT_SECRET, algorithm="HS256")

        with self.assertRaises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, SecurityConfig.JWT_SECRET, algorithms=["HS256"])

if __name__ == '__main__':
    unittest.main()
