import requests
import numpy as np


class PnL:
    def __init__(self, tick, position):
        '''
        '''
        self.bid = tick.closeBid
        self.ask = tick.closeAsk
        self.price = position.price
        self.units = position.units
        self.position = position

    def get_pnl(self):
        if self.position.side:  # short = 1
            return (self.price - self.ask) * self.units
        else:  # long = 0
            return (self.bid - self.price) * self.units


class MostRecentPosition:
    def __init__(self, side, price, units):
        self.side = side
        self.price = price
        self.units = units

    def __repr__(self):
        return "SIDE: %s PRICE: %s UNITS: %s" % (
                self.side, np.mean(self.price), self.units)


class Positions:
    def __init__(self, account, symbol):
        self.account = account
        self.symbol = symbol

    def _get_position(self):
        params = {'instruments': self.symbol,
                  "accountId": self.account.id}
        try:
            req = requests.get(self.account.positions + self.symbol, headers=self.account.headers, data=params).json()
        except Exception as e:
            print(">>> Error returning position\n%s\n%s" % (str(e), req))
            return False

        if "code" in req:
            print(req)
            return False
        elif 'side' in req:
            side = 1 if req['side'] == 'sell' else 0
            position = {'side':  side,
                        'units': req['units'],
                        'price': req['avgPrice']}
        else:
            print(req)
            return False
        return position

    def get_position(self):
        position = self._get_position()
        if position:
            position = MostRecentPosition(position["side"],
                                          position["price"],
                                          position["units"])
            return position
        else:
            return MostRecentPosition(0, 0, 0)


class MostRecentExit:
    def __init__(self, position, side, profit_loss):
        self.id =           ("-").join([str(x) for x in position["ids"]])
        self.instrument =   position["instrument"]
        self.price =        position["price"]
        self.units =        position["units"]
        self.profit_loss =  profit_loss
        self.side =         side


class ExitPosition:
    def __init__(self, account):
        self.account = account

    def _close_position(self, symbol):
        try:
            req = requests.delete(self.account.positions + self.symbol, headers=self.account.headers).json()
        except Exception as e:
            print('Unable to delete positions: \n', str(e))
            return req
        try:
            order = {'ids': req['ids'], 'instrument': req['instrument'],
                         'units': req['totalUnits'], 'price': req['price']}
            return order
        except Exception as e:
            print('Caught exception closing positions: \n%s\n%s'%(str(e), req))
            return False

    def close_position(self, position, profit_loss):
        exit = self._close_position("EUR_USD")
        if exit["units"] != 0:
            exit = MostRecentExit(exit,
                                  position.side,
                                  profit_loss)
            return exit
        else:
            print(">>> No positions removed\n(%s)" % position)
            return False
