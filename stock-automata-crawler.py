# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 02:40:23 2022

@author: wangn
"""

#imports

from bs4 import BeautifulSoup, NavigableString
import requests
import pprint
import json
import csv
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler

pp = pprint.PrettyPrinter(indent=4)

# Definitions, classess, etc

SUMMARY_LABELS = [
  ["Previous Close","PREV_CLOSE-value"  ],
  ["Open","OPEN-value"  ],
  ["Bid","BID-value"  ],
  ["Ask","ASK-value"  ],
  ["Day's range","DAYS_RANGE-value"  ],
  ["52 Week range","FIFTY_TWO_WK_RANGE-value"  ],
  ["Volume","TD_VOLUME-value"  ],
  ["Avg. Volume","AVERAGE_VOLUME_3MONTH-value"  ],
  ["Market Cap","MARKET_CAP-value"  ],
  ["Beta (5Y Monthly)","BETA_5Y-value"  ],
  ["PE Ratio (TTM)","PE_RATIO-value"  ],
  ["EPS (TTM)","EPS_RATIO-value"  ],
  ["Earnings Date","EARNINGS_DATE-value"  ],
  ["Forward Divident & Yield","DIVIDEND_AND_YIELD-value"  ],
  ["Ex-Dividend Date","EX_DIVIDEND_DATE-value"  ],
  ["1y Target Est","ONE_YEAR_TARGET_PRICE-value"  ]
]

# to acces: SUMMARY_LABELS[0][1]

class Label:
  def __init__(self, idnum, label, dataTest, value):
    self.id = idnum
    self.label = label
    self.dataTest = dataTest
    self.value = value

class Stock:
    def __init__(self, name, symbol, information):
        self.name = name
        self.symbol = symbol
        self.information = information
    def getJson(self):
        informationToDump = self.information
        informationToDump["symbol"] = self.symbol
        return json.dumps(informationToDump)

def fillSummaryData(myStock):
    idforTheLabel =0
    url = "https://finance.yahoo.com/quote/"+myStock.symbol
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    print("researching: "+myStock.symbol)
    for labelToSearch in SUMMARY_LABELS:
        idforTheLabel+=1
#         print(labelToSearch[0])
        # Way to get the content of the soup.
        valueSearched="not found"
        if(labelToSearch[0]=="Volume" or labelToSearch[0]=="Earnings Date" or labelToSearch[0]=="Ex-Dividend Date"):
                try:
                    valueSearched = soup.find_all('td', attrs={"data-test":labelToSearch[1]})[0].contents[0].contents[0]
                except: 
                    valueSearched = "NA"
                    pass
                
        else:
            try:
                valueSearched = soup.find_all('td', attrs={"data-test":labelToSearch[1]})[0].contents[0]
            except:
                valueSearched = "NA"
                pass
        newLabelInfo = Label(idforTheLabel, labelToSearch[0], labelToSearch[1],valueSearched )
        myStock.information[labelToSearch[0]]=newLabelInfo.value if newLabelInfo.value!=None else "Not Found"
    


def getNanIfNull(strin):
    return str(strin).replace("'", "") if strin!=None else "None"


def updateBasedList(stockList):
    stockArray = []

    for stockSymbol in stockList:
        tmp_stock = Stock(stockSymbol, stockSymbol, dict())
        fillSummaryData(tmp_stock)
        stockArray.append(tmp_stock.getJson())

    requestObject = {}
    url = "https://codex-chan.wangnelson.xyz/public/api/stock/bulk-add"
    requestObject["jsonstock"] = (str(stockArray).replace("'","").replace("\\",""))
    # requestObject["jsonstock"] = stockArray
    # print(requestObject)
    x = requests.post(url, data = requestObject)
    
def getTODOStockList():
    url = "https://codex-chan.wangnelson.xyz/public/api/stock/symbolstosearch"
    response = requests.get(url)
    stockList = []
    for stockToSearch in response.json():
        stockList.append(stockToSearch["symbol"])
    return stockList


sched = BlockingScheduler()
@sched.scheduled_job('interval', hours=4)
def scheduled_job():
    print(getTODOStockList())
    updateBasedList(getTODOStockList())
sched.start()
