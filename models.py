from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token1_balance = db.Column(db.Float, default=10.0)
    token2_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Pool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token1_reserve = db.Column(db.Float, default=10.0)
    token2_reserve = db.Column(db.Float, default=1000.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 记录池子历史价格用于K线图
    history = db.relationship('PoolPriceHistory', backref='pool', lazy=True, cascade="all, delete-orphan")

    @property
    def product_constant(self):
        return self.token1_reserve * self.token2_reserve

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    transaction_type = db.Column(db.String(20), nullable=False)  # "token1_to_token2" or "token2_to_token1"
    token1_amount = db.Column(db.Float, nullable=False)
    token2_amount = db.Column(db.Float, nullable=False)
    fee_amount = db.Column(db.Float, default=0.0)  # 交易手续费
    slippage = db.Column(db.Float, default=0.0)  # 交易滑点百分比
    price = db.Column(db.Float, nullable=False)  # 交易价格
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id}: {self.transaction_type}>'

class PoolPriceHistory(db.Model):
    """用于记录池子价格历史，支持K线图"""
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'), nullable=False)
    open_price = db.Column(db.Float, nullable=False)  # 开盘价
    close_price = db.Column(db.Float, nullable=False)  # 收盘价
    high_price = db.Column(db.Float, nullable=False)  # 最高价
    low_price = db.Column(db.Float, nullable=False)  # 最低价
    volume = db.Column(db.Float, default=0.0)  # 交易量
    token1_reserve = db.Column(db.Float, nullable=False)  # 记录时的token1储备
    token2_reserve = db.Column(db.Float, nullable=False)  # 记录时的token2储备
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    period = db.Column(db.String(10), default='1h')  # 时间周期: 1h, 4h, 1d 等

    def __repr__(self):
        return f'<PoolPriceHistory {self.timestamp}: {self.close_price}>' 