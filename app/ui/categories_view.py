from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                               QHBoxLayout, QInputDialog, QColorDialog, QMessageBox)
from PySide6.QtGui import QColor
from ..database import get_session
from ..models import Category

class CategoriesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Category")
        self.edit_icon_btn = QPushButton("Change Icon")
        self.edit_color_btn = QPushButton("Change Color")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_icon_btn)
        btn_layout.addWidget(self.edit_color_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Icon", "Name", "Type", "Color"])
        layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.add_category)
        self.edit_icon_btn.clicked.connect(self.edit_icon)
        self.edit_color_btn.clicked.connect(self.edit_color)
        
        self.load_data()
    
    def load_data(self):
        with get_session() as session:
            cats = session.query(Category).order_by(Category.type, Category.name).all()
            self.table.setRowCount(len(cats))
            for i, cat in enumerate(cats):
                icon_item = QTableWidgetItem(cat.icon)
                icon_item.setData(256, cat.id)
                self.table.setItem(i, 0, icon_item)
                self.table.setItem(i, 1, QTableWidgetItem(cat.name))
                self.table.setItem(i, 2, QTableWidgetItem(cat.type))
                
                color_item = QTableWidgetItem(cat.color)
                color_item.setBackground(QColor(cat.color))
                self.table.setItem(i, 3, color_item)
    
    def add_category(self):
        name, ok = QInputDialog.getText(self, "New Category", "Name:")
        if not ok or not name:
            return
        icon, ok = QInputDialog.getText(self, "Icon", "Emoji icon:", text="💰")
        if not ok:
            icon = "💰"
        type_, ok = QInputDialog.getItem(self, "Type", "Type:", ["expense", "income"], 0, False)
        if not ok:
            return
        
        with get_session() as session:
            session.add(Category(name=name, icon=icon, type=type_, color="#3498db"))
            session.commit()
        self.load_data()
    
    def edit_icon(self):
        row = self.table.currentRow()
        if row < 0:
            return
        cat_id = self.table.item(row, 0).data(256)
        icon, ok = QInputDialog.getText(self, "Change Icon", "New emoji:")
        if ok and icon:
            with get_session() as session:
                cat = session.get(Category, cat_id)
                cat.icon = icon
                session.commit()
            self.load_data()
    
    def edit_color(self):
        row = self.table.currentRow()
        if row < 0:
            return
        cat_id = self.table.item(row, 0).data(256)
        color = QColorDialog.getColor()
        if color.isValid():
            with get_session() as session:
                cat = session.get(Category, cat_id)
                cat.color = color.name()
                session.commit()
            self.load_data()