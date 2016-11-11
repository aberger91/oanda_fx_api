class Tick(object):
    def __init__(self, tick):
        self.volume =       tick["volume"]
        self.total_volume = tick["total_volume"]
        self.closeBid =     tick["close_bid"]
        self.closeAsk =     tick["close_ask"]
        self.openMid =      tick["openMid"]
        self.high_mid =      tick["high_mid"]
        self.low_mid =       tick["low_mid"]
        self.close_mid =     tick["close_mid"]
        self.K =            tick['K']
        self.D =            tick['D']
        self.sma =          tick["sma"]
        self.ewma =         tick["ewma"]
        self.upper =        tick["upper_band"]
        self.lower =        tick["lower_band"]        
        self.adf_1 =        tick["ADF_1"]
        self.adf_5 =        tick["ADF_5"]
        self.adf_10 =       tick["ADF_10"]
        self.adf_p =        tick["ADF_p"]
        self.adf_stat =     tick["ADF_stat"]
        self.spread =       self.closeAsk - self.closeBid

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s,%s,%s,%s" % (
                self._time, self.closeBid, self.closeAsk)