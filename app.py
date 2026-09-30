from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Portfolio, Transaction, Watchlist
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf
import pandas as pd

def calculate_recommendation(price, sma, rsi, macd, signal):
    score = 0

    # SMA condition
    if sma is not None:
        if price > sma:
            sma_signal = "Bullish"
            score += 1
        elif price < sma:
            sma_signal = "Bearish"
            score -= 1
        else:
            sma_signal = "Neutral"
    else:
        sma_signal = "Neutral"

    # RSI condition
    if rsi is not None:
        if rsi <= 30:
            rsi_signal = "Bullish"
            score += 1
        elif rsi >= 70:
            rsi_signal = "Bearish"
            score -= 1
        else:
            rsi_signal = "Neutral"
    else:
        rsi_signal = "Neutral"

    # MACD condition
    if macd is not None and signal is not None:
        if macd > signal:
            macd_signal = "Bullish"
            score += 1
        elif macd < signal:
            macd_signal = "Bearish"
            score -= 1
        else:
            macd_signal = "Neutral"
    else:
        macd_signal = "Neutral"

    # Final recommendation
    if score >= 2:
        recommendation = "BUY"
    elif score <= -2:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "score": score,
        "recommendation": recommendation,
        "sma_signal": sma_signal,
        "rsi_signal": rsi_signal,
        "macd_signal": macd_signal
    }

