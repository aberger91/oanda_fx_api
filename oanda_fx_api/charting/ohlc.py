from bokeh.plotting import figure, output_file

def ohlc(bars, symbol='', freq=5, title=''):

    bars['date'] = bars.index
    
    start = bars['date'].ix[0]
    end = bars['date'].ix[-1]
    
    output_file('%s.html' % title)
    TOOLS = "pan, wheel_zoom, box_zoom, reset,save"
    
    w = 1000 * freq

    mids = (bars.open_mid + bars.close_mid) / 2
    spans = abs(bars.highAsk - bars.lowBid)

    inc = bars.close_mid > bars.open_mid
    dec = bars.open_mid > bars.close_mid

    p = figure(x_axis_type='datetime', tools=TOOLS, 
               plot_width=1000, title='%s // %s to %s - %s' % (
                                       title, start, end, symbol))
    p.left[0].formatter.use_scientific = False
    
    p.segment(bars.date, bars.highAsk, bars.date, bars.lowBid, color="black")
    
    p.rect(bars.date[inc], mids[inc], w, spans[inc], fill_color="#D5E1DD", line_color="black")
    p.rect(bars.date[dec], mids[dec], w, spans[dec], fill_color="#F2583E", line_color="black")
    return p
