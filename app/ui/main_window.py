from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QScrollArea
from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QFont, QIcon
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
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        self.settings = QSettings("FinanceBudget", "App")
        
        # Process recurring on startup
        with get_session() as session:
            created = process_due(session)
            if created:
                print(f"Processed {created} recurring transactions")
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar navigation
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        main_layout.addWidget(content_frame, 1)
        
        # Stack widgets for views
        self.views = {}
        self.dashboard = DashboardView()
        self.transactions = TransactionsView(dashboard_callback=self.dashboard.refresh)
        self.budgets = BudgetsView()
        self.reports = ReportsView()
        self.goals = GoalsView()
        self.accounts = AccountsView()
        self.categories = CategoriesView()
        self.settings_view = SettingsView(theme_callback=self.apply_theme)
        
        self.views = {
            "dashboard": self.dashboard,
            "transactions": self.transactions,
            "budgets": self.budgets,
            "reports": self.reports,
            "goals": self.goals,
            "accounts": self.accounts,
            "categories": self.categories,
            "settings": self.settings_view
        }
        
        self.current_view = None
        self.show_view("dashboard")
        
        self.apply_theme(self.settings.value("dark_mode", True, type=bool))
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 40, 15, 30)
        layout.setSpacing(8)
        
        # App title
        title = QLabel("💰 Finance\nBudget")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #ffffff;
            padding: 20px 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("💳", "Transactions", "transactions"),
            ("🎯", "Budgets", "budgets"),
            ("📈", "Reports", "reports"),
            ("🏆", "Goals", "goals"),
            ("🏦", "Accounts", "accounts"),
            ("🏷️", "Categories", "categories"),
            ("⚙️", "Settings", "settings"),
        ]
        
        self.nav_buttons = {}
        for icon, text, view_id in nav_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName(f"nav_{view_id}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, v=view_id: self.show_view(v))
            layout.addWidget(btn)
            self.nav_buttons[view_id] = btn
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("v1.0")
        footer.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; padding: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        return sidebar
    
    def show_view(self, view_id):
        if self.current_view:
            self.current_view.hide()
        
        self.current_view = self.views.get(view_id)
        if self.current_view:
            layout = self.centralWidget().layout().itemAt(1).widget().layout()
            layout.addWidget(self.current_view)
            self.current_view.show()
            
            # Refresh data when switching views
            if view_id == "dashboard":
                self.dashboard.refresh()
            elif view_id == "reports":
                self.reports.plot()
        
        # Update button styles
        for vid, btn in self.nav_buttons.items():
            if vid == view_id:
                btn.setObjectName(f"nav_{vid}_active")
            else:
                btn.setObjectName(f"nav_{vid}")
            btn.setStyle(btn.style())
    
    def apply_theme(self, dark=False):
        self.settings.setValue("dark_mode", dark)
        if dark:
            self.setStyleSheet("""
                QMainWindow { 
                    background-color: #0f172a; 
                }
                
                #sidebar {
                    background: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #1e293b, stop:1 #0f172a);
                    border-right: 1px solid #334155;
                }
                
                #contentFrame {
                    background-color: #0f172a;
                }
                
                QPushButton#nav_dashboard, QPushButton#nav_transactions, 
                QPushButton#nav_budgets, QPushButton#nav_reports,
                QPushButton#nav_goals, QPushButton#nav_accounts,
                QPushButton#nav_categories, QPushButton#nav_settings {
                    background: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                }
                
                QPushButton#nav_dashboard:hover, QPushButton#nav_transactions:hover,
                QPushButton#nav_budgets:hover, QPushButton#nav_reports:hover,
                QPushButton#nav_goals:hover, QPushButton#nav_accounts:hover,
                QPushButton#nav_categories:hover, QPushButton#nav_settings:hover {
                    background: rgba(255,255,255,0.05);
                    color: #e2e8f0;
                }
                
                QPushButton#nav_dashboard_active, QPushButton#nav_transactions_active,
                QPushButton#nav_budgets_active, QPushButton#nav_reports_active,
                QPushButton#nav_goals_active, QPushButton#nav_accounts_active,
                QPushButton#nav_categories_active, QPushButton#nav_settings_active {
                    background: linear-gradient(90deg, #0ea5e9 0%, #0284c7 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    text-align: left;
                }
                
                QWidget { 
                    color: #e2e8f0; 
                    font-family: 'Segoe UI', 'SF Pro Display', Arial;
                    font-size: 14px;
                }
                
                QPushButton { 
                    padding: 12px 24px; 
                    border-radius: 10px; 
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #0ea5e9, stop:1 #0284c7);
                    color: white; 
                    font-weight: 600;
                    border: none;
                    min-width: 120px;
                }
                
                QPushButton:hover { 
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #0284c7, stop:1 #0369a1);
                }
                
                QPushButton:pressed {
                    background: #0369a1;
                }
                
                QPushButton:disabled {
                    background: #475569;
                    color: #94a3b8;
                }
                
                QTableWidget { 
                    background: #1e293b; 
                    gridline-color: #334155; 
                    border: 1px solid #334155;
                    border-radius: 12px;
                    alternate-background-color: #0f172a;
                    selection-background-color: #0ea5e9;
                    selection-color: white;
                }
                
                QTableWidget::item {
                    padding: 12px 16px;
                    border: none;
                }
                
                QTableWidget::item:hover {
                    background: #334155;
                }
                
                QTableWidget::item:selected {
                    background: #0ea5e9;
                    color: white;
                }
                
                QHeaderView::section { 
                    background: #334155; 
                    color: #e2e8f0; 
                    padding: 14px 16px; 
                    border: none;
                    border-bottom: 2px solid #475569;
                    font-weight: 600;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { 
                    background: #1e293b; 
                    border: 2px solid #334155; 
                    padding: 10px 16px; 
                    border-radius: 8px;
                    color: #e2e8f0;
                    selection-background-color: #0ea5e9;
                    font-size: 14px;
                }
                
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                    border: 2px solid #0ea5e9;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                    padding-right: 10px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #94a3b8;
                    margin-right: 10px;
                }
                
                QGroupBox { 
                    border: 2px solid #334155; 
                    border-radius: 12px;
                    margin-top: 16px; 
                    padding-top: 20px;
                    padding-left: 10px;
                    padding-right: 10px;
                    font-weight: 600;
                    font-size: 15px;
                    color: #cbd5e1;
                    background: #1e293b;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 16px;
                    padding: 0 10px;
                    color: #0ea5e9;
                }
                
                QLabel {
                    color: #e2e8f0;
                }
                
                QCheckBox {
                    spacing: 10px;
                    font-size: 14px;
                }
                
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 5px;
                    border: 2px solid #475569;
                    background: #1e293b;
                }
                
                QCheckBox::indicator:checked {
                    background: #0ea5e9;
                    border-color: #0ea5e9;
                }
                
                QCheckBox::indicator:hover {
                    border-color: #0ea5e9;
                }
                
                QScrollBar:vertical {
                    background: #1e293b;
                    width: 10px;
                    border-radius: 5px;
                }
                
                QScrollBar::handle:vertical {
                    background: #475569;
                    border-radius: 5px;
                    min-height: 30px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background: #64748b;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                
                QToolTip {
                    background: #334155;
                    color: #e2e8f0;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { 
                    background-color: #f8fafc; 
                }
                
                #sidebar {
                    background: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #ffffff, stop:1 #f1f5f9);
                    border-right: 1px solid #e2e8f0;
                }
                
                #contentFrame {
                    background-color: #f8fafc;
                }
                
                QPushButton#nav_dashboard, QPushButton#nav_transactions, 
                QPushButton#nav_budgets, QPushButton#nav_reports,
                QPushButton#nav_goals, QPushButton#nav_accounts,
                QPushButton#nav_categories, QPushButton#nav_settings {
                    background: transparent;
                    color: #64748b;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                }
                
                QPushButton#nav_dashboard:hover, QPushButton#nav_transactions:hover,
                QPushButton#nav_budgets:hover, QPushButton#nav_reports:hover,
                QPushButton#nav_goals:hover, QPushButton#nav_accounts:hover,
                QPushButton#nav_categories:hover, QPushButton#nav_settings:hover {
                    background: #f1f5f9;
                    color: #0f172a;
                }
                
                QPushButton#nav_dashboard_active, QPushButton#nav_transactions_active,
                QPushButton#nav_budgets_active, QPushButton#nav_reports_active,
                QPushButton#nav_goals_active, QPushButton#nav_accounts_active,
                QPushButton#nav_categories_active, QPushButton#nav_settings_active {
                    background: linear-gradient(90deg, #0ea5e9 0%, #0284c7 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    text-align: left;
                }
                
                QWidget { 
                    color: #0f172a; 
                    font-family: 'Segoe UI', 'SF Pro Display', Arial;
                    font-size: 14px;
                }
                
                QPushButton { 
                    padding: 12px 24px; 
                    border-radius: 10px; 
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #0ea5e9, stop:1 #0284c7);
                    color: white; 
                    font-weight: 600;
                    border: none;
                    min-width: 120px;
                }
                
                QPushButton:hover { 
                    background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #0284c7, stop:1 #0369a1);
                }
                
                QPushButton:pressed {
                    background: #0369a1;
                }
                
                QPushButton:disabled {
                    background: #cbd5e1;
                    color: #94a3b8;
                }
                
                QTableWidget { 
                    background: white; 
                    gridline-color: #e2e8f0; 
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    alternate-background-color: #f8fafc;
                    selection-background-color: #0ea5e9;
                    selection-color: white;
                }
                
                QTableWidget::item {
                    padding: 12px 16px;
                    border: none;
                }
                
                QTableWidget::item:hover {
                    background: #f1f5f9;
                }
                
                QTableWidget::item:selected {
                    background: #0ea5e9;
                    color: white;
                }
                
                QHeaderView::section { 
                    background: #f1f5f9; 
                    color: #334155; 
                    padding: 14px 16px; 
                    border: none;
                    border-bottom: 2px solid #e2e8f0;
                    font-weight: 600;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { 
                    background: white; 
                    border: 2px solid #e2e8f0; 
                    padding: 10px 16px; 
                    border-radius: 8px;
                    color: #0f172a;
                    selection-background-color: #0ea5e9;
                    font-size: 14px;
                }
                
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                    border: 2px solid #0ea5e9;
                }
                
                QGroupBox {
                    border: 2px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: 16px;
                    padding-top: 20px;
                    padding-left: 10px;
                    padding-right: 10px;
                    font-weight: 600;
                    font-size: 15px;
                    background: white;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 16px;
                    padding: 0 10px;
                    color: #0ea5e9;
                }
                
                QCheckBox {
                    spacing: 10px;
                    font-size: 14px;
                }
                
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 5px;
                    border: 2px solid #cbd5e1;
                    background: white;
                }
                
                QCheckBox::indicator:checked {
                    background: #0ea5e9;
                    border-color: #0ea5e9;
                }
                
                QCheckBox::indicator:hover {
                    border-color: #0ea5e9;
                }
                
                QScrollBar:vertical {
                    background: #f1f5f9;
                    width: 10px;
                    border-radius: 5px;
                }
                
                QScrollBar::handle:vertical {
                    background: #cbd5e1;
                    border-radius: 5px;
                    min-height: 30px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background: #94a3b8;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                
                QToolTip {
                    background: #ffffff;
                    color: #0f172a;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
            """)