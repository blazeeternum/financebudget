from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QInputDialog
from ..database import get_session
from ..models import Goal
from ..services.currency_service import get_all_currencies

class GoalsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Goal")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Goal", "Target", "Current", "Progress", "Currency"])
        layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.add_goal)
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            goals = session.query(Goal).all()
            self.table.setRowCount(len(goals))
            for i, g in enumerate(goals):
                self.table.setItem(i, 0, QTableWidgetItem(g.name))
                self.table.setItem(i, 1, QTableWidgetItem(f"{g.target_amount:,.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{g.current_amount:,.2f}"))
                pct = (g.current_amount / g.target_amount * 100) if g.target_amount else 0
                self.table.setItem(i, 3, QTableWidgetItem(f"{pct:.0f}%"))
                self.table.setItem(i, 4, QTableWidgetItem(g.currency_code))
    
    def add_goal(self):
        name, ok = QInputDialog.getText(self, "New Goal", "Goal name:")
        if not ok or not name:
            return
        amount, ok = QInputDialog.getDouble(self, "Target", "Target amount:", 1000, 0, 1e9, 2)
        if not ok:
            return
        
        with get_session() as session:
            currencies = [c.code for c in get_all_currencies(session)]
            curr, ok = QInputDialog.getItem(self, "Currency", "Select:", currencies, 0, False)
            if not ok:
                curr = "SGD"
            session.add(Goal(name=name, target_amount=amount, currency_code=curr))
            session.commit()
        self.load_data()