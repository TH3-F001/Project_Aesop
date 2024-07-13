import unittest
from unittest.mock import Mock
from src.domain.entities.regex_email_validator import RegexEmailValidator


class TestRegexEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = RegexEmailValidator()

        self.valid_addresses = [
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
        self.invalid_addresses = [
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

    def test_valid_emails(self):
        ...

    def test_invalid_emails(self):
        ...



