import unittest
from unittest.mock import Mock
from src.domain.entities.email import Email
from src.domain.interfaces.i_email_validator import IEmailValidator
from src.domain.entities.regex_email_validator import RegexEmailValidator


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.mock_validator = Mock()



    def test_valid_initialization(self):
        """Test initializing with valid email addresses."""
        for address in self.valid_addresses:
            with self.subTest(address=address):
                self.assertEqual(Email(address, self.regex_validator).address, address)

    def test_invalid_initialization(self):
        """Test initializing with invalid email addresses raises ValueError."""
        for address in self.invalid_addresses:
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    Email(address, self.regex_validator)

    def test_set_address_with_valid_emails(self):
        """Test setting valid email addresses."""
        for address in self.valid_addresses:
            with self.subTest(address=address):
                e = Email("initial@valid.com")
                e.address = address
                self.assertEqual(e.address, address)

    def test_set_address_with_invalid_emails(self):
        """Test setting invalid email addresses raises ValueError."""
        for address in self.invalid_addresses:
            with self.subTest(address=address):
                e = Email("initial@valid.com")  # Initialize with a valid email
                with self.assertRaises(ValueError):
                    e.address = address

    def test_get_address(self):
        """Test get_address method returns the correct email address."""
        for address in self.valid_addresses:
            with self.subTest(address=address):
                e = Email(address)
                self.assertEqual(e.address, address)

    def test_email_case_sensitivity(self):
        e = Email('CapSensitive@GMAIL.com')
        self.assertEqual(e.address, 'capsensitive@gmail.com')

    def test_email_char_limit(self):
        long_address = f"{'abc'*83}@gmail.com"
        with self.assertRaises(ValueError):
            Email(long_address)




if __name__ == '__main__':
    unittest.main()
