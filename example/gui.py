#!/c/users/andrew/anaconda3/python

import tkinter as tk
from tkinter import ttk
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.finance import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.transforms as mplt
from matplotlib.dates import num2date

import numpy as np
import pandas as pd
import datetime as dt
import talib
import requests

from positions import Positions, PnL
from compute import Signals
from order import OrderHandler
from account import Account

from multiprocessing import Queue, Process

# credentials
TOKEN_FILE = pd.read_csv("C:/Users/Andrew/Downloads/oandapackage/Tokens")
TOKEN_FILE.index = np.array([i for i in range(1, len(TOKEN_FILE)+1)])

TOKEN = TOKEN_FILE["token"][1]
S_ID = TOKEN_FILE["id"][1]
S_DOMAIN = TOKEN_FILE["venue"][1]
S_INSTRU = "EUR_USD"

# chart formatting
plt.rcParams["axes.labelcolor"] = "w"

# global variables
COUNT = 900
LONGWIN = COUNT * 0.25
SHORTWIN = COUNT * 0.50
SYMBOL = "EUR_USD"
GRAN = "S5"

def changeSymbol(msg):
        global SYMBOL
        SYMBOL = msg
        print("%s >> <changeSymbol> %s" % (dt.datetime.now(), msg))

def changeGran(msg):
        global GRAN
        GRAN = msg
        print("%s >> <changeGran> %s" % (dt.datetime.now(), msg))

def changeCount(msg):
        global COUNT
        global LONGWIN
        global SHORTWIN
        COUNT = msg #change COUNT
        LONGWIN = COUNT * 0.25
        SHORTWIN = COUNT * 0.50
        print("%s >> <changeCount> %s" % (dt.datetime.now(), msg))

