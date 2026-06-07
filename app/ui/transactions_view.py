from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from ..database import get_session
from ..services.transaction_service import get_transactions, add_transaction
from ..services.import_service import import_csv
from ..models import Account
from .dialogs import AddTransactionDialog
import pandas as pd

class TransactionsView(QWidget):
    def __init__(self, dashboard_callback=None):
        super().__init__()
        self.dashboard_callback = dashboard_callback
        layout = QVBoxLayout(self)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Transaction")
        self.import_btn = QPushButton("Import CSV")
        self.export_btn = QPushButton("Export Excel")
        self.refresh_btn = QPushButton("Refresh")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Account", "Category", "Type", "Amount", "Curr", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.add_tx)
        self.refresh_btn.clicked.connect(self.load_data)
        self.import_btn.clicked.connect(self.import_csv)
        self.export_btn.clicked.connect(self.export_excel)
        
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            txs = get_transactions(session, 200)
            self.table.setRowCount(len(txs))
            for i, tx in enumerate(txs):
                self.table.setItem(i, 0, QTableWidgetItem(str(tx.date)))
                self.table.setItem(i, 1, QTableWidgetItem(tx.account.name))
                self.table.setItem(i, 2, QTableWidgetItem(f"{tx.category.icon} {tx.category.name}"))
                self.table.setItem(i, 3, QTableWidgetItem(tx.type))
                
                amt_item = QTableWidgetItem(f"{tx.original_amount:,.2f}")
                amt_item.setForeground(Qt.darkGreen if tx.type == "income" else Qt.darkRed)
                self.table.setItem(i, 4, amt_item)
                
                self.table.setItem(i, 5, QTableWidgetItem(tx.original_currency))
                self.table.setItem(i, 6, QTableWidgetItem(tx.description))
        if self.dashboard_callback:
            self.dashboard_callback()
    
    def add_tx(self):
        dlg = AddTransactionDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            with get_session() as session:
                add_transaction(session, **data)
            self.load_data()
    
    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        with get_session() as session:
            acc = session.query(Account).first()
            if not acc:
                QMessageBox.warning(self, "Error", "Create an account first")
                return
            count = import_csv(session, path, acc.id)
            QMessageBox.information(self, "Import", f"Imported {count} transactions")
            self.load_data()
    
    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "transactions.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        with get_session() as session:
            txs = get_transactions(session, 10000)
            data = []
            for tx in txs:
                data.append({
                    "Date": tx.date,
                    "Account": tx.account.name,
                    "Category": tx.category.name,
                    "Type": tx.type,
                    "Original Amount": tx.original_amount,
                    "Currency": tx.original_currency,
                    "Amount (MYR)": tx.amount_base,
                    "Description": tx.description
                })
            df = pd.DataFrame(data)
            df.to_excel(path, index=False, engine='openpyxl')
            QMessageBox.information(self, "Export", f"Exported {len(data)} transactions to Excel")