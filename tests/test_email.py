import unittest
from src.domain.entities.email import Email


class TestEmail(unittest.TestCase):
    def test_email_is_valid(self):
        self.assertTrue(Email.email_is_valid("support@dell.com"))
        self.assertFalse(Email.email_is_valid("thatboyaintright.com"))
        self.assertFalse(Email.email_is_valid("dontyell@bobby."))
        self.assertFalse(Email.email_is_valid("got.damnit.bobby"))
        self.assertFalse(Email.email_is_valid("king@thehill"))
        self.assertRaises(TypeError, Email.email_is_valid, 1)


if __name__ == '__main__':
    unittest.main()
