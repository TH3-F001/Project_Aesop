import unittest

from src.domain.entities.google_account import GoogleAccount

class TestGoogleAccount(unittest.TestCase):
    def setUp(self):
        self.valid_args = {
            'email': 'support@dell.com',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.valid_args_reloaded = {
            'email': 'support@dell.com',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 600
        }

        self.negative_quota_args = {
            'email': 'support@dell.com',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': -1
        }

        self.invalid_email_args = {
            'email': 'dell.com',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.not_initialized_email_args = {
            'email': '',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.missing_cid_args = {
            'email': 'support@dell.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.missing_secret_args = {
            'email': 'support@dell.com',
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'spent_quota': 0
        }

        self.missing_email_args = {
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.missing_quota_args = {
            'client_id': '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com',
            'client_secret': 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456',
            'spent_quota': 0
        }

        self.empty_args = {}

    def tearDown(self):
        pass

    def test_initialization(self):
        # Fail Invalid input
        self.assertRaises(ValueError, GoogleAccount, self.invalid_email_args)
        self.assertRaises(ValueError, GoogleAccount, self.missing_cid_args)
        self.assertRaises(ValueError, GoogleAccount, self.missing_secret_args)

        # Allow Missing Emails, but not invalid ones
        try:
            gaccount = GoogleAccount(self.missing_email_args)
        except ValueError as e:
            self.fail(f"Wrongly denied empty email argument{e}")
        try:
            gaccount = GoogleAccount(self.not_initialized_email_args)
        except ValueError as e:
            self.fail(f"Wrongly denied non-initialized email argument{e}")


        # Make sure valid arguments work
        try:
            gaccount = GoogleAccount(self.valid_args)
        except ValueError as e:
            self.fail(f"Wrongly denied valid arguments{e}\n{self.valid_args}")
        try:
            gaccount = GoogleAccount(self.valid_args_reloaded)
        except ValueError as e:
            self.fail(f"Wrongly denied valid arguments{e}\n{self.valid_args_reloaded}")
        try:
            gaccount = GoogleAccount(self.missing_quota_args)
        except ValueError as e:
            self.fail(f"Wrongly denied valid arguments{e}\n{self.missing_quota_args}")

        # Make sure quota is properly initialized
        self.assertEqual(GoogleAccount(self.missing_quota_args).get_spent_quota(), 0)
        self.assertEqual(GoogleAccount(self.valid_args_reloaded).get_spent_quota(), 600)
        self.assertEqual(GoogleAccount(self.negative_quota_args).get_spent_quota(), 0)






if __name__ == '__main__':
    unittest.main()

