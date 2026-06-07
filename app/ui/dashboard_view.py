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
        
        # Header with cyber styling
        header_layout = QHBoxLayout()
        title = QLabel("◈ DASHBOARD OVERVIEW")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #00ffff;
            font-family: 'Consolas', monospace;
            text-transform: uppercase;
            letter-spacing: 3px;
        """)
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
    
    def make_card(self, title, value, subtitle="", color="#00ffff", icon=""):
        frame = QFrame()
        frame.setObjectName("cyberCard")
        frame.setStyleSheet(f"""
            QFrame#cyberCard {{
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 rgba({self.hex_to_rgb(color)},0.15), stop:1 rgba({self.hex_to_rgb(color)},0.05));
                border: 2px solid {color};
                border-radius: 8px;
                padding: 0px;
            }}
        """)
        frame.setMinimumHeight(150)
        frame.setMaximumWidth(340)
        
        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(6)
        
        # Icon and title row
        top_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px; background: transparent;")
            top_layout.addWidget(icon_label)
        top_layout.addStretch()
        
        # Title label
        t = QLabel(title.upper())
        t.setStyleSheet(f"""
            color: {color}; 
            font-size: 11px; 
            font-weight: 700; 
            background: transparent;
            font-family: 'Consolas', monospace;
            letter-spacing: 2px;
            text-transform: uppercase;
        """)
        top_layout.addWidget(t)
        card_layout.addLayout(top_layout)
        
        # Value
        v = QLabel(value)
        v.setStyleSheet("""
            color: #ffffff; 
            font-size: 32px; 
            font-weight: bold; 
            background: transparent;
            font-family: 'Consolas', monospace;
        """)
        card_layout.addWidget(v)
        
        # Subtitle
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet("""
                color: rgba(0,255,255,0.6); 
                font-size: 11px; 
                background: transparent;
                font-family: 'Consolas', monospace;
            """)
            card_layout.addWidget(s)
        
        card_layout.addStretch()
        return frame
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple string"""
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            return f"{r},{g},{b}"
        except:
            return "0,255,255"
    
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
            
            # Row 0: Main metrics with cyber colors
            self.grid.addWidget(self.make_card("Total Balance", f"{symbol}{total:,.2f}", "All accounts combined", "#00ffff", "💰"), 0, 0)
            self.grid.addWidget(self.make_card("Monthly Income", f"{symbol}{summary['income']:,.2f}", f"This month ({today.strftime('%B')})", "#00ff00", "📥"), 0, 1)
            self.grid.addWidget(self.make_card("Monthly Expense", f"{symbol}{summary['expense']:,.2f}", f"This month ({today.strftime('%B')})", "#ff0055", "📤"), 0, 2)
            self.grid.addWidget(self.make_card("Net Savings", f"{symbol}{summary['net']:,.2f}", "Income - Expenses", "#ff9900", "💵"), 0, 3)
            
            # Budgets section header
            budget_header = QLabel("◪ BUDGET STATUS")
            budget_header.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #00ffff; 
                margin-top: 10px;
                font-family: 'Consolas', monospace;
                text-transform: uppercase;
                letter-spacing: 2px;
            """)
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
                
                # Cyber color scheme based on usage
                if pct < 50:
                    color = "#00ff00"  # Green - good
                elif pct < 80:
                    color = "#ffff00"  # Yellow - warning
                elif pct < 100:
                    color = "#ff9900"  # Orange - caution
                else:
                    color = "#ff0055"  # Red - over budget
                
                card = self.make_card(
                    f"{cat.icon} {cat.name}", 
                    f"{pct:.0f}%", 
                    f"{symbol}{spent:,.0f} / {symbol}{limit:,.0f}",
                    color
                )
                self.grid.addWidget(card, row + 1, col)
                col += 1
