# import requests
#
# # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=IBM&apikey=ZKQOIM1FPCK9ZVA5'
# r = requests.get(url)
# data = r.json()
#
# print(data)
#

import yfinance as yf

def get_stock_press_releases(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    news = ticker.get_news()
    return news

symbol = "AAPL"
press_releases = get_stock_press_releases(symbol)
for release in press_releases:
    print(f"Title: {release['title']}\nLink: {release['link']}\n")
