from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models import RecurringTransaction
from .transaction_service import add_transaction

def process_due(session):
    today = date.today()
    due = session.query(RecurringTransaction).filter(
        RecurringTransaction.active == True,
        RecurringTransaction.next_date <= today
    ).all()
    
    created = 0
    for r in due:
        add_transaction(
            session,
            tx_date=r.next_date,
            account_id=r.account_id,
            category_id=r.category_id,
            tx_type=r.type,
            amount=r.amount,
            currency_code=r.currency_code,
            description=f"[Recurring] {r.description}"
        )
        
        # Update next date
        if r.frequency == "daily":
            r.next_date += timedelta(days=1)
        elif r.frequency == "weekly":
            r.next_date += timedelta(weeks=1)
        else:  # monthly
            r.next_date += relativedelta(months=1)
        created += 1
    
    if created:
        session.commit()
    return created