from ..models import Category, Account

DEFAULT_CATEGORIES = [
    # Expense
    {"name": "Food & Dining", "type": "expense", "color": "#e74c3c", "icon": "🍔"},
    {"name": "Transport", "type": "expense", "color": "#3498db", "icon": "🚇"},
    {"name": "Shopping", "type": "expense", "color": "#9b59b6", "icon": "🛍️"},
    {"name": "Bills & Utilities", "type": "expense", "color": "#f39c12", "icon": "💡"},
    {"name": "Rent", "type": "expense", "color": "#d35400", "icon": "🏠"},
    {"name": "Entertainment", "type": "expense", "color": "#1abc9c", "icon": "🎬"},
    {"name": "Healthcare", "type": "expense", "color": "#2ecc71", "icon": "🏥"},
    # Income
    {"name": "Salary", "type": "income", "color": "#27ae60", "icon": "💼"},
    {"name": "Freelance", "type": "income", "color": "#16a085", "icon": "💻"},
    {"name": "Investment", "type": "income", "color": "#8e44ad", "icon": "📈"},
    {"name": "Other Income", "type": "income", "color": "#2c3e50", "icon": "💰"},
]

def seed_categories(session):
    for cat in DEFAULT_CATEGORIES:
        existing = session.query(Category).filter_by(name=cat["name"]).first()
        if not existing:
            session.add(Category(**cat))

def seed_accounts(session):
    if session.query(Account).count() == 0:
        session.add_all([
            Account(name="Cash Wallet", type="Cash", currency_code="MYR", initial_balance=500),
            Account(name="Maybank Savings", type="Bank", currency_code="MYR", initial_balance=15000),
            Account(name="Wise USD", type="Bank", currency_code="USD", initial_balance=1000),
        ])