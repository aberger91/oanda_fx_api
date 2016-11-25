from oanda_fx_api.config import Config
import requests
import os


class Account:
    def __init__(self, account='trade'): 

        self._type = account
        self.init_account()

        self.id = os.getenv('OANDA_FX_USER')  # account id
        self.token = os.getenv('OANDA_FX_KEY')
        
        self.candles_venue = self.venue + "/v1/candles"
        self.streaming = Config.streaming_venue
        self._id_url = self.account_url + self.id
        
        self.orders =  self._id_url + '/orders/'
        self.positions = self._id_url + "/positions/"
        self.headers = {'Authorization': 'Bearer %s' % self.token,
                        'X-Accept-Datetime-Format': 'UNIX'}

    def init_account(self):
        if self._type == 'trade':
            self.venue = Config.fxtrade_venue  # api endpoint
            self.account_url = "%s/v1/accounts/" % self.venue
        elif self._type == 'practice':
            self.venue == Config.practice_venue
            self.account_url = "%s/v1/accounts/" % self.venue
        else:
            raise FutDBException('Invalid venue, must be practice or trade')

    def info(self):
        dat = requests.get(self._id_url, headers=self.headers).json()
        return dat

    def __str__(self):
        return "[=> %s (%s)" % (self.venue, self.id)

    def __repr__(self):
        print('Authenicating with: \nOANDA_FX_USER=%s and OANDA_FX_KEY=%s**********' % (
              self.id, self.token[:4])) 
        return self.__str__()
