import datetime as dt
import pandas as pd
import requests
import json


class StreamPrices(object):
    def __init__(self, account, instrument):
        self.account = account
        self.instrument = instrument

    def stream(self):
        params = {"instruments": self.instrument,
                  "accessToken": self.account.token,
                  "accountId":   self.account.id}
        try:
            s = requests.Session()
            req = requests.Request("GET", self.account.streaming, 
                                          headers=self.account.headers, 
                                          params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=False)
        except Exception as e:
            print(">>> Caught exception during request\n{}".format(e))
            s.close()
        finally:
            return resp

    def prices(self):
        for tick in self.stream():
            try:
                tick = json.loads(str(tick, "utf-8"))
            except json.decoder.JSONDecodeError as e:
                prev_tick = '%s' % (str(tick, "utf-8"))
                print(prev_tick)
                continue
            if "tick" in tick.keys():
                tick = tick["tick"]
                print(tick)


class GetCandles(object):
    def __init__(self, account, symbol, start='', count=900, granularity='S5'):
        self.account =      account
        self.count =        count
        self.symbol =       symbol
        self.start =        start
        self.granularity =  granularity
        self.params =       self.parameters()
        
                            
    def parameters(self):
        self.params =  {'instrument': self.symbol,
                        'granularity': self.granularity}
        if self.start:
            self.params['start'] = str(int(self.start.timestamp()))
            self.params['end'] =   str(int(dt.datetime.now().timestamp()))
        else:
            self.params['count'] = self.count
        return self.params
        
    def datetime_index(self, start, end, freq='5S'):
        index = pd.DatetimeIndex(start=start, end=end, freq=freq)
        return index

    def _request(self):
        try:
            req = requests.get(self.account.candles_venue,
                               headers=self.account.headers, 
                               params=self.params).json()
            req = req.get('candles')
        except Exception as e:
            print('%s\n>>> Error: No candles in JSON response:' % e)
            return False
        return req
            
    def request(self):
        req = self._request()
        try:
            candles = pd.DataFrame(req)
        except Exception as e:
            print('%s\n>>> Error: Could not stream request into DataFrame' % e)
            return False
        
        candles.index = candles['time'].apply(lambda x: dt.datetime.fromtimestamp(int(x)/1000000))
        start, end = candles.index[0], candles.index[-1]
        
        candles = pd.DataFrame(index=self.datetime_index(start=start, end=end)).join(candles, how='outer')
        candles = candles.fillna(method='ffill')
        
        for x in ['open', 'high', 'low', 'close']:
            candles['%s_mid' % x] = (candles['%sAsk' % x] + candles['%sBid' % x]) / 2
        return candles
