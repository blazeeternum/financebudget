from sqlalchemy import func
from ..models import Budget, Transaction, Category
from datetime import date

def set_budget(session, category_id, year, month, amount_limit):
    budget = session.query(Budget).filter_by(category_id=category_id, year=year, month=month).first()
    if budget:
        budget.amount_limit = amount_limit
    else:
        budget = Budget(category_id=category_id, year=year, month=month, amount_limit=amount_limit)
        session.add(budget)
    session.commit()
    return budget

def get_budgets_status(session, year, month):
    budgets = session.query(Budget).filter_by(year=year, month=month).all()
    results = []
    
    start = date(year, month, 1)
    end = date(year+1, 1, 1) if month == 12 else date(year, month+1, 1)
    
    for b in budgets:
        spent = session.query(func.sum(Transaction.amount_base)).filter(
            Transaction.category_id == b.category_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date < end
        ).scalar() or 0
        
        results.append({
            "budget": b,
            "spent": spent,
            "remaining": b.amount_limit - spent,
            "percent": (spent / b.amount_limit * 100) if b.amount_limit > 0 else 0
        })
    return results