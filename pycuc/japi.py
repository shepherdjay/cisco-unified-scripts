import requests


class UnityAPI(object):
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.base_url = url

    # @property
    # def version(self):
    #     return "vmrest"

    @property
    def session(self):
        """
        Constructs the standard session needed for the rest of the Unity Connections
        :return: Session
        """
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.headers = {
            'Accept': 'application/json',
            'Connection': 'keep-alive',
        }
        return session

    def _construct_uri_from_list(self, path_as_list):
        """
        Takes a path_as_list of resources and constructs the necessary URL
        :param path_as_list: API Path as path_as_list
        :return: A constructed URI for passing to requests
        """
        return self.base_url + '/' + '/'.join(path_as_list)

    def _construct_uri_from_string(self, path_as_string):
        """
        Takes a string and constructs the necessary URL
        :param path_as_string: API Path as string
        :return: A constructed URI for passing to requests
        """
        if path_as_string[0] == "/":
            return self.base_url + path_as_string
        else:
            return self.base_url + '/' + path_as_string

    def _get(self, uri):
        """
        Uses the requests library to perform a get method and return standard requests object.
        It also performs error checking to ensure the response was a 200
        :return: requests object
        """
        response = self.session.get(uri)
        if response.ok:
            return response
        else:
            raise Exception("Response Invalid")

    def get(self, path):
        """
        Takes a path. Passes them to constructor for formatting, and returns result of resource.
        :param path: List of resources
        :return: Response as json
        """
        if isinstance(path, list):
            uri = self._construct_uri_from_list(path)
        elif isinstance(path, str):
            uri = self._construct_uri_from_string(path)
        else:
            raise TypeError("Path must be string or list")
        return self._get(uri).json()

    def get_list_of_users(self):
        """
        Retrieves the users and returns as json
        :return: Response as json
        """
        response = self._get(self._construct_uri_from_list(['vmrest', 'users']))
        return response.json()['User']

    def _get_user_config_by_objectid(self, cisco_object_id):
        return self.get(['vmrest', 'users', cisco_object_id])

    def get_user_config(self, alias):
        """
        Searches for the specific user based on alias and returns the result of a call to that specific users
        object. Uses the _get_specific_user function to achieve.
        :param alias: alias to search for, must be unique
        :return: User config as json
        """
        users = self.get_list_of_users()
        for user in users:
            if user['Alias'] == alias:
                cisco_object_id = user['ObjectId']
                return self._get_user_config_by_objectid(cisco_object_id)