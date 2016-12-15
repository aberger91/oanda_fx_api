import os
import json
import urllib
import requests
import oandaBETA
import matplotlib
import subprocess
import numpy as np
import pandas as pd
import tkinter as tk
import datetime as dt
from tkinter import *
matplotlib.use("TkAgg")
from tkinter import ttk
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

ACCESS_TOKEN = os.environ['OANDA_FX_TOKEN']
ACCOUNT_ID = os.environ['OANDA_FX_USER']

timeframe = 'M1'
instru = 'EUR_USD'
count = 500
			
LARGE_FONT= ("Verdana", 16)
style.use("ggplot")

f = plt.figure()
a = f.add_subplot(111)
g = Figure(figsize=(5,5), dpi=100)
b = g.add_subplot(111)

def changeTimeFrame(tf):
	global timeframe
	timeframe = tf

def changeInstrument(ins):
	global instru
	instru = ins

def changeCount(c):
	global count
	count = c
	
def animate(i):
	url = "https://" + 'api-fxpractice.oanda.com' + "/v1/candles"
	headers = {'Authorization' : 'Bearer ' + ACCESS_TOKEN}
	params = {'instrument' : instru,
			'granularity' : timeframe,
			'count' : count}
	req = requests.get(url, headers = headers, params = params).json()
	
	bidList = []
	askList = []
	timeList = []
	volumeList = []
	
	avgList = []
	
	x = 0
	while x < count:
		bids = req['candles'][x]['closeBid']
		asks = req['candles'][x]['closeAsk']
		times = req['candles'][x]['time']
		volume = req['candles'][x]['volume']
		
		timestamp = dt.datetime.strptime(str(times)[:-1], '%Y-%m-%dT%H:%M:%S.%f')
		
		bidList.append(bids)
		askList.append(asks)
		timeList.append(timestamp)
		volumeList.append(volume)
		
		x += 1
		
	a.clear()
	b.clear()
	
	a.plot_date(timeList, askList, "#00A3E0", label="asks")
	a.plot_date(timeList, bidList, "#183A54", label="bids")
	b.plot(timeList, volumeList, '#008000', label='volume')
	
	a.legend(loc='best')
	b.legend(loc=2)
			 
	title = str(instru) + ': ' + str(req['candles'][(count - 1)]['closeAsk']), str(req['candles'][(count - 1)]['closeBid'])
	title2 = 'Granularity: ', str(timeframe)
	a.set_title(title, loc='center')
	a.set_title(title2, loc='right')
	
class oandaGUI(tk.Tk):
	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, 'OANDA LiveTrade Account Client')

		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		
		menubar = tk.Menu(container, tearoff=0)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_separator()
		filemenu.add_command(label='Home', 
							command=lambda: self.show_frame(StartPage))
		filemenu.add_command(label='Exit', command=quit)
		menubar.add_cascade(label='File', menu=filemenu)
		
		dataTF = tk.Menu(menubar, tearoff=0)
		dataTF.add_command(label='S5',
							command=lambda: changeTimeFrame('S5'))
		dataTF.add_command(label='M1',
							command=lambda: changeTimeFrame('M1'))
		dataTF.add_command(label='M5',
							command=lambda: changeTimeFrame('M5'))
		dataTF.add_command(label='M15',
							command=lambda: changeTimeFrame('M15'))
		dataTF.add_command(label='M30',
							command=lambda: changeTimeFrame('M30'))
		dataTF.add_command(label='H1',
							command=lambda: changeTimeFrame('H1'))
		menubar.add_cascade(label='Time Frame', menu=dataTF)
		
		instruChoice = tk.Menu(menubar, tearoff=0)
		instruChoice.add_command(label='AUD/USD',
								command=lambda: changeInstrument('AUD_USD'))
		instruChoice.add_command(label='EUR/USD',
								command=lambda: changeInstrument('EUR_USD'))
		instruChoice.add_command(label='GBP/USD',
								command=lambda: changeInstrument('GBP_USD'))
		instruChoice.add_command(label='NZD/USD',
								command=lambda: changeInstrument('NZD_USD'))
		instruChoice.add_command(label='USD/CAD',
								command=lambda: changeInstrument('USD_CAD'))
		instruChoice.add_command(label='USD/CNH', 
								command=lambda: changeInstrument('USD_CNH'))
		instruChoice.add_command(label='USD/JPY',
								command=lambda: changeInstrument('USD_JPY'))
		menubar.add_cascade(label='Instrument', menu=instruChoice)
		
		countChange = tk.Menu(menubar, tearoff=0)
		countChange.add_command(label='50',
								command=lambda: changeCount(50))
		countChange.add_command(label='100',
								command=lambda: changeCount(100))
		countChange.add_command(label='150',
								command=lambda: changeCount(150))
		countChange.add_command(label='200',
								command=lambda: changeCount(200))
		countChange.add_command(label='250',
								command=lambda: changeCount(250))
		countChange.add_command(label='500',
								command=lambda: changeCount(500))
		countChange.add_command(label='1000',
								command=lambda: changeCount(1000))
		menubar.add_cascade(label='Bars', menu=countChange)
		
		tradeNow = tk.Menu(menubar, tearoff=0)
		tradeNow.add_command(label='WMA/SMA doubleCross',
							command=lambda: oandaBETA.trade())
		menubar.add_cascade(label='Trade', menu=tradeNow)
		
		tk.Tk.config(self, menu=menubar)
		self.frames = {}

		for F in (StartPage, PageOne, PageTwo, PageThree, PageFour):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame(StartPage)

	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
		
class StartPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self,parent)
		label = tk.Label(self, text='Home', font=LARGE_FONT)
		label.pack(pady=10,padx=10, side='top')

		button = ttk.Button(self, text="Positions",
							command=lambda: controller.show_frame(PageOne))
		button.pack()

		button2 = ttk.Button(self, text="Trade",
							command=lambda: controller.show_frame(PageTwo))
		button2.pack()

		button3 = ttk.Button(self, text="Graphs",
							command=lambda: controller.show_frame(PageThree))
		button3.pack()
		
		button4 = ttk.Button(self, text="Portfolio",
							command=lambda: controller.show_frame(PageFour))
		button4.pack()
		
		text = Text(self, height=10, width=50)
		text.pack(fill="both", expand=True)
		
		
class closeAll(object):	
	def __init__(self, instruments):
		self.instruments = instruments
		
	def _positions(self):
		instrument_list = list(
							['AUD_USD', 
							'EUR_USD', 
							'GBP_USD',
							'NZD_USD',
							'USD_CAD',
							'USD_CNH',
							'USD_JPY']
							)
		_info = []
		print('\n')
		print('\nClosing positions...\n')

		for i in self.instruments:
			for n in instrument_list:
				if i == n:
					s = requests.Session()
					url = "https://" + 'api-fxpractice.oanda.com' + "/v1/accounts/" + ACCOUNT_ID + "/positions/" + str(i)
					headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
					req = requests.Request('DELETE', url, headers=headers)
					pre = req.prepare()
					resp = s.send(pre, stream=True, verify=False)
					for line in resp:
						print('\nInstrument: ' + str(i))
						try:
							try:
								msg = json.loads(line.decode())
							except:
								print('\nError converting response to JSON\n')			
							if 'code' in msg:
								try:
									print(str(i) + ': None\n')
									print(msg['message'], '\n', msg['moreInfo'], '\n')
									try:
										msgdf = pd.Series(msg)
									except:
										print('Error converting JSON to PANDAS\n')	
									msgdf = list(msgdf)	
								except:
									print('Code found in message\n' + '\nError converting PANDAS to python list\n')
									return
							else:
								try:
									msgdf = pd.Series(msg)
									
									id = msgdf['ids']
									units = msgdf['totalUnits']
									price = msgdf['price']
									
									print('IDS: ', str(id),
									'Units: ', str(units),
									'Price: ', str(price)
									)
									
									print('\n')
								except:
									print('Error converting PANDAS to python list\n')			
						except:
							print("Error converting response\n")
							print(line)
		
class PageOne(tk.Frame):
	def getCurrent():
		url = "https://" + 'api-fxpractice.oanda.com' + "/v1/accounts/" + ACCOUNT_ID + "/positions/"
		headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN}
		req = requests.get(url, headers=headers).json()
		
		print('\n')
		print('--Positions--\n')
		
		x = 0
		while x < len(req['positions']):
			if req['positions'][x]['side'] == 'buy':
				side = 'Long'
			elif req['positions'][x]['side'] == 'sell':
				side = 'Short'
			else:
				side = 'none'
				
			units = req['positions'][x]['units']
			instrument = req['positions'][x]['instrument']
			price = req['positions'][x]['avgPrice']
				
			print(side, units, instrument, price)
			print('\n')
			x += 1
			
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Positions", font=LARGE_FONT)
		label.pack(pady=10,padx=10)
		done = PageOne

		button1 = ttk.Button(self, text="Back to Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()
		
		button2 = ttk.Button(self, text='Get Current Positions',
							command=done.getCurrent)
		button2.pack()
		
		button3 = ttk.Button(self, text='Close All Positions',
							command=close._positions)
		button3.pack()
		
		
class PageTwo(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Trade", font=LARGE_FONT)
		label.pack(pady=10,padx=10)

		button1 = ttk.Button(self, text="Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()

		button2 = ttk.Button(self, text="Positions",
							command=lambda: controller.show_frame(PageOne))
		button2.pack()
		
		#im = PhotoImage(file='/home/aberger91/Pictures/OANDA/Graphs/photo2.PNG')
		#label = tk.Label(self, image=im, 
						#text='Model_1\n' + 'SMA Momentum',
						#padx=10,
						#justify=LEFT)
		#label.pack(side='bottom')
		#label.image = im
		
		
class PageThree(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		text = tk.Label(self, text='Graphs', font=LARGE_FONT)
		text.pack(side='top')
		
		button1 = ttk.Button(self, text="Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack(side='top')
		
		canvas_1 = FigureCanvasTkAgg(f, self)
		canvas_1.show()
		canvas_1.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH)

		toolbar = NavigationToolbar2TkAgg(canvas_1, self)
		toolbar.update()
		canvas_1._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH)
		
		canvas_2 = FigureCanvasTkAgg(g, self)
		canvas_2.show()
		canvas_2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH)

		toolbar = NavigationToolbar2TkAgg(canvas_2, self)
		toolbar.update()
		canvas_2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH)
	

app = oandaGUI()
app.geometry('1280x720')

ani_1 = animation.FuncAnimation(f, animate, interval=1000)
ani_2 = animation.FuncAnimation(g, animate, interval=1000)

app.mainloop()
