import oanda_fx_api as ofx
import datetime as dt
                            
symbol = 'EUR_USD'

start = dt.datetime.now() - dt.timedelta(minutes=60)

acc = ofx.Account()
dat = ofx.GetCandles(acc, symbol, start=start).request()

entry_price = dat.ix[-1]['closeAsk'] - 0.0005

order = ofx.OrderHandler(acc, 'buy', 100000, symbol, entry_price, kind='limit')

order = order.send_order()
working_orders = order.working()
id = working_orders[0]['id']

order.delete(id)
print(order.working())