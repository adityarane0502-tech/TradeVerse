from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Virtual trading wallet
    virtual_balance = db.Column(
        db.Float,
        nullable=False,
        default=100000.00
    )

    # Relationships
    portfolio = db.relationship(
        "Portfolio",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    transactions = db.relationship(
        "Transaction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    watchlist = db.relationship(
        "Watchlist",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Portfolio(db.Model):
    __tablename__ = "portfolio"

    portfolio_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    symbol = db.Column(
        db.String(20),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    average_price = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    symbol = db.Column(
        db.String(20),
        nullable=False
    )

    transaction_type = db.Column(
        db.String(10),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )


class Watchlist(db.Model):
    __tablename__ = "watchlist"

    watchlist_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    symbol = db.Column(
        db.String(20),
        nullable=False
    )