class HistGraph:

        fig = plt.figure()

        ax = fig.add_subplot(211)
        ax.set_position(mplt.Bbox([[0.125, 0.27], [0.9, 0.9]]))

        ax4 = fig.add_subplot(212)
        ax4.set_position(mplt.Bbox([[0.125, 0.1], [0.9, 0.27]]))

        def __init__(self):
                HistGraph.ax.clear()
                HistGraph.ax4.clear()

                self.trade_logs, self.ticks = self.get_data()

        def __call__(self, date):
                self.__init__()
                fig = self.plot_historical_data(date)
                return fig

        def window(self, container):
                trade_logs, ticks = self.get_data()
                text = ttk.Text(container, height=30, width=10, state="disabled")
                text.pack(side=tk.LEFT)
                text.insert(END, trade_logs.describe())
        
        def get_data(self):
                trade_logs = pd.read_csv("C:/Users/andrew/Downloads/oandapackage/oanda_trade_logs",
                                                names=["time","id","side","symbol","amt",
                                                "price", "volume", "trend", "volatility", "K", "vwap",
                                                "ask", "bid", "total_volume"], skiprows=1)

                ticks = pd.read_csv("C:/Users/andrew/Downloads/oandapackage/oanda_ticks",
                                    sep=",",
                                    names=["time", "bid", "ask", "volume", "K", "trend",
                                           "vwap", "macd_hist", "volatility", "spread", "total_volume",
                                          "adx", "hammer", "invhammer"])
                self.total_days = pd.Series(np.unique(np.trunc(trade_logs["time"]/86400))).map(lambda x: dt.datetime.utcfromtimestamp(x*86400))
                self.symbol = trade_logs.ix[0]["symbol"]
                return trade_logs, ticks

        def get_trades(self, exits):
                x = 0
                trades = []
                while x < len(exits):
                        row = exits.ix[x]
                        row_loc = self.trade_logs.index.get_loc(exits.index[x])
                        if row["symbol"] == "30000":
                                trade_one = row_loc - 3
                                trade_one = row_loc - 2
                                trade_two = row_loc - 1
                                trades.append(trade_one)
                                trades.append(trade_two)
                                trades.append(trade_three)
                        if row["symbol"] == "20000":
                                trade_one = row_loc - 2
                                trade_two = row_loc - 1
                                trades.append(trade_one)
                                trades.append(trade_two)
                        if row["symbol"] == "10000":
                                trade_one = row_loc - 1
                                trades.append(trade_one)
                        x += 1
                trades = self.trade_logs.ix[self.trade_logs.index[trades]]
                return trades

        def plot_historical_data(self, date, position=0):
                TREND_THRESH = 2.5

                date = str(date).replace("-", "")
                year, month, day = int(date[0:4]), int(date[4:6]), int(date[6:8])

                start = dt.datetime(year,int(month),int(day))
                end = dt.datetime(year,int(month),int(day)+1)
                
                start_ld = start + dt.timedelta(hours=5)
                start_us = start + dt.timedelta(hours=12)
                end_us = start + dt.timedelta(hours=21)

                self.trade_logs.index = self.trade_logs["time"].map(lambda x:dt.datetime.utcfromtimestamp(x))

                self.trade_logs = self.trade_logs.ix[(self.trade_logs.index>start)&(self.trade_logs.index<end)]
                
                self.trade_logs_ld = self.trade_logs.ix[(self.trade_logs.index>start_ld)&(self.trade_logs.index<start_us)]
                self.trade_logs_us = self.trade_logs.ix[(self.trade_logs.index>start_us)&(self.trade_logs.index<end_us)]
                self.trade_logs["trend"] = abs(self.trade_logs["trend"])
                self.trade_logs["volatility"] = abs(self.trade_logs["volatility"])
                self.ticks.index = self.ticks["time"].map(lambda x:dt.datetime.utcfromtimestamp(x))
                self.ticks = self.ticks.ix[(self.ticks.index>start)&(self.ticks.index<end)]
                self.ticks["trend"] = abs(self.ticks["trend"])
                self.ticks["volatility"] = abs(self.ticks["volatility"])
                self.ticks["macd_hist"] = abs(self.ticks["macd_hist"])
                self.ticks["closeMid"] = (self.ticks["ask"] + self.ticks["bid"]) / 2
                self.ticks["returns"] = self.ticks["closeMid"].pct_change()
                self.ticks["sigma"] = self.ticks["returns"].std()

                winner_exits = self.trade_logs.ix[((self.trade_logs["side"]=="long")|(self.trade_logs["side"]=="short"))&(self.trade_logs["price"]>0)]
                loser_exits = self.trade_logs.ix[((self.trade_logs["side"]=="long")|(self.trade_logs["side"]=="short"))&(self.trade_logs["price"]<0)]
                
                winner_exits_ld = self.trade_logs_ld.ix[((self.trade_logs_ld["side"]=="long")|(self.trade_logs_ld["side"]=="short"))&(self.trade_logs_ld["price"]>0)]
                loser_exits_ld = self.trade_logs_ld.ix[((self.trade_logs_ld["side"]=="long")|(self.trade_logs_ld["side"]=="short"))&(self.trade_logs_ld["price"]<0)]
                
                winner_exits_us = self.trade_logs_us.ix[((self.trade_logs_us["side"]=="long")|(self.trade_logs_us["side"]=="short"))&(self.trade_logs_us["price"]>0)]
                loser_exits_us = self.trade_logs_us.ix[((self.trade_logs_us["side"]=="long")|(self.trade_logs_us["side"]=="short"))&(self.trade_logs_us["price"]<0)]

                profit = winner_exits["price"].sum(); loss = loser_exits["price"].sum()
                PnL = profit + loss
                winner_trades = self.get_trades(winner_exits)
                loser_trades = self.get_trades(loser_exits)
                
                winner_trades_ld = self.get_trades(winner_exits_ld)
                loser_trades_ld = self.get_trades(loser_exits_ld)
                
                winner_trades_us = self.get_trades(winner_exits_us)
                loser_trades_us = self.get_trades(loser_exits_us)
                
                winner_mom = winner_trades.ix[winner_trades["trend"]>TREND_THRESH]
                loser_mom = loser_trades.ix[loser_trades["trend"]>TREND_THRESH]
                
                winner_rev = winner_trades.ix[winner_trades["trend"]<TREND_THRESH]
                loser_rev = loser_trades.ix[loser_trades["trend"]<TREND_THRESH]
                
                LEGEND_FONT = 8
                LABEL_FONT = 12

                buys = self.trade_logs.ix[self.trade_logs["side"]=="buy"]
                buy_exits = self.trade_logs.ix[self.trade_logs["side"]=="long"]
                sells = self.trade_logs.ix[self.trade_logs["side"]=="sell"]
                sell_exits = self.trade_logs.ix[self.trade_logs["side"]=="short"]

                # profitable trades and the exits
                winners = winner_trades
                winner_exits = winner_exits

                # profitable longs
                winner_long = winners.ix[winners["side"]=="buy"]
                winner_longex = winner_exits.ix[winner_exits["side"]=="long"]
                
                # profitable shorts
                winner_short = winners.ix[winners["side"]=="sell"]
                winner_shortex = winner_exits.ix[winner_exits["side"]=="short"]

                # negative return trades and the exits
                losers = loser_trades
                loser_exits = loser_exits

                # negative longs
                loser_long = losers.ix[losers["side"]=="buy"]
                loser_longex = loser_exits.ix[loser_exits["side"]=="long"]
                
                # negative shorts
                loser_short = losers.ix[losers["side"]=="sell"]
                loser_shortex = loser_exits.ix[loser_exits["side"]=="short"]

                markersize = 10
                #plt.grid(True)

                # plot bid and ask
                HistGraph.ax.plot(self.ticks.index, self.ticks[["bid", "ask"]], "--", linewidth=0.50)

                # plot profitable trades (long/short) and exits
                HistGraph.ax.plot(winner_long[winner_long["trend"]>TREND_THRESH].index, winner_long[winner_long["trend"]>TREND_THRESH]["price"],
                        "^",
                        label="W - Momentum Long",
                        markersize=markersize)
                HistGraph.ax.plot(winner_long[winner_long["trend"]<TREND_THRESH].index, winner_long[winner_long["trend"]<TREND_THRESH]["price"],
                        "^",
                        label="W - Reversion Long",
                        markersize=markersize)
                HistGraph.ax.plot(winner_longex.index, winner_longex["amt"],
                        "v",
                        label="W - Long Exit",
                       markersize=markersize)
                HistGraph.ax.plot(winner_short[winner_short["trend"]>TREND_THRESH].index, winner_short[winner_short["trend"]>TREND_THRESH]["price"],
                        "v",
                        label="W - Momentum Short",
                        markersize=markersize)
                HistGraph.ax.plot(winner_short[winner_short["trend"]<TREND_THRESH].index, winner_short[winner_short["trend"]<TREND_THRESH]["price"],
                        "v",
                        label="W - Reversion Short",
                        markersize=markersize)
                HistGraph.ax.plot(winner_shortex.index, winner_shortex["amt"],
                        "^",
                        label="W - Short Exit",
                       markersize=markersize)

                # plot current position if exists
                if position != 0:
                    HistGraph.ax.plot(self.ticks.index, [position.price for x in range(0, len(self.ticks.index))], "--")

                # plot negative return trades (long/short) and exit
                HistGraph.ax.plot(loser_long[loser_long["trend"]>TREND_THRESH].index, loser_long[loser_long["trend"]>TREND_THRESH]["price"],
                         "^",
                         label="L - Momentum Long",
                         markersize=markersize)
                HistGraph.ax.plot(loser_long[loser_long["trend"]<TREND_THRESH].index, loser_long[loser_long["trend"]<TREND_THRESH]["price"],
                         "^",
                         label="L - Reversion Long",
                         markersize=markersize)
                HistGraph.ax.plot(loser_longex.index, loser_longex["amt"],
                         "v",
                         label="L - Long Exit",
                         markersize=markersize)
                HistGraph.ax.plot(loser_short[loser_short["trend"]>TREND_THRESH].index, loser_short[loser_short["trend"]>TREND_THRESH]["price"],
                         "v",
                         label="L - Momentum Short",
                        markersize=markersize)
                HistGraph.ax.plot(loser_short[loser_short["trend"]<TREND_THRESH].index, loser_short[loser_short["trend"]<TREND_THRESH]["price"],
                         "v",
                         label="L - Reversion Short",
                        markersize=markersize)
                HistGraph.ax.plot(loser_shortex.index, loser_shortex["amt"],
                         "^",
                         label="L - Short Exit",
                        markersize=markersize)

                # HistGraph Legend
                HistGraph.ax.legend(mode="expand", 
                                    bbox_to_anchor=(0, 1, 1, 0.1), 
                                    loc=3, 
                                    ncol=4,
                                    fancybox=True, 
                                    fontsize=LEGEND_FONT)

                # total pnl
                self.pnl = self.trade_logs.ix[(self.trade_logs["side"]=="long")|(self.trade_logs["side"]=="short")]["price"]
                self.returns = self.pnl

                HistGraph.ax4.plot(self.pnl.index, self.pnl.cumsum(), label="Portfolio", linewidth=2.5)

                # axis label formatting
                for label in HistGraph.ax.xaxis.get_ticklabels():
                        label.set_visible(False)

                for label in HistGraph.ax4.xaxis.get_ticklabels():
                        label.set_rotation(25)
                        label.set_fontsize(LABEL_FONT)
                   
                # ylim formatting
                HistGraph.ax4.set_xlim([self.ticks.index[0], self.ticks.index[len(self.ticks)-1]])
                print("%s >> Called <plot_historical_data> for %s" % (dt.datetime.now(), date))

                return HistGraph.fig