def get_stock_recommendation(symbol):
    """
    Fetch current price and calculate
    SMA, RSI, MACD and recommendation
    for a stock.
    """

    stock = yf.Ticker(symbol)

    # Latest available price
    data = stock.history(period="5d")

    if data.empty:
        return None

    current_price = float(data.iloc[-1]["Close"])

    # Historical data
    history = stock.history(period="3mo")

    if history.empty:
        return None

    # =====================================================
    # SMA 10
    # =====================================================

    history["SMA_10"] = (
        history["Close"]
        .rolling(window=10)
        .mean()
    )

    # =====================================================
    # RSI 14
    # =====================================================

    delta = history["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(window=14).mean()
    average_loss = loss.rolling(window=14).mean()

    rs = average_gain / average_loss

    history["RSI"] = 100 - (
        100 / (1 + rs)
    )

    # =====================================================
    # MACD
    # =====================================================

    ema_12 = history["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema_26 = history["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    history["MACD"] = ema_12 - ema_26

    history["Signal"] = history["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    # Latest indicators
    latest = history.iloc[-1]

    sma = latest["SMA_10"]
    rsi = latest["RSI"]
    macd = latest["MACD"]
    signal = latest["Signal"]

    # Convert values
    if pd.isna(sma):
        sma = None
    else:
        sma = round(float(sma), 2)

    if pd.isna(rsi):
        rsi = None
    else:
        rsi = round(float(rsi), 2)

    if pd.isna(macd):
        macd = None
    else:
        macd = round(float(macd), 2)

    if pd.isna(signal):
        signal = None
    else:
        signal = round(float(signal), 2)

    # Existing recommendation engine
    recommendation_data = calculate_recommendation(
        current_price,
        sma,
        rsi,
        macd,
        signal
    )

    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "score": recommendation_data["score"],
        "recommendation": recommendation_data["recommendation"]
    }

app = Flask(__name__)

app.secret_key = "tradeverse-development-key"


# SQLite database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tradeverse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Connect SQLAlchemy to Flask
db.init_app(app)


# Home route
@app.route("/")
def home():
    return "TradeVerse is running!"


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return "Registration successful!"

    return render_template("register.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.user_id
            session["user_name"] = user.name

            return redirect(url_for("dashboard"))

        return "Invalid email or password!"

    return render_template("login.html")


# Dashboard route
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    return render_template("dashboard.html", user=user)


# Logout route
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# Search route
@app.route("/search", methods=["POST"])
def search():

    if "user_id" not in session:
        return redirect(url_for("login"))

    symbol = request.form.get("symbol")

    if not symbol:
        return redirect(url_for("dashboard"))

    symbol = symbol.upper().strip()

    # Add NSE suffix if not provided
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    stock = yf.Ticker(symbol)

    # Latest available data
    data = stock.history(period="5d")

    if data.empty:
        return "Stock not found or no market data available."

    latest = data.iloc[-1]

    # Historical data
    history = stock.history(period="3mo")

    if history.empty:
        return "Historical market data is not available."

    # =========================================================
    # SMA 10
    # =========================================================

    history["SMA_10"] = (
        history["Close"]
        .rolling(window=10)
        .mean()
    )

    # =========================================================
    # RSI 14
    # =========================================================

    delta = history["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(window=14).mean()
    average_loss = loss.rolling(window=14).mean()

    rs = average_gain / average_loss

    history["RSI"] = 100 - (100 / (1 + rs))
                                
    # =========================================================
    # MACD
    # =========================================================

    ema_12 = history["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema_26 = history["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    history["MACD"] = ema_12 - ema_26   

    history["Signal"] = history["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    # =========================================================
    # Latest indicators
    # =========================================================

    latest_indicators = history.iloc[-1]

    sma = latest_indicators["SMA_10"]
    rsi = latest_indicators["RSI"]
    macd = latest_indicators["MACD"]
    signal = latest_indicators["Signal"]

    # Convert SMA to normal number
    if pd.isna(sma):
        sma = None
    else:
        sma = round(float(sma), 2)

    # Convert RSI to normal number
    if pd.isna(rsi):
        rsi = None
    else:
        rsi = round(float(rsi), 2)

    # Convert MACD to normal number
    if pd.isna(macd):
        macd = None
    else:
        macd = round(float(macd), 2)

    # Convert Signal to normal number
    if pd.isna(signal):
        signal = None
    else:
        signal = round(float(signal), 2)

    recommendation_data = calculate_recommendation(
        float(latest["Close"]),
        sma,
        rsi,
        macd,
        signal
        )
        
    # =========================================================
    # Stock information
    # =========================================================

    stock_data = {
        "symbol": symbol,
        "open": round(float(latest["Open"]), 2),
        "high": round(float(latest["High"]), 2),
        "low": round(float(latest["Low"]), 2),
        "close": round(float(latest["Close"]), 2),
        "volume": int(latest["Volume"]),
        "sma": sma,
        "rsi": rsi,
        "macd": macd,
        "signal": signal,
        "score": recommendation_data["score"],
        "recommendation": recommendation_data["recommendation"],
        "sma_signal": recommendation_data["sma_signal"],
        "rsi_signal": recommendation_data["rsi_signal"],
        "macd_signal": recommendation_data["macd_signal"]
    }     
        
    # =========================================================
    # Chart dates
    # =========================================================

    chart_dates = [
        date.strftime("%Y-%m-%d")
        for date in history.index
    ]

    # =========================================================
    # Closing prices
    # =========================================================

    chart_prices = [
        round(float(price), 2)
        for price in history["Close"]
    ]

    # =========================================================
    # SMA values for chart
    # =========================================================

    chart_sma = []

    for value in history["SMA_10"]:

        if pd.isna(value):
            chart_sma.append(None)
        else:
            chart_sma.append(round(float(value), 2))

    # =========================================================
    # MACD values for chart
    # =========================================================

    chart_macd = []

    for value in history["MACD"]:

        if pd.isna(value):
            chart_macd.append(None)
        else:
            chart_macd.append(round(float(value), 2))

    # =========================================================
    # Signal Line values for chart
    # =========================================================

    chart_signal = []

    for value in history["Signal"]:

        if pd.isna(value):
            chart_signal.append(None)
        else:
            chart_signal.append(round(float(value), 2))

    # =========================================================
    # RSI values for chart
    # =========================================================

    chart_rsi = []

    for value in history["RSI"]:

        if pd.isna(value):
            chart_rsi.append(None)
        else:
            chart_rsi.append(round(float(value), 2))

    # =========================================================
    # User trading information
    # =========================================================

    user = User.query.get(session["user_id"])

    holding = Portfolio.query.filter_by(
        user_id=user.user_id,
        symbol=symbol
    ).first()

    return render_template(
        "stock.html",
        stock=stock_data,
        chart_dates=chart_dates,
        chart_prices=chart_prices,
        chart_sma=chart_sma,
        chart_macd=chart_macd,
        chart_signal=chart_signal,
        chart_rsi=chart_rsi,
        user=user,
        holding=holding
    )

# =========================================================
# Virtual BUY
# =========================================================

@app.route("/buy", methods=["POST"])
def buy():

    if "user_id" not in session:
        return redirect(url_for("login"))

    symbol = request.form.get("symbol")
    quantity = request.form.get("quantity")

    # Check input
    if not symbol or not quantity:
        return "Please enter a stock symbol and quantity."

    symbol = symbol.upper().strip()

    try:
        quantity = int(quantity)
    except ValueError:
        return "Quantity must be a valid number."

    if quantity <= 0:
        return "Quantity must be greater than 0."

    # Get logged-in user
    user = User.query.get(session["user_id"])

    # Get latest stock price
    stock = yf.Ticker(symbol)
    data = stock.history(period="5d")

    if data.empty:
        return "Stock price data is not available."

    latest_price = float(data.iloc[-1]["Close"])

    # Calculate total purchase cost
    total_amount = latest_price * quantity

    # Check wallet balance
    if total_amount > user.virtual_balance:
        return "Insufficient virtual balance."

    # Check whether user already owns this stock
    holding = Portfolio.query.filter_by(
        user_id=user.user_id,
        symbol=symbol
    ).first()

    if holding:

        # Existing quantity
        old_quantity = holding.quantity

        # Existing total investment
        old_total = holding.average_price * old_quantity

        # New total investment
        new_total = old_total + total_amount

        # New quantity
        new_quantity = old_quantity + quantity

        # Calculate new average price
        new_average_price = new_total / new_quantity

        holding.quantity = new_quantity
        holding.average_price = new_average_price

    else:

        # Create new portfolio holding
        holding = Portfolio(
            user_id=user.user_id,
            symbol=symbol,
            quantity=quantity,
            average_price=latest_price
        )

        db.session.add(holding)

    # Deduct money from virtual wallet
    user.virtual_balance -= total_amount

    # Record transaction
    transaction = Transaction(
        user_id=user.user_id,
        symbol=symbol,
        transaction_type="BUY",
        quantity=quantity,
        price=latest_price,
        total_amount=total_amount
    )

    db.session.add(transaction)

    # Save everything
    db.session.commit()

    return (
        f"Successfully bought {quantity} shares of "
        f"{symbol} at ₹{latest_price:.2f}. "
        f"Total: ₹{total_amount:.2f}"
    )


# =========================================================
# Portfolio
# =========================================================

@app.route("/portfolio")
def portfolio():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    holdings = Portfolio.query.filter_by(
        user_id=user.user_id
    ).all()

    portfolio_data = []

    for holding in holdings:

        # Get latest available market price
        stock = yf.Ticker(holding.symbol)
        data = stock.history(period="5d")

        if data.empty:
            continue

        current_price = float(data.iloc[-1]["Close"])

        # Calculate invested value
        invested_value = (
            holding.quantity * holding.average_price
        )

        # Calculate current market value
        current_value = (
            holding.quantity * current_price
        )

        # Calculate profit/loss
        profit_loss = (
            current_value - invested_value
        )

        # Calculate profit/loss percentage
        if invested_value > 0:
            profit_loss_percent = (
                profit_loss / invested_value
            ) * 100
        else:
            profit_loss_percent = 0

        portfolio_data.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "average_price": round(holding.average_price, 2),
            "current_price": round(current_price, 2),
            "invested_value": round(invested_value, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percent": round(
                profit_loss_percent,
                2
            )
        })

    return render_template(
        "portfolio.html",
        user=user,
        holdings=portfolio_data
    )

# =========================================================
# Virtual SELL
# =========================================================

@app.route("/sell", methods=["POST"])
def sell():

    if "user_id" not in session:
        return redirect(url_for("login"))

    symbol = request.form.get("symbol")
    quantity = request.form.get("quantity")

    # Check input
    if not symbol or not quantity:
        return "Please enter a stock symbol and quantity."

    symbol = symbol.upper().strip()

    try:
        quantity = int(quantity)
    except ValueError:
        return "Quantity must be a valid number."

    if quantity <= 0:
        return "Quantity must be greater than 0."

    # Get logged-in user
    user = User.query.get(session["user_id"])

    # Find stock in user's portfolio
    holding = Portfolio.query.filter_by(
        user_id=user.user_id,
        symbol=symbol
    ).first()

    if not holding:
        return "You do not own this stock."

    # Check whether user owns enough shares
    if quantity > holding.quantity:
        return "You do not have enough shares to sell."

    # Get latest stock price
    stock = yf.Ticker(symbol)
    data = stock.history(period="5d")

    if data.empty:
        return "Stock price data is not available."

    latest_price = float(data.iloc[-1]["Close"])

    # Calculate selling amount
    total_amount = latest_price * quantity

    # Add money to virtual wallet
    user.virtual_balance += total_amount

    # Reduce portfolio quantity
    holding.quantity -= quantity

    # If all shares are sold, remove the holding
    if holding.quantity == 0:
        db.session.delete(holding)

    # Record SELL transaction
    transaction = Transaction(
        user_id=user.user_id,
        symbol=symbol,
        transaction_type="SELL",
        quantity=quantity,
        price=latest_price,
        total_amount=total_amount
    )

    db.session.add(transaction)

    # Save changes
    db.session.commit()

    return (
        f"Successfully sold {quantity} shares of "
        f"{symbol} at ₹{latest_price:.2f}. "
        f"Total received: ₹{total_amount:.2f}"
    )

# =========================================================
# Transaction History
# =========================================================

@app.route("/transactions")
def transactions():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    transaction_history = Transaction.query.filter_by(
        user_id=user.user_id
    ).order_by(
        Transaction.timestamp.desc()
    ).all()

    return render_template(
        "transactions.html",
        user=user,
        transactions=transaction_history
    )

# =========================================================
# Watchlist
# =========================================================

@app.route("/watchlist")
def watchlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    watchlist_items = Watchlist.query.filter_by(
        user_id=user.user_id
    ).all()

    watchlist_data = []

    suggested_symbols = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "ITC.NS",
        "LT.NS",
        "AXISBANK.NS",
        "BHARTIARTL.NS"
    ]

    suggested_data = []

    for symbol in suggested_symbols:

        # Don't show stocks already in user's watchlist
        already_added = Watchlist.query.filter_by(
            user_id=user.user_id,
            symbol=symbol
        ).first()

        if already_added:
            continue

        result = get_stock_recommendation(symbol)

        if result:
            suggested_data.append(result)

    for item in watchlist_items:

        stock = yf.Ticker(item.symbol)

        # Latest available data
        data = stock.history(period="5d")

        if data.empty:
            continue

        latest = data.iloc[-1]

        current_price = round(
            float(latest["Close"]),
            2
        )

        # Historical data for indicators
        history = stock.history(period="3mo")

        if history.empty:
            continue

        # =====================================================
        # SMA 10
        # =====================================================

        history["SMA_10"] = (
            history["Close"]
            .rolling(window=10)
            .mean()
        )

        # =====================================================
        # RSI 14
        # =====================================================

        delta = history["Close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        average_gain = gain.rolling(window=14).mean()
        average_loss = loss.rolling(window=14).mean()

        rs = average_gain / average_loss

        history["RSI"] = 100 - (
            100 / (1 + rs)
        )

        # =====================================================
        # MACD
        # =====================================================

        ema_12 = history["Close"].ewm(
            span=12,
            adjust=False
        ).mean()

        ema_26 = history["Close"].ewm(
            span=26,
            adjust=False
        ).mean()

        history["MACD"] = ema_12 - ema_26

        history["Signal"] = history["MACD"].ewm(
            span=9,
            adjust=False
        ).mean()

        # Latest indicators
        latest_indicators = history.iloc[-1]

        sma = latest_indicators["SMA_10"]
        rsi = latest_indicators["RSI"]
        macd = latest_indicators["MACD"]
        signal = latest_indicators["Signal"]

        # Convert values
        if pd.isna(sma):
            sma = None
        else:
            sma = round(float(sma), 2)

        if pd.isna(rsi):
            rsi = None
        else:
            rsi = round(float(rsi), 2)

        if pd.isna(macd):
            macd = None
        else:
            macd = round(float(macd), 2)

        if pd.isna(signal):
            signal = None
        else:
            signal = round(float(signal), 2)

        # Existing recommendation engine
        recommendation_data = calculate_recommendation(
            current_price,
            sma,
            rsi,
            macd,
            signal
        )

        watchlist_data.append({
            "symbol": item.symbol,
            "current_price": current_price,
            "score": recommendation_data["score"],
            "recommendation": recommendation_data["recommendation"]
        })

    return render_template(
        "watchlist.html",
        user=user,
        watchlist=watchlist_data,
        suggested_stocks=suggested_data
    )

# =========================================================
# Add to Watchlist
# =========================================================

@app.route("/watchlist/add", methods=["POST"])
def add_watchlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    symbol = request.form.get("symbol")

    if not symbol:
        return "Stock symbol is required."

    symbol = symbol.upper().strip()
    
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    user = User.query.get(session["user_id"])

    # Check if stock is already in watchlist
    existing_item = Watchlist.query.filter_by(
        user_id=user.user_id,
        symbol=symbol
    ).first()

    if existing_item:
        return redirect(url_for("watchlist"))

    # Add stock
    watchlist_item = Watchlist(
        user_id=user.user_id,
        symbol=symbol
    )

    db.session.add(watchlist_item)
    db.session.commit()

    return redirect(url_for("watchlist"))

# =========================================================
# Remove from Watchlist
# =========================================================

@app.route("/watchlist/remove", methods=["POST"])
def remove_watchlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    symbol = request.form.get("symbol")

    if not symbol:
        return redirect(url_for("watchlist"))

    symbol = symbol.upper().strip()

    user = User.query.get(session["user_id"])

    watchlist_item = Watchlist.query.filter_by(
        user_id=user.user_id,
        symbol=symbol
    ).first()

    if not watchlist_item:
        return redirect(url_for("watchlist"))

    db.session.delete(watchlist_item)
    db.session.commit()

    return redirect(url_for("watchlist"))

    
# =============================================================
# Create database tables
# =============================================================

with app.app_context():
    db.create_all()


# =============================================================
# Run Flask application
# =============================================================

if __name__ == "__main__":
    app.run(debug=True)