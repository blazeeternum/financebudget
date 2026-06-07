from datetime import date, datetime
from sqlalchemy import func
from ..models import Transaction, Account
from .currency_service import convert_to_base

def add_transaction(session, tx_date, account_id, category_id, tx_type, amount, currency_code, description=""):
    amount_base = convert_to_base(session, amount, currency_code)
    
    tx = Transaction(
        date=tx_date,
        account_id=account_id,
        category_id=category_id,
        type=tx_type,
        original_amount=amount,
        original_currency=currency_code,
        amount_base=amount_base,
        description=description
    )
    session.add(tx)
    session.commit()
    
    # Refresh to load relationships for notification
    session.refresh(tx)
    
    # Check budget and send Telegram notification if needed
    try:
        from .notification_service import check_budget_and_notify
        check_budget_and_notify(session, tx)
    except Exception as e:
        print(f"Notification check failed: {e}")
    
    return tx

def get_transactions(session, limit=100):
    return session.query(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit).all()

def get_monthly_summary(session, year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year+1, 1, 1)
    else:
        end = date(year, month+1, 1)
    
    income = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.type == "income",
        Transaction.date >= start,
        Transaction.date < end
    ).scalar() or 0
    
    expense = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.type == "expense",
        Transaction.date >= start,
        Transaction.date < end
    ).scalar() or 0
    
    return {"income": income, "expense": expense, "net": income - expense}

def get_account_balance(session, account):
    tx_sum = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.account_id == account.id
    ).scalar() or 0
    
    # For expenses, amount_base is positive but should subtract
    # We'll store all as positive and apply sign by type
    income_sum = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.account_id == account.id,
        Transaction.type == "income"
    ).scalar() or 0
    
    expense_sum = session.query(func.sum(Transaction.amount_base)).filter(
        Transaction.account_id == account.id,
        Transaction.type == "expense"
    ).scalar() or 0
    
    # Convert initial balance to base
    from .currency_service import convert_to_base
    initial_base = convert_to_base(session, account.initial_balance, account.currency_code)
    
    return initial_base + income_sum - expense_sum

def get_total_balance(session):
    total = 0
    for acc in session.query(Account).all():
        total += get_account_balance(session, acc)
    return total