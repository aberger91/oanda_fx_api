import oanda_fx_api as ofx


if __name__ == '__main__':

    acc = ofx.Account()
    
    symbol = 'EUR_USD'
    granularity = 'S5'
    count = 1250
    
    dat = ofx.GetCandles(acc, symbol).request()
    print(dat[['closeBid', 'closeAsk']].head())
    
    exposure = ofx.Positions(acc, symbol)
    
    print()
    print(acc.id, acc.venue)
    print(exposure.get_position())
    
    signals = ofx.Signals(acc, 'EUR_USD')
    tick = signals.tick
    
    pre_order = ofx.OrderHandler(acc, 'EUR_USD', tick.closeAsk, 'buy', 10000, kind='limit')
    order = pre_order.send_order()
    