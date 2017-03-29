import yaml
import os
import sys

class ConfigPathError(Exception):
    """
    Exception that indicates that the path specifed for a v20 config file
    location doesn't exist
    """
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Config file '{}' could not be loaded.".format(self.path)


class ConfigValueError(Exception):
    """
    Exception that indicates that the v20 configuration file is missing
    a required value
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Config is missing value for '{}'.".format(self.value)


class Account(object):
    """
    The Config object encapsulates all of the configuration required to create
    a v20 API context and configure it to work with a specific Account. 
    Using the Config object enables the scripts to exist without many command
    line arguments (host, token, accountID, etc)
    """
    def __init__(self):
        """
        Load a Config object from ~/.v20.conf
        """
        self.hostname = None
        self.streaming_hostname = None
        self.port = 443
        self.ssl = True
        self.token = None
        self.id = None
        self.accounts = []
        self.active_account = None
        self.path = None
        self.datetime_format = "RFC3339"
        self.load()

    def __str__(self):
        """
        Create the string (YAML) representaion of the Config instance 
        """
        s = ""
        s += "hostname: {}\n".format(self.hostname)
        s += "streaming_hostname: {}\n".format(self.streaming_hostname)
        s += "port: {}\n".format(self.port)
        s += "ssl: {}\n".format(str(self.ssl).lower())
        s += "token: {}\n".format(self.token)
        s += "id: {}\n".format(self.id)
        s += "datetime_format: {}\n".format(self.datetime_format)
        s += "accounts:\n"
        for a in self.accounts:
            s += "- {}\n".format(a)
        s += "active_account: {}".format(self.active_account)
        return s

    def load(self, path="~/.v20.conf"):
        """
        Load the YAML config representation from a file into the Config instance
        Args:
            path: The location to read the config YAML from
        """
        self.path = path
        self.venue = 'https://api-fxtrade.oanda.com'
        self.candles_venue = self.venue + '/v1/candles'
        self.account_url = self.venue + '/v1/accounts/'
        self.streaming = 'https://stream-fxtrade.oanda.com/v1/prices'
        try:
            with open(os.path.expanduser(path)) as f:
                y = yaml.load(f)
                self.hostname = y.get("hostname", self.hostname)
                self.streaming_hostname = y.get(
                    "streaming_hostname", self.streaming_hostname
                )
                self.port = y.get("port", self.port)
                self.ssl = y.get("ssl", self.ssl)
                self.id = str(y.get("username", self.id))
                self.token = y.get("token", self.token)
                self.accounts = y.get("accounts", self.accounts)
                self.active_account = y.get(
                    "active_account", self.active_account
                )
                self.datetime_format = y.get("datetime_format", self.datetime_format)
        except:
            raise ConfigPathError(path)

        self._id_url = self.account_url + self.id
        self.orders =  self._id_url + '/orders/'
        self.positions = self._id_url + "/positions/"
        self.headers = {'Authorization': 'Bearer %s' % self.token,
                        'X-Accept-Datetime-Format': 'UNIX'}

    def validate(self):
        """
        Ensure that the Config instance is valid
        """
        if self.hostname is None:
            raise ConfigValueError("hostname")
        if self.streaming_hostname is None:
            raise ConfigValueError("hostname")
        if self.port is None:
            raise ConfigValueError("port")
        if self.ssl is None:
            raise ConfigValueError("ssl")
        if self.id is None:
            raise ConfigValueError("id")
        if self.token is None:
            raise ConfigValueError("token")
        if self.accounts is None:
            raise ConfigValueError("account")
        if self.active_account is None:
            raise ConfigValueError("account")
        if self.datetime_format is None:
            raise ConfigValueError("datetime_format")

    def info(self):
        '''
        '''
        dat = requests.get(self._id_url, headers=self.headers).json()
        return dat

    def __str__(self):
        return "[=> %s (%s)" % (self.venue, self.id)

    def __repr__(self):
        print('OANDA_FX_USER=%s and OANDA_FX_KEY=%s******' % (
              self.id, self.token[:5])) 
        return self.__str__()
#
#from oanda_fx_api.config import Config
#import requests
#import os
#
#
#class Account:
#    def __init__(self, account='trade'): 
#        self._type = account
#        self._config = Config(account)
#
#        # Envirnment Variables
#        self.id = os.getenv('OANDA_FX_USER')  # account id
#        self.token = os.getenv('OANDA_FX_KEY')
#        #
#        
#        #  Endpoints
#        self.candles_venue = self._config.venue + "/v1/candles"
#        self.account_url = "%s/v1/accounts/" % self._config.venue
#        self.streaming = self._config.streaming_venue
#
#        self._id_url = self.account_url + self.id
#        self.orders =  self._id_url + '/orders/'
#        self.positions = self._id_url + "/positions/"
#        #
#
#        # Headers
#        self.headers = {'Authorization': 'Bearer %s' % self.token,
#                        'X-Accept-Datetime-Format': 'UNIX'}
#        #
#
#    def info(self):
#        '''
#        '''
#        dat = requests.get(self._id_url, headers=self.headers).json()
#        return dat
#
#    def __str__(self):
#        return "[=> %s (%s)" % (self.venue, self.id)
#
#    def __repr__(self):
#        print('OANDA_FX_USER=%s and OANDA_FX_KEY=%s******' % (
#              self.id, self.token[:5])) 
#        return self.__str__()
