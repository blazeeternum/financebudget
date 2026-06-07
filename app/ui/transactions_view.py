from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog, QMessageBox, QLabel, QLineEdit, QFrame
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("💳 Transactions")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e2e8f0;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search transactions...")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 16px;
                border-radius: 8px;
                border: 2px solid #334155;
                background: #1e293b;
                color: #e2e8f0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Action buttons in a styled container
        btn_container = QFrame()
        btn_container.setObjectName("btnContainer")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        
        self.add_btn = QPushButton("➕ Add Transaction")
        self.import_btn = QPushButton("📥 Import CSV")
        self.export_btn = QPushButton("📤 Export Excel")
        self.refresh_btn = QPushButton("🔄 Refresh")
        
        for btn in [self.add_btn, self.import_btn, self.export_btn, self.refresh_btn]:
            btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        layout.addWidget(btn_container)
        
        # Table with enhanced styling
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Account", "Category", "Type", "Amount", "Curr", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.add_tx)
        self.refresh_btn.clicked.connect(self.load_data)
        self.import_btn.clicked.connect(self.import_csv)
        self.export_btn.clicked.connect(self.export_excel)
        
        self.load_data()
    
    def filter_table(self, text):
        """Filter table rows based on search text"""
        search_text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
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
        
        # Auto-resize columns
        self.table.resizeColumnsToContents()
        
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