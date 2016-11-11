Python Wrapper for the Oanda fxTrade Platform (REST-v20 API)
  - http://developer.oanda.com/rest-live-v20/introduction/

all packages used are included in the Anaconda distribution of Python 3.5:
  - https://docs.continuum.io/anaconda/

to install oanda_fx_api:

    git clone https://github.com/abberger1/fx_stoch_event_algo
    pip install .
  
dependencies:
  - pandas
  - numpy
  - bokeh
  - statsmodels

examples in IPython:
  
    >> import oanda_fx_api as ofx
    >> import datetime as dt

    >> acc = ofx.Account()

    >> start = dt.datetime.now() - dt.timedelta(minutes=60)
    >> candles = ofx.GetCandles(acc, 'EUR_USD', start=start).request()
    >> candles['closeMid'].plot()

    >> stream = ofx.StreamPrices('EUR_USD')
    >> stream.prices()
