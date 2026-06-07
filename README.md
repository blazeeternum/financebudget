# Finance Budget - PySide6 Multi-Currency (MYR Default)

Full-featured personal finance budgeting software with Telegram bot.

## NEW Features Added
✅ **Default Currency: MYR** (Malaysian Ringgit)
✅ **Settings Page** - Edit exchange rates live, no code change
✅ **Account Management** - Full CRUD for accounts
✅ **Export to Excel** - One-click export with openpyxl
✅ **Dark Mode** - Toggle in Settings
✅ **Category Icons Editor** - Change emoji & colors
✅ **Telegram Bot** - Add transactions via Telegram
✅ **Telegram Budget Alerts** - Auto-notify when exceed 80%/100%
✅ **.env Config** - Secure configuration

## Features
- Multi-Currency: MYR (base), SGD, USD, EUR, JPY, IDR, CNY, GBP
- Dashboard, Transactions, Budgets, Reports, Goals, Accounts, Categories
- Recurring transactions
- CSV Import / Excel Export

## Setup
```bash
cd finance-budget
pip install -r requirements.txt

# 1. Configure environment
cp .env.example .env
# Edit .env with your Telegram token

python main.py
```

## Telegram Setup (for bot + alerts)
1. Message @BotFather → /newbot → copy token
2. Edit `.env`:
```
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=your_id
```
3. Get Chat ID:
   - Message your new bot
   - Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
   - Copy your chat id number

4. Run bot:
```bash
python telegram_bot.py
```

**Budget Alerts:** Automatically sent when you add a transaction that pushes a category over 80% or 100% of budget.

## Settings
- Go to ⚙️ Settings tab
- Edit exchange rates live → Save Rates
- Toggle Dark Mode
- All data stored in SQLite

## Project Structure
```
├── telegram_bot.py
├── main.py
└── app/ui/
    ├── settings_view.py (NEW)
    ├── accounts_view.py (NEW)
    └── categories_view.py (NEW)
```
