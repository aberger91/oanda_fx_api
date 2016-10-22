Python Wrapper for the Oanda fxTrade Platform (REST-v20 API)
  - http://developer.oanda.com/rest-live-v20/introduction/

all packages used are included in the Anaconda distribution of Python 3.5:
  - https://docs.continuum.io/anaconda/

to install oanda_fx_api:

    git clone https://github.com/abberger1/fx_stoch_event_algo
    pip install .
  
dependencies:
  - pandas
  - statsmodels
  - bokeh

examples in IPython:
  
    >> import oanda_fx_api as ofx

    >> symbol = 'EUR_USD'

    >> acc = ofx.Account()
    >> candles = ofx.GetCandles(acc, symbol).request()

    >> entry_price = candles.iloc[-1]['closeAsk']
    >> exit_price = candles.iloc[-1]['closeBid']
 
    >> entry_order = OrderHandler(acc, 'buy', 100000, symbol, entry_price)
    >> order = pre_order.send_order()
 
    >> position = ofx.Positions(acc, symbol).get_position()

    >> exit_order = OrderHandler(acc, 'sell', 100000, symbol, exit_price)
    >> order = pre_order.send_order()

    >> position = ofx.Positions(acc, symbol).get_position()