class LiveGraph:

        SMALL = 8
        MED = 12
        LARGE = 18
        MARKERSIZE = 10

        fig = plt.figure()

        # main chart
        ax = fig.add_subplot(211)
        ax.set_position(mplt.Bbox([[0.125, 0.22], [0.9, 0.77]]))

        ax.set_ylabel("Price")

        # volume underlay
        ax1 = ax.twinx()
        ax1.set_position(mplt.Bbox([[0.125, 0.22], [0.9, 0.77]]))
        
        # bottom indicators
        ax2 = ax.twinx()
        ax2.set_ylim([0, 100])

        ax2.set_position(mplt.Bbox([[0.125, 0.1], [0.9, 0.22]]))
        ax2.yaxis.tick_right()
                                
        ax3 = ax.twinx()
        ax3.set_position(mplt.Bbox([[0.125, 0.77], [0.9, 0.9]]))
        tick = pd.Series()
        
        def animate(i):
                LiveGraph.ax.clear()
                LiveGraph.ax1.clear()
                LiveGraph.ax2.clear()
                LiveGraph.ax3.clear()

                LONGWIN = COUNT*0.25
                SHORTWIN = LONGWIN*0.50
                model = Signals(COUNT, 
                                SYMBOL, 
                                LONGWIN, 
                                SHORTWIN, 
                                granularity=GRAN)
                LiveGraph.tick = model.tick
                candles = model.candles; 

                candles_ohlc = candles["closeMid"].resample("T1", how="ohlc")
                candles_ohlc["time"] = candles_ohlc.index.map(lambda x: dt.datetime.timestamp(x))
                
                candles_ohlc = list(zip(candles_ohlc["time"],
                                        candles_ohlc["open"], 
                                        candles_ohlc["high"], 
                                        candles_ohlc["low"], 
                                        candles_ohlc["close"]))

                candlestick_ohlc(LiveGraph.ax, candles_ohlc, alpha=50, 
                                                             width=50,
                                                             colorup="g",
                                                             colordown="r")

                _open = candles["openMid"].values
                high = candles["highMid"].values
                low = candles["lowMid"].values
                close = candles["closeMid"].values

                # Matplotlib Graph
                LiveGraph.ax3.set_title("%s\n%s" % (candles.index[0], candles.index[len(candles)-1]), fontsize=LiveGraph.LARGE)
                LiveGraph.ax3.set_title("%s: %s %s" % (SYMBOL, GRAN, COUNT), loc="left", fontsize=LiveGraph.MED)

                LiveGraph.ax.plot(candles["timestamp"], candles["upper_band"], linewidth=0.5)
                LiveGraph.ax.plot(candles["timestamp"], candles["lower_band"], linewidth=0.5)

                LiveGraph.ax1.fill_between(candles["timestamp"], candles["volume"], alpha=0.25)
                LiveGraph.ax1.set_ylim([0, candles["volume"].max()*4])

                LiveGraph.ax2.plot(candles["timestamp"], candles["trend"], "--", label="trend")
                LiveGraph.ax2.legend(loc="best", fancybox=True, fontsize=LiveGraph.SMALL)

                LiveGraph.ax3.plot(candles["timestamp"], candles["K"], label="K")
                LiveGraph.ax3.plot(candles["timestamp"], candles["D"], label="d")

                LiveGraph.ax3.set_ylim([0, 100])

                # label formatting
                for label in LiveGraph.ax.xaxis.get_ticklabels():
                        label.set_visible(False)

                labels = pd.Series(np.unique(np.trunc(candles["timestamp"]*0.001))).map(lambda x: dt.datetime.fromtimestamp(x/0.001))
                LiveGraph.ax2.set_xticklabels(labels)
                for label in LiveGraph.ax2.xaxis.get_ticklabels():
                        label.set_rotation(18)

                print("%s >> Updating LiveGraph.fig <animate(i)> for %s" % (dt.datetime.now(), candles.index[len(candles)-1]))

