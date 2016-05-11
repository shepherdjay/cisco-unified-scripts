from getpass import getpass

from pycuc.japi import UnityAPI
import yaml


class Config:
    def __init__(self, filename):
        with open(filename, 'r') as stream:
            config = yaml.load(stream)
        self.unity_url = config['unity_url']


def get_input(message):
    return input(message)


def get_username_password():
    """
    Uses get_input function to collect username and password
    :return: Tuple of username and password
    """
    username = get_input("Please enter your username for unity: ")
    password = getpass(prompt="Password: ")
    return username, password


def find_users_without(api):
    """
    Wires together the required API Calls to Unity to find users without SingleInbox
    :param api: UnityAPI Object
    :return: List of users without SingleInbox or Empty List if None
    """
    users = api.get_list_of_users()
    no_single_inbox = []

    for user in users:
        service_uri = user["ExternalServiceAccountsURI"]
        service_accounts = api.get(service_uri)
        if service_accounts['@total'] == "0":
            no_single_inbox.append(user['Alias'])

    return no_single_inbox


def ldap_user(api, alias):
    """
    Checks the UnityAPI to determine if user is synced to ActiveDirectory. Returns Boolean Result
    :param api: UnityAPI Object
    :param alias: Alias to search for
    :return: Boolean
    """
    user_config = api.get_user_config(alias)

    if user_config["LdapType"] == "3":
        return True
    else:
        return False


def main():
    script_config = Config('config.yml')
    un, pw = get_username_password()

    api = UnityAPI(username=un, password=pw, url=script_config.unity_url)

    no_single_inbox = find_users_without(api)

    filtered_users = []
    for alias in no_single_inbox:
        if ldap_user(api, alias):
            filtered_users.append(alias)

    print(filtered_users)


if __name__ == "__main__":
    main()
