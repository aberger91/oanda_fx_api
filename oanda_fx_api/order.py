import requests
import datetime as dt
from oanda_fx_api.config import Paths


class Orders:
    def __init__(self, account):
        self.account = account
        self.params = {}
    
    def working(self):
        try:
            resp = requests.get(self.account.orders,
                                headers=self.account.headers, 
                                verify=False).json()
            resp = resp['orders']
        except Exception as e:
            raise ValueError(">>> Error: Caught exception retrieving orders: %s" % e)
        return resp
            
    def delete(self, id):
        try:
            resp = requests.request("DELETE", 
                                    self.account.orders + str(id), 
                                    headers=self.account.headers, 
                                    verify=False).json()
            return resp
        except Exception as e:
            raise ValueError(">>> Error: Caught exception deleting order: %s" % e)
            
    def get(self, id):
        try:
            resp = requests.get(self.account.orders + str(id),
                                headers=self.account.headers, 
                                verify=False).json()
        except Exception as e:
            raise ValueError(">>> Error: Caught exception retrieving order: %s" % e)
        return resp
        
    def update(self, id, param, value):
        try:
            self.params[param] = value
            resp = requests.request("PATCH", 
                                    self.account.orders + str(id),
                                    headers=self.account.headers, 
                                    data=self.params,
                                    verify=False).json()
        except Exception as e:
            raise ValueError(">>> Error: Caught exception updating order: %s" % e)
        return resp

                
class MostRecentOrder(Orders):
    def working(self):
        try:
            resp = requests.get(self.account.orders,
                                headers=self.account.headers, 
                                verify=False).json()
            return resp
        except Exception as e:
            raise ValueError(">>> Caught exception retrieving orders: %s"%e)

    def delete(self):
        try:
            resp = requests.request("DELETE", self.account.orders, 
                                    headers=self.account.headers, verify=False).json()
            return resp
        except Exception as e:
                raise ValueError(">>> Caught exception retrieving orders: %s"%e)


class MostRecentReject:
    def __init__(self, order, params):
        self._time =    dt.datetime.now().timestamp()
        self.code =     order["code"]
        self.message =  order["message"]
        self.params =   params
        self.reject =   True # will not log

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # code == 23
        return "[=> REJECT %s %s @ %s (%s)" % (
                self._time, self.params['side'], self.params['price'], self.message)


class MostRecentTrade:
    """
    Market Orders --> response from Oanda POST
    Receives and handles the order data
    """
    def __init__(self, order):
        self.order =    order
        self.trade =    self._trade()
        self.reject =   False

    def _trade(self):
        if "tradesClosed" in self.order and self.order["tradesClosed"]:
            self.time = dt.datetime.fromtimestamp(int(self.order['time'])/1000000)
            try:
                self.side =         self.order["tradesClosed"][0]["side"]
                self.id =           self.order["tradesClosed"][0]["id"]
                self.units =        self.order["tradesClosed"][0]["units"]
                self.instrument =   self.order["instrument"]
                self.price =        self.order["price"]
                return True
            except KeyError as e:
                print(">>> Error: Caught exception in closed_trade\n%s" % e)
        elif "tradeOpened" in self.order and self.order["tradeOpened"]:
            self.time = dt.datetime.fromtimestamp(int(self.order['time'])/1000000)
            try:
                self.side =         self.order["tradeOpened"]["side"]
                self.id =           self.order["tradeOpened"]["id"]
                self.units =        self.order["tradeOpened"]["units"]
                self.instrument =   self.order["instrument"]
                self.price =        self.order["price"]
                return True
            except KeyError as e:
                print(">>> Error: Caught exception in opened_trade\n%s" % e)
        return False

    def __repr__(self):
        return str(self.order)


class OrderHandler(Orders):
    def __init__(self, account, side, 
                 quantity, symbol, price, 
                 kind="market", duration=0):
        self.account =  account
        self.side =     side
        self.quantity = quantity
        self.symbol =   symbol
        self.kind =     kind
        self.price =    price
        self.duration = dt.timedelta(seconds=duration)
        
    def expiry(self):
        return str(int((dt.datetime.utcnow() + self.duration).timestamp()))

    def market_order(self):
        params = {'instrument': self.symbol,
                  'side':       self.side,
                  'type':       self.kind,
                  'units':      self.quantity}
        return params

    def limit_order(self):
        '''
        duration: int (seconds)
        '''
        params = {'instrument': self.symbol,
                  'side':       self.side,
                  'type':       self.kind,
                  'units':      self.quantity,
                  "price":      self.price,
                  "expiry":     self.expiry()}
        return params

    def _send_order(self):
        params = self.market_order() if self.kind == 'market' else self.limit_order()
        try:
            resp = requests.post(self.account.orders, 
                                 headers=self.account.headers, 
                                 data=params, 
                                 verify=False).json()
        except Exception as e:
            print(">>> Error: Caught exception sending order\n%s" % e)
            return False
        return resp, params

    def send_order(self):
        order, params = self._send_order()
        if order:
            if "tradeOpened" in order.keys():
                order = MostRecentTrade(order)
            elif "orderOpened" in order.keys():
                order = MostRecentOrder(self.account, order)
            elif "code" in order.keys():
                if order["code"] in [22, 23]:
                    order = MostRecentReject(order, params)
                    print(order)
                else:
                    print(order)
                    raise NotImplementedError(">>> Error: order[\'code\'] not an integer or != 23 or 22")
            return order
        else:
            print("%s Order not done\n" % order)
            return False
