from oanda_fx_api.account import Account
from oanda_fx_api.prices import GetCandles, StreamPrices
from oanda_fx_api.order import OrderHandler
from oanda_fx_api.tools.risk import Risk
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
                        nargs=4,
                        help='send an order', 
                        required=False, 
                        type=str)
    parser.add_argument('-s', '--summary', 
                        nargs=1,
                        help='account summary', 
                        required=False, 
                        type=str)
    args = parser.parse_args()
    return args.prices, args.order, args.summary

def main():
    prices, order, summary = arguments()

    acc = Account()
    if prices:
        ccy = prices[0]
        prices = StreamPrices(acc, ccy).prices()
    elif order:
        side, amount, ccy, _type = order
        quote = GetCandles(acc, ccy, count=1).request()
        if side == 'buy':
            _price = quote['closeAsk']
        elif side == 'sell':
            _price = quote['closeBid']
        else:
            raise ValueError('Invalid side -- should be \'buy\' or \'sell\'')
        order = OrderHandler(acc, side, amount, ccy, _price, kind=_type).send_order()
    elif summary:
        symbols = summary[0].split(',')
        risk = Risk(acc).summary(symbols)
