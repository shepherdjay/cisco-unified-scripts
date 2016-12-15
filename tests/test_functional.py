import os
from unittest import TestCase
from unittest.mock import patch

import requests
from singleinbox import find_users_without, get_username_password
from pycuc.japi import UnityAPI


def fetch_http_test_file(file):
    """
    Fetches a test file of the HTTP Content and returns in bytes
    :param file: A properly formatted html file to fetch
    :return: File returned as bytes
    """
    fn = os.path.join(os.path.dirname(__file__), file)
    with open(fn, mode='r') as infile:
        return infile.read().encode('utf-8')


def build_fake_user_response():
    fake = requests.Response()
    fake._content = fetch_http_test_file("files/users.json")
    fake.status_code = 200
    return fake


def build_fake_external_services_response():
    fake1 = requests.Response()
    fake1._content = fetch_http_test_file("files/external_services_with.json")
    fake1.status_code = 200

    fake2 = requests.Response()
    fake2._content = fetch_http_test_file("files/external_services_without.json")
    fake2.status_code = 200
    return fake1, fake2


class FunctionalTests(TestCase):
    def setUp(self):
        self.user_with = 'brian'
        self.user_without = 'jay'
        self.fake_user_response = build_fake_user_response()
        self.fake_external_with, self.fake_external_without = build_fake_external_services_response()

    def test_report_users_without_single_inbox(self):
        with patch('singleinbox.get_input') as mock:
            mock.side_effect = ['test', 'password']
            # As a user I would like to be able to generate a list of users in Unity
            # that are missing SingleInbox Integration

            # I start by running the program from command line with no arguments passed
            # The system asks for my username and my password which happens to be test,test
            ## I don't know how to test this functionally so I patch in get_input() function with fake calls.
            username, password = get_username_password()

        api_object = UnityAPI(username, password, "https://localhost")

        # Once I enter the correct information it provides the expected output
        ## The main function will actually print this but --
        ## again not sure how to interact with the command line in a testing way

        with patch("singleinbox.UnityAPI._get") as mock_api:
            mock_api.mock_add_spec(UnityAPI._get)
            mock_api.side_effect = [self.fake_user_response, self.fake_external_with, self.fake_external_without]
            output = find_users_without(mock_api)

        self.assertNotIn("brianc", output)
        self.assertIn("jayl", output)
