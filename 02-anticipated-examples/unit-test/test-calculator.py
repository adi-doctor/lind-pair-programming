import unittest
from calculator import add, divide


class TestCalculator(unittest.TestCase):

    def setUp(self):
        """Runs before each test method."""
        pass

    def tearDown(self):
        """Runs after each test method."""
        pass

    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

    def test_divide_valid(self):
        self.assertEqual(divide(10, 2), 5)
        self.assertAlmostEqual(divide(1, 3), 0.3333333, places=6)

    def test_divide_by_zero_raises_exception(self):
        with self.assertRaises(ValueError) as context:
            divide(10, 0)
        self.assertIn("Cannot divide by zero", str(context.exception))


if __name__ == "__main__":
    unittest.main()