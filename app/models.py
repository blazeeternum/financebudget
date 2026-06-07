from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .database import Base

class Currency(Base):
    __tablename__ = "currencies"
    code = Column(String(3), primary_key=True)  # SGD, USD
    name = Column(String(50), nullable=False)
    symbol = Column(String(5), nullable=False)
    rate_to_base = Column(Float, nullable=False, default=1.0)  # 1 unit = X SGD
    is_base = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), default="Cash")  # Cash, Bank, Credit
    currency_code = Column(String(3), ForeignKey("currencies.code"), default="SGD")
    initial_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    currency = relationship("Currency")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(20), nullable=False)  # income or expense
    color = Column(String(7), default="#3498db")
    icon = Column(String(10), default="💰")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=date.today)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    type = Column(String(20), nullable=False)  # income or expense
    
    original_amount = Column(Float, nullable=False)  # as entered
    original_currency = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    amount_base = Column(Float, nullable=False)  # converted to SGD
    
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category")
    currency = relationship("Currency")

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    amount_limit = Column(Float, nullable=False)  # in SGD base
    
    category = relationship("Category")

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), default="SGD")
    frequency = Column(String(20), default="monthly")  # daily, weekly, monthly
    next_date = Column(Date, nullable=False)
    description = Column(Text, default="")
    active = Column(Boolean, default=True)
    
    account = relationship("Account")
    category = relationship("Category")
    currency = relationship("Currency")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), default="SGD")
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    currency = relationship("Currency")