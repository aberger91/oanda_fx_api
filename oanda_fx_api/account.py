from oanda_fx_api.config import Config
import requests
import os


class Account:
    def __init__(self, account='trade'): 
        self._type = account
        self._config = Config(account)

        # Envirnment Variables
        self.id = os.getenv('OANDA_FX_USER')  # account id
        self.token = os.getenv('OANDA_FX_KEY')
        #
        
        #  Endpoints
        self.candles_venue = self._config.venue + "/v1/candles"
        self.account_url = "%s/v1/accounts/" % self._config.venue
        self.streaming = self._config.streaming_venue

        self._id_url = self.account_url + self.id
        self.orders =  self._id_url + '/orders/'
        self.positions = self._id_url + "/positions/"
        #

        # Headers
        self.headers = {'Authorization': 'Bearer %s' % self.token,
                        'X-Accept-Datetime-Format': 'UNIX'}
        #

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
