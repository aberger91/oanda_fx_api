from oanda_fx_api.prices import GetCandles
from oanda_fx_api.position import PositionHandler, PnL
from oanda_fx_api.account import Account


class Risk:
    def __init__(self, acc):
        self.acc = acc

    def summary(self, symbols):
        total_pnl = 0
        for symbol in symbols:

            print(symbol)
            tick = GetCandles(self.acc, symbol, count=1).request().ix[-1]
            position = PositionHandler(self.acc, symbol).get_position()
            pnl = PnL(tick, position).get_pnl()

            print(position)

            if symbol[3:] != 'USD':
                pnl = pnl / tick.close_mid
            total_pnl += pnl

            print('%s PnL: %s' % (symbol, pnl))
            print(tick[['closeBid', 'closeAsk']])
            print()

        print('Total PnL: %s' % total_pnl)
        info = self.acc.info()
        balance, unrealpl = info['balance'], info['unrealizedPl']
        nav = balance + unrealpl
        print('Balance: %s\nUnrealizedPnL: %s\nNAV: %s' % (balance, unrealpl, nav))

