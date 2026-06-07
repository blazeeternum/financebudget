import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "budget.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_session():
    return SessionLocal()

def init_db():
    from . import models
    from .services.currency_service import seed_currencies
    from .services.seed_data import seed_categories, seed_accounts
    
    Base.metadata.create_all(bind=engine)
    
    with get_session() as session:
        seed_currencies(session)
        seed_categories(session)
        seed_accounts(session)
        session.commit()