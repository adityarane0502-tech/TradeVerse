# TradeVerse – Virtual Stock Trading Simulation Platform

## Project Overview

TradeVerse is a web-based virtual stock trading simulation platform developed as a final-year B.Sc. Computer Science project.

The system allows users to explore stock market information, analyze stocks using technical indicators, receive BUY/HOLD/SELL recommendations, and perform virtual stock transactions without using real money.

## Features

* User registration and login
* Virtual wallet with initial virtual balance
* Stock search using stock symbols
* Current and historical stock market data
* Stock price charts
* Technical analysis
* SMA (Simple Moving Average)
* RSI (Relative Strength Index)
* MACD-based analysis
* BUY/HOLD/SELL recommendation
* Virtual stock buying and selling
* Portfolio management
* Profit/Loss calculation
* Transaction history
* Stock watchlist

## Technology Stack

* **Programming Language:** Python
* **Web Framework:** Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite
* **ORM:** Flask-SQLAlchemy
* **Stock Data:** yfinance / Yahoo Finance
* **Data Processing:** Pandas, NumPy
* **Charts:** Chart.js

## Project Structure

```text
TradeVerse/
│
├── app.py
├── models.py
├── requirements.txt
├── check_database.py
├── check_wallet.py
├── test_yfinance.py
├── .gitignore
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── login.html
    ├── register.html
    ├── stock.html
    ├── portfolio.html
    ├── transactions.html
    └── watchlist.html
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/adityarane0502-tech/TradeVerse.git
```

### 2. Open the project folder

```bash
cd TradeVerse
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment on Windows

```powershell
venv\Scripts\Activate.ps1
```

### 5. Install required packages

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

The Flask development server will start locally. Open the localhost address displayed in the terminal in a web browser.

## Usage

1. Register a new user account.
2. Log in to the TradeVerse platform.
3. Search for a stock using its symbol.
4. View stock information, charts and technical analysis.
5. Check the generated BUY/HOLD/SELL recommendation.
6. Buy or sell stocks using the virtual wallet.
7. View holdings and profit/loss in the portfolio.
8. Check previous transactions.
9. Add stocks to the watchlist for monitoring.

## Important Note

TradeVerse is an educational stock market simulation project. It uses market data for analysis and provides virtual trading functionality. It does not involve real-money trading.

## Repository

GitHub Repository:

https://github.com/adityarane0502-tech/TradeVerse
