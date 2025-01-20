import unittest
from enums import OrderStatus

class EnumsTestCase(unittest.TestCase):
    def test_enum_values(self):
        self.assertIn("PLACED", OrderStatus.get_statuses())
        self.assertEqual(OrderStatus.PLACED.value, "PLACED")

if __name__ == '__main__':
    unittest.main()
