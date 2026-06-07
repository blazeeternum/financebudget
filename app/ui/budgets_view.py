from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QSpinBox, QLabel
from datetime import date
from ..database import get_session
from ..models import Category, Budget
from ..services.budget_service import set_budget, get_budgets_status
from ..services.currency_service import get_base_currency

class BudgetsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Month:"))
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1,12)
        self.month_spin.setValue(date.today().month)
        ctrl.addWidget(self.month_spin)
        
        ctrl.addWidget(QLabel("Year:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(date.today().year)
        ctrl.addWidget(self.year_spin)
        
        self.load_btn = QPushButton("Load")
        ctrl.addWidget(self.load_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Category", "Limit (MYR)", "Spent", "Remaining", "%"])
        layout.addWidget(self.table)
        
        self.save_btn = QPushButton("Save Budgets")
        layout.addWidget(self.save_btn)
        
        self.load_btn.clicked.connect(self.load_data)
        self.save_btn.clicked.connect(self.save_data)
        self.month_spin.valueChanged.connect(self.load_data)
        self.year_spin.valueChanged.connect(self.load_data)
        
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            cats = session.query(Category).filter_by(type="expense").all()
            self.table.setRowCount(len(cats))
            
            year = self.year_spin.value()
            month = self.month_spin.value()
            status_map = {s["budget"].category_id: s for s in get_budgets_status(session, year, month)}
            
            for i, cat in enumerate(cats):
                self.table.setItem(i, 0, QTableWidgetItem(f"{cat.icon} {cat.name}"))
                
                budget = session.query(Budget).filter_by(category_id=cat.id, year=year, month=month).first()
                limit = budget.amount_limit if budget else 0
                limit_item = QTableWidgetItem(str(int(limit)))
                limit_item.setData(256, cat.id)  # store id
                self.table.setItem(i, 1, limit_item)
                
                s = status_map.get(cat.id, {})
                spent = s.get("spent", 0)
                remaining = s.get("remaining", limit)
                pct = s.get("percent", 0)
                
                self.table.setItem(i, 2, QTableWidgetItem(f"{spent:.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{remaining:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{pct:.0f}%"))
    
    def save_data(self):
        with get_session() as session:
            year = self.year_spin.value()
            month = self.month_spin.value()
            for row in range(self.table.rowCount()):
                limit_item = self.table.item(row, 1)
                if not limit_item:
                    continue
                cat_id = limit_item.data(256)
                try:
                    limit = float(limit_item.text())
                    set_budget(session, cat_id, year, month, limit)
                except:
                    pass
        self.load_data()