def tick_label(label):
        def tick():
                data = Signals(COUNT, 
                                SYMBOL, 
                                LONGWIN, 
                                SHORTWIN).tick
                msg = "EUR_USD\nBID: %s\nAsk: %s\nVolume: %s\nTrend: %s\nVolatility: %s" % (data.closeBid, data.closeAsk, data.volume, data.trend, data.volatility)
                label.config(text=msg)
                label.after(5000, tick)
        #tick()

def getTicks():
        popup = tk.Tk()
        tk.Tk.wm_title(popup, "EUR_USD")

        label = ttk.Label(popup)
        label.pack(pady=10, padx=10)

        tick_label(label)

        button = ttk.Button(popup, text="Done", command=popup.destroy)
        button.pack(pady=10, padx=10)

        popup.mainloop()

def position_label(label):
        def check():
                tick = Signals(COUNT, 
                                SYMBOL, 
                                LONGWIN, 
                                SHORTWIN, 
                                GRAN).tick
                position = Positions().checkPosition("EUR_USD")
                if position.units == 0:
                        msg = "No open positions"
                else:
                        pnl = PnL(tick, position).get_pnl()
                        msg = "%s %s EUR_USD %s  PnL: %s" % (position.side, position.units, position.price, pnl)
                label.config(text=msg)
                label.after(5000, check)
        check()

