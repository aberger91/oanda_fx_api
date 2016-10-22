import oanda_fx_api as ofx
                            
symbol = 'EUR_USD'

acc = ofx.Account()
dat = ofx.GetCandles(acc, symbol).request()

print(dat[['closeBid', 'closeAsk']].head())
print(dat.columns)