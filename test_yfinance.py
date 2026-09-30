import yfinance as yf

stock = yf.Ticker("TCS.NS")

data = stock.history(period="5d")

print(data)