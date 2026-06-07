from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt
from datetime import date
from ..database import get_session
from ..services.transaction_service import get_total_balance, get_monthly_summary
from ..services.budget_service import get_budgets_status
from ..services.currency_service import get_base_currency

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        layout.addStretch()
        
        self.refresh()
    
    def make_card(self, title, value, color="#3498db"):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 {color}, stop:1 {self.darken_color(color)});
                border-radius: 16px;
                padding: 16px;
            }}
        """)
        frame.setMinimumHeight(110)
        l = QVBoxLayout(frame)
        l.setContentsMargins(4, 4, 4, 4)
        t = QLabel(title)
        t.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 500; background: transparent;")
        v = QLabel(value)
        v.setStyleSheet("color: white; font-size: 26px; font-weight: bold; background: transparent; margin-top: 4px;")
        l.addWidget(t)
        l.addWidget(v)
        l.addStretch()
        return frame
    
    def darken_color(self, hex_color):
        # Simple darken for gradient
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            r = max(0, int(r*0.8)); g = max(0, int(g*0.8)); b = max(0, int(b*0.8))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def refresh(self):
        # Clear grid
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        with get_session() as session:
            base = get_base_currency(session)
            symbol = base.symbol if base else "S$"
            
            total = get_total_balance(session)
            today = date.today()
            summary = get_monthly_summary(session, today.year, today.month)
            
            self.grid.addWidget(self.make_card("Total Balance", f"{symbol}{total:,.2f}", "#2ecc71"), 0, 0)
            self.grid.addWidget(self.make_card("This Month Income", f"{symbol}{summary['income']:,.2f}", "#3498db"), 0, 1)
            self.grid.addWidget(self.make_card("This Month Expense", f"{symbol}{summary['expense']:,.2f}", "#e74c3c"), 0, 2)
            self.grid.addWidget(self.make_card("Net", f"{symbol}{summary['net']:,.2f}", "#9b59b6"), 1, 0)
            
            # Budgets
            budgets = get_budgets_status(session, today.year, today.month)
            row = 2
            for b in budgets[:4]:
                cat = b["budget"].category
                pct = b["percent"]
                color = "#2ecc71" if pct < 80 else "#f39c12" if pct < 100 else "#e74c3c"
                card = self.make_card(f"{cat.icon} {cat.name}", f"{pct:.0f}% used", color)
                self.grid.addWidget(card, row // 3, row % 3)
                row += 1