def getPositions():
        popup = tk.Tk()
        tk.Tk.wm_title(popup, "Positions")
        label = ttk.Label(popup)
        label.pack(pady=10, padx=10)

        position_label(label)

        button = ttk.Button(popup, text="Done", command=popup.destroy)
        button.pack(pady=10, padx=10)

class Gui(tk.Tk):
        def __init__(self, *args, **kwargs):
                tk.Tk.__init__(self, *args, **kwargs)
                flip = ttk.Notebook(self)
                graph = HistGraph()

                self.symbols = ["AUD_USD", "EUR_USD", 
                                "EUR_JPY", "GBP_USD", 
                                "NZD_USD", "USD_CAD", 
                                "USD_JPY"]

                # Live Frame (First Page)
                self.container = ttk.Frame(flip, width=180, height=720, borderwidth=1, relief="groove")

                # Menu Bar
                self.add_menu()

                # Historical Frame (Second Page)
                self.container2 = ttk.Frame(flip, width=180, height=120, borderwidth=1, relief="groove")

                # Backtest Frame (Third Page)
                self.container4 = ttk.Frame(flip, width=180, height=120, borderwidth=1, relief="groove")

                # Transactions Frame (First Page)
                self.container3 = ttk.Frame(self, width=180, height=10, borderwidth=1, relief="groove")
                self.container3.pack(expand=1, anchor="n", fill="x", side=tk.BOTTOM, padx=1, pady=1)

                # Notebook Tabs
                flip.add(self.container, text="Live")
                flip.add(self.container2, text="Historical")
                flip.add(self.container4, text="Backtest")
                flip.pack(expand=1, fill="both", side=tk.BOTTOM, anchor="center", padx=1, pady=1)

                # Chart Live 
                self.live()

                # Get Transactions
                self.transactions()

                # Listbox of Dates
                self.listbox(graph)

                # Chart Historical (default)
                graph(20160408)

                # Show Historical Chart
                self.canvas2 = FigureCanvasTkAgg(graph.fig, self.container2)
                self.canvas2.get_tk_widget().pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=10, pady=10)
                toolbar = NavigationToolbar2TkAgg(self.canvas2, self.container2)

                # Historical CHART button
                self.hist()

        def listbox(self, graph):
                t_days = graph.total_days
                self.t_days_list = tk.Listbox(self.container2, width=18, height=len(t_days))
                for day in t_days:
                        self.t_days_list.insert(tk.END, day)	
                self.t_days_list.bind("<Return>", self.chart_hist)
                self.t_days_list.pack(side=tk.LEFT)

        def transactions(self):
                text = tk.Text(self.container3, height=5, width=125)
                text.pack(side=tk.BOTTOM)
                def get():
                        acc = Account()
                get()

        def live(self):
                # container 1
                label = ttk.Label(self.container, font=("Comic Sans",18))
                label.pack(pady=5, padx=5, side=tk.LEFT)
                tick_label(label)

                label_2 = ttk.Label(self.container, font=("Comic Sans", 16))
                label_2.pack(pady=5, padx=5, side=tk.TOP)
                position_label(label_2)
        
                canvas = FigureCanvasTkAgg(LiveGraph.fig, self.container)
                print(LiveGraph.tick)
                canvas.show()
                canvas.get_tk_widget().pack(expand=True, fill="both", padx=5, pady=5)

                toolbar = NavigationToolbar2TkAgg(canvas, self.container)

        def chart_hist(self, event):
                graph = HistGraph()
                d_index = [int(x) for x in self.t_days_list.curselection()][0]
                _date = graph.total_days[d_index]

                graph(_date)
                self.canvas2.draw()

        def hist(self):
                # container 2
                button = ttk.Button(self.container2, text="CHART", command=lambda: self.chart_hist(None))
                button.pack(side=tk.LEFT)

        def error_msg(self, msg):
                popup = tk.Tk()
                popup.wm_title(" !!!!! ")
                label = ttk.Label(popup, text=msg)
                label.pack(side="top", fill="x", pady=25)
                button = ttk.Button(popup, text="Ack", command=popup.destroy)
                button.pack()
                popup.mainloop()

        def quick_order(self):
                popup = tk.Tk()
                tk.Tk.wm_title(popup, "Quick Order")

                side = tk.IntVar()
                kind = tk.IntVar()
                amount = tk.StringVar()

                label = tk.Label(popup, text="Amount")
                label.pack()

                amt_entry = tk.Entry(popup, textvariable=amount)
                amount.set("10000")
                amt_entry.pack(pady=10, padx=10, expand=True)

                symbol_box = tk.Listbox(popup, width=7, height=len(self.symbols))
                for symbol in self.symbols:
                        symbol_box.insert(tk.END, symbol)
                symbol_box.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

                side_button = tk.Radiobutton(popup, text="Buy", variable=side, value=1)
                side.set(1)
                side_button.pack(pady=5, padx=5, expand=True)

                side_button = tk.Radiobutton(popup, text="Sell", variable=side, value=2)
                side_button.pack(pady=5, padx=5, expand=True)

                kind_button = tk.Radiobutton(popup, text="Market", variable=kind, value=1)
                kind.set(1)
                kind_button.pack(pady=5, padx=5, expand=True)

                kind_button = tk.Radiobutton(popup, text="Limit", variable=kind, value=2)
                kind_button.pack(pady=5, padx=5, expand=True)

                _kind = kind.get()
                side = side.get()
                _symbol = symbol_box.curselection()
                tick = LiveGraph.tick

                if _kind == 1: _kind = "market"
                else: _kind = "limit"

                if side == 1: side = "buy"
                else: side = "sell"

                print(_symbol)
                _symbol = self.symbols[_symbol]
                print(_symbol)
                order = OrderHandler(_symbol, tick, side, amount.get())
                order.kind = _kind

                order_button = ttk.Button(popup, text="Execute", command=order)
                order_button.pack(pady=5, padx=5, expand=True)
                
        def add_menu(self):
                menu = tk.Menu(self.container)
                filemenu = tk.Menu(menu, tearoff=0)
                filemenu.add_command(label="Exit", command=quit)
                menu.add_cascade(label="File", menu=filemenu)

                tk.Tk.config(self, menu=menu)

                c_symbol = tk.Menu(menu, tearoff=0)
                c_symbol.add_command(label="AUD_USD", command=lambda: changeSymbol("AUD_USD"))
                c_symbol.add_command(label="EUR_USD", command=lambda: changeSymbol("EUR_USD"))
                c_symbol.add_command(label="GBP_USD", command=lambda: changeSymbol("GBP_USD"))
                c_symbol.add_command(label="NZD_USD", command=lambda: changeSymbol("NZD_USD"))
                c_symbol.add_command(label="USD_CAD", command=lambda: changeSymbol("USD_CAD"))
                c_symbol.add_command(label="USD_CHF", command=lambda: changeSymbol("USD_CHF"))
                c_symbol.add_command(label="USD_JPY", command=lambda: changeSymbol("USD_JPY"))
                menu.add_cascade(label="Symbol", menu=c_symbol)

                c_count = tk.Menu(menu, tearoff=0)
                c_count.add_command(label="90", command=lambda: changeCount(90))
                c_count.add_command(label="270", command=lambda: changeCount(270))
                c_count.add_command(label="540", command=lambda: changeCount(540))
                c_count.add_command(label="900", command=lambda: changeCount(900))
                c_count.add_command(label="1800", command=lambda: changeCount(1800))
                c_count.add_command(label="3600", command=lambda: changeCount(3600))
                c_count.add_command(label="5000", command=lambda: changeCount(5000))
                menu.add_cascade(label="Count", menu=c_count)

                c_gran = tk.Menu(menu, tearoff=0)
                c_gran.add_command(label="S5", command=lambda: changeGran("S5"))
                c_gran.add_command(label="S15", command=lambda: changeGran("S15"))
                c_gran.add_command(label="S30", command=lambda: changeGran("S30"))
                c_gran.add_command(label="M1", command=lambda: changeGran("M1"))
                c_gran.add_command(label="M5", command=lambda: changeGran("M5"))
                c_gran.add_command(label="M15", command=lambda: changeGran("M15"))
                c_gran.add_command(label="H1", command=lambda: changeGran("H1"))
                c_gran.add_command(label="H8", command=lambda: changeGran("H8"))
                c_gran.add_command(label="D", command=lambda: changeGran("D"))
                menu.add_cascade(label="Granularity", menu=c_gran)

                trade = tk.Menu(menu, tearoff=0)
                trade.add_command(label="Manual Trading", command=lambda: self.error_msg("Manual trading is not implemented yet!"))
                trade.add_command(label="Automated Trading", command=lambda: self.error_msg("Automated trading is not implemented yet!"))
                menu.add_cascade(label="Trading", menu=trade)

                order = tk.Menu(menu, tearoff=0)
                order.add_command(label="Quick Order", command=self.quick_order)
                menu.add_cascade(label="Orders", menu=order)

                position = tk.Menu(menu, tearoff=0)
                position.add_command(label="View Positions", command=lambda: getPositions())
                position.add_command(label="View Orders", command=lambda: getOrders())
                position.add_command(label="Get Prices", command=lambda: getTicks())
                menu.add_cascade(label="Portfolio", menu=position)

class StartPage(tk.Frame):
        def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)

if __name__ == "__main__":
        app = Gui()
        ani = animation.FuncAnimation(LiveGraph.fig, LiveGraph.animate, interval=5000)
        app.mainloop()
