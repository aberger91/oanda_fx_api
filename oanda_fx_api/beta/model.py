#from time import sleep
from config import FX, TradeModelError
from position import  Positions, ExitPosition, PnL
from order import OrderHandler
from util import Signals


class Initialize(object):
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config

    def init_model(self):
        try:
                name, setting = self.set_params()
        except Exception as e:
                print("Failed to initialize:\n%s" % e)	
                return False
        return name, setting

    def set_params(self):
        params = [x.split(',') for x in open(self.path_to_config).read().splitlines()]
        print(params)
        name = [x for x in params if params.index(x) % 2==0]
        setting = [x for x in params if params.index(x) % 2 != 0]
        return name, setting


class Parameters(object):
    def __init__(self, path_to_config):
        self.is_initialized = Initialize(path_to_config).init_model()
        param = self.get_parameters()
        self.COUNT = param[0]
        self.LONGWIN = param[1]
        self.SHORTWIN = param[2]
        self.SYMBOL = param[3]
        self.QUANTITY = param[4]
        self.MAXPOS = param[5]
        self.MAXLOSS = param[6]
        self.MAXGAIN = param[7] 
        self.LIMIT = param[8]
        self.KUP = param[9]
        self.KDOWN = param[10]
        self.TREND_THRESH = param[11] 

    def __repr__(self):
        return "SYMBOL:%s\nCOUNT:%s\nMAXPOS:%s\n" % (
                self.SYMBOL, self.COUNT, self.MAXPOS)

    def get_parameters(self):
        if self.is_initialized:
                return self.is_initialized[1]
        else:
                raise TradeModelError(0)
        return False


class Initial(object):
    def __init__(self, name):
        self.name = Confs.page[name]

    def _config(self):
        with open(self.name) as csv_file:
            try:
                p = csv_file.read().replace("\n", ",").split(",")
                field = [x for x in p if p.index(x)%2==0]
                value = [x for x in p if p.index(x)%2!=0]
            except Exception as e:
                raise TradeModelError(0, message=e)
        return field, value


class FX(object):
    def __init__(self, name):
        self._init = self.setup(name) # calls Initial
        self.COUNT = self._init[0]
        self.LONGWIN = self._init[1]
        self.SHORTWIN = self._init[2]
        self.SYMBOL = self._init[3]
        self.QUANTITY = self._init[4]
        self.MAXPOS = self._init[5]
        self.MAXLOSS = self._init[6]
        self.MAXGAIN = self._init[7]
        self.LIMIT = self._init[8]
        self.MODEL = []

    def setup(self, name):
        if name in Confs.page.keys():
            try:
                Initial(name)._config()[1] # second column
            except Exception as e:
                raise TradeModelError(0, message=e)
        else:
            raise TradeModelError(1, name)

    def stoch_event(self):
        self.MODEL.append("stoch")
        self.KUP = self._init[9]
        self.KDOWN = self._init[10]

    def bband_event(self):
        self.MODEL.append("bband")

    def mavg_event(self):
        self.MODEL.append("mavg")

    def macd_event(self):
        self.MODEL.append("macd")

    def adx_event(self):
        self.MODEL.append("adx")


class Indicators(object):
    def __init__(self, kup, kdown):
        self.KUP = kup
        self.KDOWN = kdown

    def kthresh_up_cross(self, chan, param):
        """ Upper threshold signal (self.KUP) """
        if (chan == 0) and (param > self.KUP):
            return True
        else:
            return False

    def kthresh_down_cross(self, chan, param):
        """ Lower threshold signal (self.KDOWN) """
        if (chan == 0) and (param < self.KDOWN):
            return True
        else:
            return False

    def stoch_upcross(self, K_to_D, params):
        K, D = params
        if (K_to_D  == -1) and  (K > D):
            if (K < self.KDOWN):
                return True
        else:
            return False

    def stoch_downcross(self, K_to_D, params):
        K, D = params
        if (K_to_D  == 1) and  (K < D):
            if (K > self.KUP):
                return True
        else:
            return False


class Conditions(Indicators):
    def __init__(self,kup, kdown):
        Indicators.__init__(kup, kdown)

    def cross(self):
        if self.stoch_upcross(K_to_D, [K, D]):
            self.order_handler(tick, "buy")

        if self.stoch_downcross(K_to_D, [K, D]):
            self.order_handler(tick, "sell")

    def thresh(self):
        if self.kthresh_up_cross(channel, K):
            self.order_handler(tick, "sell")

        elif self.kthresh_down_cross(channel, K):
            self.order_handler(tick, "buy")


class Generic(FX):
        def __init__(self, name):
            FX.__init__(name)
            self.stoch_event()

        def signals(self, granularity='S5'):
            return Signals(self.COUNT,
                           self.SYMBOL,
                           self.LONGWIN,
                           self.SHORTWIN,
                           granularity)

        def order_handler(self, tick, side):
            trade = OrderHandler(self.SYMBOL,
                                 tick,
                                 side,
                                 self.QUANTITY).send_order()
            if trade.reject:
                print("[!]  -- Order rejected -- ")
            return trade

        def positions(self):
            position = Positions(self.SYMBOL).checkPosition()
            return position

        def close_out(self, tick, position, profit_loss):
            close = ExitPosition().closePosition(position, profit_loss, tick)
            return close

        def check_position(self, tick):
           # while True:
           #     tick = self.signal_queue.get()[2]

            # get positions
            position = self.positions()
            #self.position_queue.put(position.units)

            if position.units != 0:
                self.risk_control(tick, position)

        def risk_control(self, tick, position):
                lower_limit = self.MAXLOSS * (position.units/self.QUANTITY)
                upper_limit = self.MAXGAIN * (position.units/self.QUANTITY)
                profit_loss = PnL(tick, position).get_pnl()

                if profit_loss < lower_limit:
                    self.close_out(tick,
                                    position,
                                    profit_loss)

                if profit_loss > upper_limit:
                    self.close_out(tick,
                                    position,
                                    profit_loss)

'''
class StochEventAlgo(Generic):
	def __init__(self, name):
		Generic.__init__(name)

	def signal_listen(self):
	    while True:
	        channel, K_to_D, tick = self.signal_queue.get()
	        K, D = tick.K, tick.D
	        print(tick)

	def trade_model(self):
	    model = self.signals()
	    tick = model.tick
	    channel = model.channel
	    K_to_D = model.stoch

	    while True:
	        self.signal_queue.put([channel, K_to_D, tick])
	        sleep(5)
	        channel = model.channel
	        K_to_D = model.stoch
	        model = self.signals()
	        tick = model.tick
'''
