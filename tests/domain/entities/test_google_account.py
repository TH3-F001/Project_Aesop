import unittest
from src.domain.entities.google_account import GoogleAccount
from src.domain.exceptions.core_exceptions import MissingArgumentException


class TestGoogleAccount(unittest.TestCase):

    def setUp(self):
        self.email = 'support@dell.com'
        self.client_id = '0123456789100-1234567890abcdefghijklmnopqrstuv.apps.googleusercontent.com'
        self.client_secret = 'ABCDEF-GHIjKL-M1NopqRsTuVw-xYZ23456'
        self.spent_quota = 0
        self.max_quota = 10_000
        self.invalid_email = 'dell.com'
        self.initialized_quota = 600

    def tearDown(self):
        pass

    def test_initialization(self):
        # Fail Invalid input
        #Invalid Email
        self.assertRaises(ValueError, GoogleAccount, email=self.invalid_email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)

        # Missing client_id
        self.assertRaises(MissingArgumentException, GoogleAccount, email=self.email, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)

        # Missing client_secret
        self.assertRaises(MissingArgumentException, GoogleAccount, email=self.email, client_id=self.client_id, spent_quota=self.spent_quota, max_quota=self.max_quota)

        # Allow Missing Emails, but not invalid ones
        try:
            gaccount = GoogleAccount(email='', client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        except ValueError as e:
            self.fail(f"Wrongly denied non-initialized email argument{e}")

        # Make sure valid arguments work
        try:
            gaccount = GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        except ValueError as e:
            self.fail(f"Wrongly denied valid arguments{e}")

        try:
            gaccount = GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.initialized_quota, max_quota=self.max_quota)
        except ValueError as e:
            self.fail(f"Wrongly denied valid arguments{e}")

        # Make sure quota is properly initialized
        self.assertEqual(GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota).get_spent_quota(), 0)
        self.assertEqual(GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.initialized_quota, max_quota=self.max_quota).get_spent_quota(), self.initialized_quota)
        self.assertEqual(GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=-1, max_quota=self.max_quota).get_spent_quota(), 0)

    def test_getters(self):
        gaccount = GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        self.assertEqual(gaccount.get_email(), self.email)
        self.assertEqual(gaccount.get_spent_quota(), 0)
        self.assertEqual(gaccount.get_client_id(), self.client_id)
        self.assertEqual(gaccount.get_max_quota(), self.max_quota)

    def test_spend_quota(self):
        gaccount = GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        gaccount.spend_quota(20)
        self.assertEqual(gaccount.get_spent_quota(), 20)
        gaccount.reset_quota()
        self.assertEqual(gaccount.get_spent_quota(), 0)
        self.assertRaises(ValueError, gaccount.spend_quota, -1)

    def test_set_email(self):
        valid_email = "abc123@gmail.com"
        invalid_email = "abc123"
        gaccount = GoogleAccount(email=self.email, client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        self.assertRaises(ValueError, gaccount.set_email, invalid_email)
        self.assertRaises(ValueError, gaccount.set_email, valid_email)
        gaccount = GoogleAccount(email='', client_id=self.client_id, client_secret=self.client_secret, spent_quota=self.spent_quota, max_quota=self.max_quota)
        gaccount.set_email(valid_email)
        self.assertRaises(ValueError, gaccount.set_email, invalid_email)
        self.assertEqual(gaccount.get_email(), valid_email)

if __name__ == '__main__':
    unittest.main()
