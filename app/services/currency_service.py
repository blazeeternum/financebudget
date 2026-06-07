from ..models import Currency
from datetime import datetime

DEFAULT_CURRENCIES = [
    {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM", "rate_to_base": 1.0, "is_base": True},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "rate_to_base": 3.45, "is_base": False},
    {"code": "USD", "name": "US Dollar", "symbol": "$", "rate_to_base": 4.66, "is_base": False},
    {"code": "EUR", "name": "Euro", "symbol": "€", "rate_to_base": 5.03, "is_base": False},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "rate_to_base": 0.0297, "is_base": False},
    {"code": "IDR", "name": "Indonesian Rupiah", "symbol": "Rp", "rate_to_base": 0.00030, "is_base": False},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "rate_to_base": 0.66, "is_base": False},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "rate_to_base": 5.90, "is_base": False},
]

def seed_currencies(session):
    for curr in DEFAULT_CURRENCIES:
        existing = session.get(Currency, curr["code"])
        if not existing:
            session.add(Currency(**curr))
    session.commit()

def get_base_currency(session):
    return session.query(Currency).filter_by(is_base=True).first()

def get_rate(session, code):
    curr = session.get(Currency, code)
    return curr.rate_to_base if curr else 1.0

def convert_to_base(session, amount, currency_code):
    rate = get_rate(session, currency_code)
    return amount * rate

def convert_from_base(session, amount_base, target_code):
    rate = get_rate(session, target_code)
    return amount_base / rate if rate else amount_base

def get_all_currencies(session):
    return session.query(Currency).order_by(Currency.is_base.desc(), Currency.code).all()

def update_rate(session, code, new_rate):
    curr = session.get(Currency, code)
    if curr and not curr.is_base:
        curr.rate_to_base = new_rate
        curr.updated_at = datetime.utcnow()
        session.commit()