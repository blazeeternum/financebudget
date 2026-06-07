from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QMessageBox)
from ..database import get_session
from ..models import Account
from ..services.currency_service import get_all_currencies
from ..services.transaction_service import get_account_balance

class AccountDialog(QDialog):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("Edit Account" if account else "Add Account")
        self.setMinimumWidth(350)
        
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit(account.name if account else "")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Cash", "Bank", "Credit Card", "E-Wallet", "Investment"])
        if account:
            self.type_combo.setCurrentText(account.type)
        
        self.currency_combo = QComboBox()
        with get_session() as session:
            for curr in get_all_currencies(session):
                self.currency_combo.addItem(f"{curr.code} - {curr.name}", curr.code)
        if account:
            idx = self.currency_combo.findData(account.currency_code)
            if idx >= 0:
                self.currency_combo.setCurrentIndex(idx)
        
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setMaximum(1e9)
        self.balance_spin.setMinimum(-1e9)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setValue(account.initial_balance if account else 0)
        
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Currency:", self.currency_combo)
        layout.addRow("Initial Balance:", self.balance_spin)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
    
    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "currency_code": self.currency_combo.currentData(),
            "initial_balance": self.balance_spin.value()
        }

class AccountsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Account")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Currency", "Initial", "Current Balance"])
        layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.add_account)
        self.edit_btn.clicked.connect(self.edit_account)
        self.delete_btn.clicked.connect(self.delete_account)
        
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            accounts = session.query(Account).all()
            self.table.setRowCount(len(accounts))
            for i, acc in enumerate(accounts):
                self.table.setItem(i, 0, QTableWidgetItem(acc.name))
                self.table.item(i, 0).setData(256, acc.id)
                self.table.setItem(i, 1, QTableWidgetItem(acc.type))
                self.table.setItem(i, 2, QTableWidgetItem(acc.currency_code))
                self.table.setItem(i, 3, QTableWidgetItem(f"{acc.initial_balance:,.2f}"))
                
                balance = get_account_balance(session, acc)
                self.table.setItem(i, 4, QTableWidgetItem(f"{balance:,.2f} MYR"))
    
    def add_account(self):
        dlg = AccountDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            with get_session() as session:
                session.add(Account(**data))
                session.commit()
            self.load_data()
    
    def edit_account(self):
        row = self.table.currentRow()
        if row < 0:
            return
        acc_id = self.table.item(row, 0).data(256)
        with get_session() as session:
            acc = session.get(Account, acc_id)
            dlg = AccountDialog(self, acc)
            if dlg.exec():
                data = dlg.get_data()
                for k, v in data.items():
                    setattr(acc, k, v)
                session.commit()
        self.load_data()
    
    def delete_account(self):
        row = self.table.currentRow()
        if row < 0:
            return
        acc_id = self.table.item(row, 0).data(256)
        if QMessageBox.question(self, "Confirm", "Delete account and all transactions?") == QMessageBox.Yes:
            with get_session() as session:
                acc = session.get(Account, acc_id)
                session.delete(acc)
                session.commit()
            self.load_data()