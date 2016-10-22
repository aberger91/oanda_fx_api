import statsmodels.tsa.stattools as ts
from oanda_fx_api.prices import GetCandles
from oanda_fx_api.logic.tick import Tick


class Compute(GetCandles):
    def __init__(self, account, symbol, 
                 count=900, long_win=720, 
                 short_win=540, granularity='S5'):
        '''
        takes priority over GetCandles.__init__
        '''
        self.init(account, symbol)
        self.candles =      self.request()
        self.long_win =     long_win
        self.short_win =    short_win
        self._open =        self.candles["open_mid"]
        self.high =         self.candles["high_mid"]
        self.low =          self.candles["low_mid"]
        self.close =        self.candles["close_mid"]
        self.candles["total_volume"] = self.candles["volume"].sum()
        self.moving_average()
        self.stoch_osc()
        self.adf_test()
        self.bbands()
        self.tick = self._tick
    
    def init(self, account, symbol):
        GetCandles.__init__(self, account, symbol, 
                            count=count, granularity=granularity)

    @property                            
    def _tick(self):
        return Tick(self.candles.ix[self.candles.iloc[-1]])
                            
    def adf_test(self):
        test = ts.adfuller(self.candles["close_mid"], maxlag=1)
        adf_crit = test[4]
        self.candles["ADF_1"] = adf_crit["1%"]
        self.candles["ADF_5"] = adf_crit["5%"]
        self.candles["ADF_10"] = adf_crit["10%"]
        self.candles["ADF_p"] = test[1]
        self.candles["ADF_stat"] = test[0]

    def stoch_osc(self):
        self.candles['max'] = self.high.rolling(window=self.long_win).max()
        self.candles['min'] = self.low.rolling(window=self.long_win).min()
        
        self.candles['K'] = (self.close - self.candles['min']) / (self.candles['max'] - self.candles['min']) * 100
        self.candles['D'] = self.candles['K'].rolling(window=3).mean()

    def moving_average(self):
        self.candles['sma'] = self.close.rolling(window=self.long_win).mean()
        self.candles['ewma'] = self.close.rolling(window=self.short_win).mean()

    def bbands(self):
        self.candles['upper_band'] = self.candles['sma'] + self.close.rolling(window=self.long_win).std() * 2
        self.candles['lower_band'] = self.candles['sma'] - self.close.rolling(window=self.long_win).std() * 2


class Signals(Compute):
    def __init__(self, account, symbol, 
                 count=900, long_win=720, 
                 short_win=540, granularity="S5"):
        '''
        takes priority over Compute.__init__
        '''
        self.init(account, symbol)
        self.channel, self.stoch = self.stoch_signals()
        self.bbands_channel =      self.bband_signals()
        self.mavg_state =          self.moving_avg_signals()
        
    def init(self, account, symbol, count, long_win, short_win, granularity):
        Compute.__init__(self, account, symbol, count=count, 
                         long_win=long_win, short_win=short_win, 
                         granularity=granularity)

    def stoch_signals(self, limitup=80, limitdown=20):
        if limitup < self.tick.K:
            channel = 1
        elif self.tick.K < limitdown:
            channel = -1
        else:
            channel = 0
            
        if self.tick.K > self.tick.D:
            stoch = 1
        elif self.tick.K < self.tick.D:
            stoch = -1
        return channel, stoch

    def bband_signals(self):
        if self.tick.close_mid > self.tick.upper:
            channel = 1
        elif self.tick.close_mid < self.tick.lower:
            channel = -1
        else:
            channel = 0
        return channel

    def moving_avg_signals(self):
        if self.tick.ewma > self.tick.sma:
            sma_state = 1
        elif self.tick.ewma < self.tick.sma:
            sma_state = -1
        return sma_state