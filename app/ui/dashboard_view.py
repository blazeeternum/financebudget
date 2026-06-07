from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QScrollArea, QHBoxLayout
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with welcome message
        header_layout = QHBoxLayout()
        title = QLabel("📊 Dashboard Overview")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e2e8f0; margin-bottom: 8px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content_widget = QWidget()
        self.grid = QGridLayout(content_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(20)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.refresh()
    
    def make_card(self, title, value, subtitle="", color="#3498db", icon=""):
        frame = QFrame()
        frame.setObjectName("cardFrame")
        frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 {color}, stop:1 {self.darken_color(color)});
                border-radius: 16px;
                padding: 0px;
            }}
        """)
        frame.setMinimumHeight(140)
        frame.setMaximumWidth(320)
        
        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(8)
        
        # Icon and title row
        top_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px; background: transparent;")
            top_layout.addWidget(icon_label)
        top_layout.addStretch()
        card_layout.addLayout(top_layout)
        
        # Title
        t = QLabel(title)
        t.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 14px; font-weight: 500; background: transparent;")
        card_layout.addWidget(t)
        
        # Value
        v = QLabel(value)
        v.setStyleSheet("color: white; font-size: 32px; font-weight: bold; background: transparent;")
        card_layout.addWidget(v)
        
        # Subtitle
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
            card_layout.addWidget(s)
        
        card_layout.addStretch()
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
            
            # Row 0: Main metrics
            self.grid.addWidget(self.make_card("Total Balance", f"{symbol}{total:,.2f}", "All accounts combined", "#2ecc71", "💰"), 0, 0)
            self.grid.addWidget(self.make_card("Monthly Income", f"{symbol}{summary['income']:,.2f}", f"This month ({today.strftime('%B')})", "#3498db", "📥"), 0, 1)
            self.grid.addWidget(self.make_card("Monthly Expense", f"{symbol}{summary['expense']:,.2f}", f"This month ({today.strftime('%B')})", "#e74c3c", "📤"), 0, 2)
            self.grid.addWidget(self.make_card("Net Savings", f"{symbol}{summary['net']:,.2f}", "Income - Expenses", "#9b59b6", "💵"), 0, 3)
            
            # Budgets section header
            budget_header = QLabel("🎯 Budget Status")
            budget_header.setStyleSheet("font-size: 20px; font-weight: 600; color: #e2e8f0; margin-top: 10px;")
            self.grid.addWidget(budget_header, 1, 0)
            
            # Budgets
            budgets = get_budgets_status(session, today.year, today.month)
            col = 0
            row = 1
            for i, b in enumerate(budgets[:6]):
                if col >= 4:
                    col = 0
                    row += 1
                
                cat = b["budget"].category
                pct = b["percent"]
                spent = b.get("spent", 0)
                limit = b["budget"].amount_limit
                
                # Color based on usage
                if pct < 50:
                    color = "#2ecc71"  # Green - good
                elif pct < 80:
                    color = "#f39c12"  # Orange - warning
                elif pct < 100:
                    color = "#e67e22"  # Dark orange - caution
                else:
                    color = "#e74c3c"  # Red - over budget
                
                card = self.make_card(
                    f"{cat.icon} {cat.name}", 
                    f"{pct:.0f}%", 
                    f"{symbol}{spent:,.0f} / {symbol}{limit:,.0f}",
                    color
                )
                self.grid.addWidget(card, row + 1, col)
                col += 1