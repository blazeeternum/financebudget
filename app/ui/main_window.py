from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QSettings
from ..database import get_session
from ..services.recurring_service import process_due
from .dashboard_view import DashboardView
from .transactions_view import TransactionsView
from .budgets_view import BudgetsView
from .reports_view import ReportsView
from .goals_view import GoalsView
from .accounts_view import AccountsView
from .categories_view import CategoriesView
from .settings_view import SettingsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Budget - Multi-Currency (MYR)")
        self.setGeometry(100, 100, 1200, 750)
        
        self.settings = QSettings("FinanceBudget", "App")
        
        # Process recurring on startup
        with get_session() as session:
            created = process_due(session)
            if created:
                print(f"Processed {created} recurring transactions")
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.dashboard = DashboardView()
        self.transactions = TransactionsView(dashboard_callback=self.dashboard.refresh)
        self.budgets = BudgetsView()
        self.reports = ReportsView()
        self.goals = GoalsView()
        self.accounts = AccountsView()
        self.categories = CategoriesView()
        self.settings_view = SettingsView(theme_callback=self.apply_theme)
        
        self.tabs.addTab(self.dashboard, "📊 Dashboard")
        self.tabs.addTab(self.transactions, "💳 Transactions")
        self.tabs.addTab(self.budgets, "🎯 Budgets")
        self.tabs.addTab(self.reports, "📈 Reports")
        self.tabs.addTab(self.goals, "🏆 Goals")
        self.tabs.addTab(self.accounts, "🏦 Accounts")
        self.tabs.addTab(self.categories, "🏷️ Categories")
        self.tabs.addTab(self.settings_view, "⚙️ Settings")
        
        self.tabs.currentChanged.connect(self.on_tab_change)
        
        self.apply_theme(self.settings.value("dark_mode", True, type=bool))
    
    def apply_theme(self, dark=False):
        self.settings.setValue("dark_mode", dark)
        if dark:
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #0f172a; 
                    color: #e2e8f0; 
                    font-family: 'Segoe UI', Arial;
                    font-size: 13px;
                }
                QTabWidget::pane { 
                    border: none; 
                    background: #0f172a; 
                }
                QTabBar::tab { 
                    padding: 12px 24px; 
                    font-size: 14px; 
                    background: #1e293b; 
                    color: #94a3b8; 
                    border: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected { 
                    background: #334155; 
                    color: #f8fafc;
                    font-weight: 600; 
                }
                QTabBar::tab:hover {
                    background: #273549;
                    color: #e2e8f0;
                }
                QPushButton { 
                    padding: 10px 18px; 
                    border-radius: 8px; 
                    background: #0ea5e9; 
                    color: white; 
                    font-weight: 600;
                    border: none;
                }
                QPushButton:hover { 
                    background: #0284c7; 
                }
                QPushButton:pressed {
                    background: #0369a1;
                }
                QTableWidget { 
                    background: #1e293b; 
                    gridline-color: #334155; 
                    border: 1px solid #334155;
                    border-radius: 8px;
                    alternate-background-color: #0f172a;
                }
                QTableWidget::item {
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background: #0ea5e9;
                    color: white;
                }
                QHeaderView::section { 
                    background: #334155; 
                    color: #e2e8f0; 
                    padding: 10px; 
                    border: none;
                    font-weight: 600;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { 
                    background: #1e293b; 
                    border: 1px solid #475569; 
                    padding: 8px 12px; 
                    border-radius: 6px;
                    color: #e2e8f0;
                    selection-background-color: #0ea5e9;
                }
                QLineEdit:focus, QComboBox:focus {
                    border: 1px solid #0ea5e9;
                }
                QGroupBox { 
                    border: 1px solid #334155; 
                    border-radius: 8px;
                    margin-top: 12px; 
                    padding-top: 16px;
                    font-weight: 600;
                    color: #cbd5e1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                }
                QLabel {
                    color: #e2e8f0;
                }
                QCheckBox {
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 1px solid #475569;
                    background: #1e293b;
                }
                QCheckBox::indicator:checked {
                    background: #0ea5e9;
                    border-color: #0ea5e9;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { 
                    background-color: #f8fafc; 
                    color: #0f172a; 
                    font-family: 'Segoe UI', Arial;
                    font-size: 13px;
                }
                QTabWidget::pane { 
                    border: none; 
                    background: #f8fafc; 
                }
                QTabBar::tab { 
                    padding: 12px 24px; 
                    font-size: 14px; 
                    background: #e2e8f0; 
                    color: #475569; 
                    border: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected { 
                    background: white; 
                    color: #0f172a;
                    font-weight: 600; 
                }
                QTabBar::tab:hover {
                    background: #cbd5e1;
                }
                QPushButton { 
                    padding: 10px 18px; 
                    border-radius: 8px; 
                    background: #0ea5e9; 
                    color: white; 
                    font-weight: 600;
                    border: none;
                }
                QPushButton:hover { 
                    background: #0284c7; 
                }
                QTableWidget { 
                    background: white; 
                    gridline-color: #e2e8f0; 
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    alternate-background-color: #f8fafc;
                }
                QTableWidget::item {
                    padding: 8px;
                    color: #0f172a;
                }
                QTableWidget::item:selected {
                    background: #0ea5e9;
                    color: white;
                }
                QHeaderView::section { 
                    background: #f1f5f9; 
                    color: #334155; 
                    padding: 10px; 
                    border: none;
                    font-weight: 600;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { 
                    background: white; 
                    border: 1px solid #cbd5e1; 
                    padding: 8px 12px; 
                    border-radius: 6px;
                    color: #0f172a;
                }
                QLineEdit:focus {
                    border: 1px solid #0ea5e9;
                }
                QGroupBox {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 16px;
                    font-weight: 600;
                }
            """)
    
    def on_tab_change(self, index):
        if self.tabs.tabText(index).startswith("📊"):
            self.dashboard.refresh()
        elif self.tabs.tabText(index).startswith("📈"):
            self.reports.plot()