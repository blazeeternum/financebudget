"""
Telegram Bot for Finance Budget
Commands:
 /start - welcome
 /balance - show total balance in MYR
 /add <amount> <currency> <category> <description> - quick add expense
   Example: /add 12.50 MYR Food lunch
 /income <amount> <currency> <category> <description>
 /summary - this month summary
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from app.database import init_db, get_session
from app.models import Account, Category
from app.services.transaction_service import add_transaction, get_total_balance, get_monthly_summary
from app.services.currency_service import get_base_currency
from app.config import TELEGRAM_BOT_TOKEN, is_telegram_configured

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Finance Budget Bot\n\n"
        "Commands:\n"
        "/balance - Total balance\n"
        "/summary - This month\n"
        "/add 12.5 MYR Food lunch - Add expense\n"
        "/income 3000 MYR Salary - Add income"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    with get_session() as session:
        total = get_total_balance(session)
        base = get_base_currency(session)
        symbol = base.symbol if base else "RM"
        await update.message.reply_text(f"💵 Total Balance: {symbol}{total:,.2f}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    with get_session() as session:
        today = date.today()
        s = get_monthly_summary(session, today.year, today.month)
        base = get_base_currency(session)
        symbol = base.symbol if base else "RM"
        msg = (
            f"📊 {today.strftime('%B %Y')}\n"
            f"Income: {symbol}{s['income']:,.2f}\n"
            f"Expense: {symbol}{s['expense']:,.2f}\n"
            f"Net: {symbol}{s['net']:,.2f}"
        )
        await update.message.reply_text(msg)

async def add_tx(update: Update, context: ContextTypes.DEFAULT_TYPE, tx_type="expense"):
    init_db()
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /add <amount> <currency> <category> <description>")
            return
        
        amount = float(args[0])
        currency = args[1].upper()
        category_name = args[2]
        description = " ".join(args[3:]) if len(args) > 3 else ""
        
        with get_session() as session:
            account = session.query(Account).first()
            category = session.query(Category).filter(Category.name.ilike(f"%{category_name}%"), Category.type == tx_type).first()
            
            if not account:
                await update.message.reply_text("No account found. Create one in app first.")
                return
            if not category:
                category = session.query(Category).filter_by(type=tx_type).first()
            
            add_transaction(
                session,
                tx_date=date.today(),
                account_id=account.id,
                category_id=category.id,
                tx_type=tx_type,
                amount=amount,
                currency_code=currency,
                description=description or f"via Telegram"
            )
            
            base = get_base_currency(session)
            await update.message.reply_text(f"✅ Added {tx_type}: {amount} {currency} to {category.name}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_tx(update, context, "expense")

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_tx(update, context, "income")

def main():
    if not is_telegram_configured() or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ERROR: Configure Telegram in .env file")
        print("1. Copy .env.example to .env")
        print("2. Get token from @BotFather on Telegram")
        print("3. Get your chat ID: message your bot, then visit:")
        print(f"   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
        return
    
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("income", add_income))
    
    print("Bot running... Press Ctrl+C to stop")
    app.run_polling()

if __name__ == "__main__":
    main()