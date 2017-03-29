from oanda_fx_api.account import Account
from oanda_fx_api.prices import GetCandles, StreamPrices
from oanda_fx_api.order import OrderHandler
from oanda_fx_api.tools.risk import Risk
from oanda_fx_api.charting import ohlc
from bokeh.plotting import show
import argparse


def arguments():
    '''
    command-line arguments
    '''
    desc = '''application for creating algorithmic trading strategies
using the OANDA FX trading platform '''
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--prices', 
                        nargs=1,
                        help='get FX prices', 
                        required=False, 
                        type=str)
    parser.add_argument('-o', '--order', 
                        nargs=3,
                        help='send an order', 
                        required=False, 
                        type=str)
    parser.add_argument('-c', '--candles', 
                        nargs=1,
                        help='get FX candles', 
                        required=False, 
                        type=str)
    parser.add_argument('-s', '--summary', 
                        nargs=1,
                        help='account summary', 
                        required=False, 
                        type=str)
    args = parser.parse_args()
    return args.prices, args.order, args.candles, args.summary

def main():
    prices, order, candles, summary = arguments()
    acc = Account()

    if prices:
        quotes = GetCandles(acc, prices[0], count=500).request()
        print(quotes.tail())

    elif order:
        side, amount, ccy = order
        quote = GetCandles(acc, ccy, count=1).request()
        _price = quote['closeAsk'] if side == 'buy' else quote['closeBid']
        order = OrderHandler(acc, 
                             side, 
                             amount, 
                             ccy, 
                             _price, 
                             kind='market').send_order()

    elif candles:
        ccy = candles[0]
        quotes = GetCandles(acc, ccy, count=500).request()
        p = ohlc(quotes, symbol=ccy, freq=5)
        show(p)

    elif summary:
        symbols = summary[0].split(',')
        risk = Risk(acc).summary(symbols)
