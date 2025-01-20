import unittest
from exceptions import ValidationError

class ExceptionsTestCase(unittest.TestCase):
    def test_custom_exception(self):
        with self.assertRaises(ValidationError):
            raise ValidationError("This is a validation error")

if __name__ == '__main__':
    unittest.main()
