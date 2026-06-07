import requests
from datetime import date
from sqlalchemy import func
from ..models import Budget, Transaction
from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, is_telegram_configured

# Track last notification to avoid spam (in-memory)
_last_notified = {}

def send_telegram_message(text):
    if not is_telegram_configured():
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram notification failed: {e}")
        return False

def check_budget_and_notify(session, transaction):
    """Check if transaction causes budget to exceed and notify"""
    if transaction.type != "expense":
        return
    
    tx_date = transaction.date
    year, month = tx_date.year, tx_date.month
    
    # Get budget for this category
    budget = session.query(Budget).filter_by(
        category_id=transaction.category_id,
        year=year,
        month=month
    ).first()
    
    if not budget or budget.amount_limit <= 0:
        return
    
    # Calculate total spent this month
    start = date(year, month, 1)
    end = date(year+1, 1, 1) if month == 12 else date(year, month+1, 1)
    
    spent = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.category_id == transaction.category_id,
        Transaction.type == "expense",
        Transaction.date >= start,
        Transaction.date < end
    ).scalar() or 0
    
    percent = (spent / budget.amount_limit) * 100
    category_name = transaction.category.name
    symbol = "RM"  # Base is MYR
    
    # Create unique key to prevent duplicate notifications
    key = f"{year}-{month}-{transaction.category_id}"
    last_percent = _last_notified.get(key, 0)
    
    message = None
    if percent >= 100 and last_percent < 100:
        message = (
            f"🚨 <b>Budget Exceeded!</b>\n\n"
            f"{transaction.category.icon} <b>{category_name}</b>\n"
            f"Spent: {symbol}{spent:,.2f} / {symbol}{budget.amount_limit:,.2f}\n"
            f"Over by: {symbol}{spent - budget.amount_limit:,.2f} ({percent:.0f}%)"
        )
        _last_notified[key] = 100
    elif percent >= 80 and last_percent < 80:
        message = (
            f"⚠️ <b>Budget Warning (80%)</b>\n\n"
            f"{transaction.category.icon} <b>{category_name}</b>\n"
            f"Spent: {symbol}{spent:,.2f} / {symbol}{budget.amount_limit:,.2f}\n"
            f"Remaining: {symbol}{budget.amount_limit - spent:,.2f}"
        )
        _last_notified[key] = 80
    
    if message:
        send_telegram_message(message)