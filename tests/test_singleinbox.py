import json
import os
from unittest import TestCase
from unittest.mock import patch

import requests
from pycuc.japi import UnityAPI
from singleinbox import get_username_password


def fetch_test_file(file):
    """
    Fetches a test file content and returns in bytes
    :param file: A properly formatted html file to fetch
    :return: File returned as bytes
    """
    fn = os.path.join(os.path.dirname(__file__), file)
    with open(fn, mode='r') as infile:
        return infile.read().encode('utf-8')


class UnityAPITests(TestCase):
    def setUp(self):
        self.api = UnityAPI('user', 'password', 'https://cucm.api')

    def test_construct_url_oneitem(self):
        uri = self.api._construct_uri_from_list(['vmrest'])

        self.assertEqual(uri, (self.api.base_url + '/vmrest'))

    def test_construct_url_multiple(self):
        uri = self.api._construct_uri_from_list(['vmrest', 'locations', 'connectionlocations'])

        self.assertEqual(uri, (self.api.base_url + '/vmrest/locations/connectionlocations'))

    def test_construct_url_handles_leading_slash(self):
        uri = self.api._construct_uri_from_string("/removeleadingslash")
        self.assertEqual(uri, 'https://cucm.api/removeleadingslash')

    def test_return_session_object(self):
        session = self.api.session

        self.assertIsInstance(session, requests.Session)


@patch('singleinbox.UnityAPI._get', autospec=True)
class UnityAPIPatchTests(TestCase):
    """
    This test class is used to patch the _get function of the UnityAPI
    """

    def setUp(self):
        self.api = UnityAPI('user', 'password', 'https://cucm.api')

    def test_get_raises_exception_on_incorrect_pass(self, mock_api):
        with self.assertRaises(TypeError):
            self.api.get(1)
        self.assertEqual(mock_api.call_count, 0)

    def test_get_formats_string(self, mock_api):
        self.api.get("string")
        mock_api.assert_called_once_with(self.api, "https://cucm.api/string")

    def test_get_formats_list(self, mock_api):
        self.api.get(['one', 'two', 'three'])
        mock_api.assert_called_once_with(self.api, "https://cucm.api/one/two/three")

    def test_get_specific_user_config(self, mock_api):
        # Setup our fake user
        fake_user_config = requests.Response()
        fake_user_config._content = fetch_test_file("files/test_user_ldap.json")
        fake_user_config.status_code = 200
        mock_api.return_value = fake_user_config

        response = self.api._get_user_config_by_objectid("test_user")

        self.assertEqual(response["LdapType"], "3")
        mock_api.assert_called_once_with(self.api, "https://cucm.api/vmrest/users/test_user")

    def test_get_list_of_users(self, mock_api):
        fake_response = requests.Response()
        fake_response._content = fetch_test_file("files/users.json")
        fake_response.status_code = 200
        mock_api.return_value = fake_response

        response = json.dumps(self.api.get_list_of_users())

        self.assertEqual(mock_api.call_count, 1)
        self.assertIn('users', mock_api.call_args[0][1])
        self.assertIn("jayl", response)
        self.assertNotIn('missing_user', response)

    def test_get_user_config(self, mock_api):
        users = requests.Response()
        users._content = fetch_test_file("files/users.json")
        user = requests.Response()
        user._content = fetch_test_file("files/test_user_ldap.json")
        mock_api.side_effect = [users, user]

        response = self.api.get_user_config('brianc')

        self.assertEqual(mock_api.call_count, 2)
        self.assertEqual(response["Title"], "Breaker")


class SingleInboxTests(TestCase):
    @patch('singleinbox.getpass')
    @patch('singleinbox.get_input')
    def test_get_username_password(self, mock_input, mock_pass):
        mock_input.return_value = 'test'
        mock_pass.return_value = 'password'
        username, password = get_username_password()
        self.assertEqual(username, "test")
        self.assertEqual(password, "password")
