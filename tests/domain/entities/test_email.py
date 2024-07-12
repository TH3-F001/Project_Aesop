import unittest
from src.domain.entities.email import Email


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.valid_emails = [
            "support@dell.com",
            "email-with-dash@example.com",
            "email.with.periods@example.com",
            "email-with-long-domain-name@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk.com",
            "email-with-long-local-part-" + ("a" * 64) + "@example.com",
            "email-with-subdomain@sub.domain.example.com",
            "email-with+symbol@example.com",
            "email-with_underscore@example.com",
            "1234567890@example.com",
        ]

        # Invalid Emails
        self.invalid_emails = [
            "plainaddress",
            "missing.domain@",
            "@missing.localpart",
            "spaces in@address.com",
            "spaces@in.address.com ",
            "missing@dotcom",
            "invalid@domain..com",
            "invalid@.dotstart.com",
            "invalid@dotend.com.",
            "invalid@-hyphen-start.com",
            "invalid@hyphen-end-.com"
        ]

    def test_valid_initialization(self):
        """Test initializing with valid email addresses."""
        for email in self.valid_emails:
            with self.subTest(email=email):
                e = Email(email)
                self.assertEqual(e.get_address(), email)

    def test_invalid_initialization(self):
        """Test initializing with invalid email addresses raises ValueError."""
        for email in self.invalid_emails:
            with self.subTest(email=email):
                self.assertRaises(ValueError, Email, email)

    def test_set_address_with_valid_emails(self):
        """Test setting valid email addresses."""
        for email in self.valid_emails:
            with self.subTest(email=email):
                e = Email("initial@valid.com")
                e.set_address(email)
                self.assertEqual(e.get_address(), email)

    def test_set_address_with_invalid_emails(self):
        """Test setting invalid email addresses raises ValueError."""
        for email in self.invalid_emails:
            with self.subTest(email=email):
                e = Email("initial@valid.com")  # Initialize with a valid email
                with self.assertRaises(ValueError):
                    e.set_address(email)

    def test_get_address(self):
        """Test get_address method returns the correct email address."""
        for email in self.valid_emails:
            with self.subTest(email=email):
                e = Email(email)
                self.assertEqual(e.get_address(), email)



if __name__ == '__main__':
    unittest.main()
