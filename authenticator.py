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
        
        credpath = 'creds.yml'
 
        with open(credpath, "r") as file:
            try:
                self.working_creds = load(file)
            except YAMLError as err:
                print(err)