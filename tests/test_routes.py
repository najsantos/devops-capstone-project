"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app
from service import talisman

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    def get_account_count(self):
        """Count the current number of accounts"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_read_an_account(self):
        """It should Read an Account"""

        # Make a self.client.post() call to accounts to create a new account, passing in some account data.
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get back the account id that was generated from the json.
        account.id = response.get_json()["id"]

        # Make a self.client.get() call to /accounts/{id} passing in that account id.
        response = self.client.get(f"{BASE_URL}/{account.id}")

        # Assert that the return code was HTTP_200_OK, to verify that the request was successful.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the json that was returned and assert that it is equal to the data that you sent.
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_read_account_not_found(self):
        """Attempt to read non-existing account, should return account not found"""

        # Make a self.client.get() call to /accounts/{id} passing in an invalid account id 0
        response = self.client.get(f"{BASE_URL}/0")

        # Assert that the return code was HTTP_404_NOT_FOUND
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account(self):
        """It should Update an existing Account"""

        # Make a self.client.post() call to accounts to create a new account, passing in some account data.
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the account with different data
        new_account = response.get_json()
        new_account["name"] = "John Doe"

        # Make a self.client.put() call to /accounts/{id} passing in that account id.
        response = self.client.put(f"{BASE_URL}/{new_account['id']}", json=new_account)

        # Assert that the return code was HTTP_200_OK, to verify that the request was successful.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the json that was returned and assert that it is equal to the data that you sent.
        updated_account = response.get_json()
        self.assertEqual(updated_account["name"], "John Doe")

    def test_update_account_not_found(self):
        """Attempt to update non-existing account, should return not found"""

        # Make a self.client.put() call to /accounts/{id} passing in an invalid account id 0
        account = AccountFactory()
        response = self.client.put(f"{BASE_URL}/0", json=account.serialize())

        # Assert that the return code was HTTP_404_NOT_FOUND
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_accounts(self):
        """It should Get the list of Accounts"""

        # Create five accounts with Account Factory
        self._create_accounts(5)

        # Make a self.client.get() call to /accounts to read all accounts
        response = self.client.get(BASE_URL)

        # Assert that the return code was HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check five accounts were returned
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_delete_account(self):
        """It should Delete an Account"""

        # Create five accounts with Account Factory
        accounts = self._create_accounts(5)
        account_count = self.get_account_count()
        self.assertEqual(account_count, 5)

        # Delete one of the accounts
        test_account = accounts[0]
        response = self.client.delete(f"{BASE_URL}/{test_account.id}")

        # Assert that the return code was HTTP_204_NO_CONTENT and no data was sent.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # Attempt to read account to verify deletion
        response = self.client.get(f"{BASE_URL}/{test_account.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_account_count()
        self.assertEqual(new_count, account_count - 1)

    def test_security_headers(self):
        """It should return security headers"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': 'default-src \'self\'; object-src \'none\'',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        for key, value in headers.items():
            self.assertEqual(response.headers.get(key), value)
