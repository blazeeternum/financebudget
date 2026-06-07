import pandas as pd
from datetime import datetime
from ..models import Category, Account
from .transaction_service import add_transaction

def import_csv(session, filepath, account_id, date_col="Date", desc_col="Description", amount_col="Amount", currency="SGD"):
    df = pd.read_csv(filepath)
    
    # Try to detect DBS/OCBC format
    df.columns = [c.strip() for c in df.columns]
    
    imported = 0
    for _, row in df.iterrows():
        try:
            tx_date = pd.to_datetime(row[date_col]).date()
            description = str(row[desc_col])
            amount = float(row[amount_col])
            
            tx_type = "income" if amount > 0 else "expense"
            amount = abs(amount)
            
            # Auto-categorize (simple)
            cat = session.query(Category).filter_by(type=tx_type).first()
            
            add_transaction(
                session,
                tx_date=tx_date,
                account_id=account_id,
                category_id=cat.id,
                tx_type=tx_type,
                amount=amount,
                currency_code=currency,
                description=description
            )
            imported += 1
        except Exception as e:
            print(f"Skip row: {e}")
            continue
    return imported