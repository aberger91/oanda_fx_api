import os

class Paths:
    HOME = os.getenv('HOME')
    LOG = "%s/tmp/" % HOME

    trades = "%s/trade_log" % LOG
    orders = "%s/order_log" % LOG
    model = "%s/model_log" % LOG

    def __init__(self, symbol):
        self.ticks = "%s/%s_tick" % (self.LOG, symbol)


class Config:
    fxtrade_venue = "https://api-fxtrade.oanda.com"
    practice_venue = "https://api-fxpractice.oanda.com"
    streaming_practice_venue = "https://stream-fxpractice.oanda.com/v1/prices"
    fxtrade_venue = "https://api-fxtrade.oanda.com"
    streaming_venue = "https://stream-fxtrade.oanda.com/v1/prices"


class TradeModelError(Exception):
    messages = {0: "Model not initialized.",
                1: "Could not open configuration file.",
                2: "Configuration file contains invalid parameter.",
                3: "Unknown order status. Check if trade done."}

    def __init__(self, error, message=""):
        self.error = TradeModelError.messages[error]
        self.message = message
        self.callback()

    def callback(self):
        super().__init__(self.error, self.message) if self.message else super().__init__(self.error)
            
