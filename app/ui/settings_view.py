from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                               QPushButton, QHBoxLayout, QCheckBox, QMessageBox, QGroupBox, QLineEdit)
from PySide6.QtCore import Qt, QSettings
from ..database import get_session
from ..services.currency_service import get_all_currencies, update_rate, get_base_currency
from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, is_telegram_configured

class SettingsView(QWidget):
    def __init__(self, theme_callback=None):
        super().__init__()
        self.theme_callback = theme_callback
        self.settings = QSettings("FinanceBudget", "App")
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Telegram Config
        tg_box = QGroupBox("Telegram Notifications")
        tg_layout = QVBoxLayout()
        status = "✅ Configured" if is_telegram_configured() else "❌ Not configured - edit .env file"
        status_label = QLabel(f"Status: {status}")
        status_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        tg_layout.addWidget(status_label)
        
        token_display = f"{'*' * 12}{TELEGRAM_BOT_TOKEN[-6:]}" if TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 6 else "Not set"
        tg_layout.addWidget(QLabel(f"Bot Token: {token_display}"))
        tg_layout.addWidget(QLabel(f"Chat ID: {TELEGRAM_CHAT_ID or 'Not set'}"))
        info = QLabel("Budget alerts sent automatically at 80% and 100%")
        info.setStyleSheet("color: #64748b; font-style: italic; margin-top: 8px;")
        tg_layout.addWidget(info)
        tg_box.setLayout(tg_layout)
        layout.addWidget(tg_box)
        
        # Dark Mode
        theme_box = QGroupBox("Appearance")
        theme_layout = QHBoxLayout()
        self.dark_mode = QCheckBox("Enable Dark Mode")
        self.dark_mode.setChecked(self.settings.value("dark_mode", True, type=bool))
        self.dark_mode.toggled.connect(self.toggle_dark)
        theme_layout.addWidget(self.dark_mode)
        theme_layout.addStretch()
        theme_box.setLayout(theme_layout)
        layout.addWidget(theme_box)
        
        # Exchange Rates
        rates_box = QGroupBox("Exchange Rates (Live Editor)")
        rates_layout = QVBoxLayout()
        base = None
        with get_session() as session:
            base = get_base_currency(session)
        rates_layout.addWidget(QLabel(f"Base Currency: {base.code if base else 'MYR'} - All rates are 1 unit = X {base.code if base else 'MYR'}"))
        
        self.rates_table = QTableWidget()
        self.rates_table.setColumnCount(4)
        self.rates_table.setHorizontalHeaderLabels(["Code", "Name", "Symbol", "Rate to Base"])
        rates_layout.addWidget(self.rates_table)
        
        btn_layout = QHBoxLayout()
        self.save_rates_btn = QPushButton("Save Rates")
        self.save_rates_btn.clicked.connect(self.save_rates)
        btn_layout.addWidget(self.save_rates_btn)
        btn_layout.addStretch()
        rates_layout.addLayout(btn_layout)
        
        rates_box.setLayout(rates_layout)
        layout.addWidget(rates_box)
        
        layout.addStretch()
        self.load_rates()
    
    def load_rates(self):
        with get_session() as session:
            currencies = get_all_currencies(session)
            self.rates_table.setRowCount(len(currencies))
            for i, curr in enumerate(currencies):
                self.rates_table.setItem(i, 0, QTableWidgetItem(curr.code))
                self.rates_table.item(i, 0).setFlags(Qt.ItemIsEnabled)
                
                self.rates_table.setItem(i, 1, QTableWidgetItem(curr.name))
                self.rates_table.item(i, 1).setFlags(Qt.ItemIsEnabled)
                
                self.rates_table.setItem(i, 2, QTableWidgetItem(curr.symbol))
                self.rates_table.item(i, 2).setFlags(Qt.ItemIsEnabled)
                
                rate_item = QTableWidgetItem(f"{curr.rate_to_base:.6f}")
                if curr.is_base:
                    rate_item.setFlags(Qt.ItemIsEnabled)
                    rate_item.setBackground(Qt.lightGray)
                self.rates_table.setItem(i, 3, rate_item)
    
    def save_rates(self):
        with get_session() as session:
            for row in range(self.rates_table.rowCount()):
                code = self.rates_table.item(row, 0).text()
                try:
                    rate = float(self.rates_table.item(row, 3).text())
                    update_rate(session, code, rate)
                except:
                    pass
        QMessageBox.information(self, "Saved", "Exchange rates updated!")
        self.load_rates()
    
    def toggle_dark(self, checked):
        self.settings.setValue("dark_mode", checked)
        if self.theme_callback:
            self.theme_callback(checked)