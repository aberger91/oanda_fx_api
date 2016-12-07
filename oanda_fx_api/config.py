import os


class Paths(object):
    HOME = os.getenv('HOME')
    LOG = "%s/tmp/" % HOME

    trades = "%s/trade_log" % LOG
    orders = "%s/order_log" % LOG
    model = "%s/model_log" % LOG

    def __init__(self, symbol):
        self.ticks = "%s/%s_tick" % (self.LOG, symbol)


class Config(object):
    def __init__(self, mode):
        venue = 'https://api-fx%s.oanda.com' % mode
        streaming_venue = "https://stream-fx%s.oanda.com/v1/prices" % mode

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
            
