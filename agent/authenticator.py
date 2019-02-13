from yaml import load, YAMLError
from os import path


class Authenticator():
    """ The authenticator class interprets the credentials
    yaml file into a python dictionary datastructure. This
    module can be used across all aspects of our application to
    alleviate hard coded values such as usernames and passwords.
    """

    def __init__(self):
        """ Initilizer for the authenticator module. Pulls data
            from a yaml file to obtain credentials.
        """
        rootpath = path.abspath("")
        credpath = self.find_cred_file(rootpath)

        with open(credpath, "r") as file:
            try:
                self.working_creds = load(file)
            except YAMLError as err:
                print(err)

    def find_cred_file(self, rootpath):
        """ Helper funciton to get the correct path to the yaml file.
            Must be excecuted on a linux machine.
        """
        rootdir = ''
        for char in rootpath:
            if (char != '/'):
                rootdir += char
            else:
                rootdir = ""

        if (rootdir == 'agent'):
            return path.join(rootpath, 'creds.yml')
        elif (rootdir == 'NET4901-SP'):
            return path.join(rootpath, 'agent/creds.yml')
        elif (rootdir == 'webapp'):
            return path.join(rootpath, '../agent/creds.yml')
        else:
            print('Authenticator Relative Path Error!')
            exit()
