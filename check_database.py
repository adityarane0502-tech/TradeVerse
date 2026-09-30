from app import app
from models import User, Portfolio, Transaction


with app.app_context():

    user = User.query.first()

    print("\n===== WALLET =====")
    print("User:", user.name)
    print("Balance:", round(user.virtual_balance, 2))

    print("\n===== PORTFOLIO =====")

    holdings = Portfolio.query.filter_by(
        user_id=user.user_id
    ).all()

    for holding in holdings:
        print(
            "Symbol:",
            holding.symbol,
            "| Quantity:",
            holding.quantity,
            "| Average Price:",
            round(holding.average_price, 2)
        )

    print("\n===== TRANSACTIONS =====")

    transactions = Transaction.query.filter_by(
        user_id=user.user_id
    ).all()

    for transaction in transactions:
        print(
            "Type:",
            transaction.transaction_type,
            "| Symbol:",
            transaction.symbol,
            "| Quantity:",
            transaction.quantity,
            "| Price:",
            round(transaction.price, 2),
            "| Total:",
            round(transaction.total_amount, 2)
        )

    print("\n========================")