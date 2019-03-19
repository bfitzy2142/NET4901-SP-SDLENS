from yaml import load, YAMLError
import getpass


class Authenticator():
    """ The authenticator class interprets the credentials
    yaml file into a python dictionary datastructure. This
    module can be used across all aspects of our application to
    alleviate hard coded values such as usernames and passwords.
    """
    #TODO: Make seperate YAML files for app auth and agent auth

    def __init__(self):
        """ Initilizer for the authenticator module. Pulls data
            from a yaml file to obtain credentials.
        """
        comp_user = getpass.getuser()
        try:
            with open(f'/home/{comp_user}/.sdlens/creds.yml', "r") as file:
                try:
                    self.working_creds = load(file)
                except YAMLError as err:
                    print(err)
        except FileNotFoundError:
                print('-------------------------')
                print('YAML file does not exist!')
                print('-------------------------')
                exit()
