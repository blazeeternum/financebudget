from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                               QDoubleSpinBox, QLineEdit, QPushButton, QDateEdit, QFormLayout)
from PySide6.QtCore import QDate
from datetime import date
from ..database import get_session
from ..models import Account, Category
from ..services.currency_service import get_all_currencies

class AddTransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Transaction")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["expense", "income"])
        self.type_combo.currentTextChanged.connect(self.update_categories)
        
        self.account_combo = QComboBox()
        self.category_combo = QComboBox()
        self.currency_combo = QComboBox()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMaximum(1_000_000)
        self.amount_spin.setMinimum(0.01)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(10.0)
        
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("e.g., Lunch at hawker")
        
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Account:", self.account_combo)
        layout.addRow("Category:", self.category_combo)
        layout.addRow("Currency:", self.currency_combo)
        layout.addRow("Amount:", self.amount_spin)
        layout.addRow("Description:", self.desc_edit)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)
        
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            accounts = session.query(Account).all()
            for acc in accounts:
                self.account_combo.addItem(f"{acc.name} ({acc.currency_code})", acc.id)
            
            for curr in get_all_currencies(session):
                self.currency_combo.addItem(f"{curr.code} - {curr.symbol}", curr.code)
            
            self.update_categories()
    
    def update_categories(self):
        self.category_combo.clear()
        tx_type = self.type_combo.currentText()
        with get_session() as session:
            cats = session.query(Category).filter_by(type=tx_type).all()
            for cat in cats:
                self.category_combo.addItem(f"{cat.icon} {cat.name}", cat.id)
    
    def get_data(self):
        return {
            "date": self.date_edit.date().toPython(),
            "type": self.type_combo.currentText(),
            "account_id": self.account_combo.currentData(),
            "category_id": self.category_combo.currentData(),
            "currency": self.currency_combo.currentData(),
            "amount": self.amount_spin.value(),
            "description": self.desc_edit.text()
        }