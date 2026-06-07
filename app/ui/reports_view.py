from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import date
from sqlalchemy import func
from ..database import get_session
from ..models import Transaction, Category

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Monthly Spending by Category"))
        
        self.canvas = FigureCanvas(Figure(figsize=(5,4)))
        layout.addWidget(self.canvas)
        self.plot()
    
    def plot(self):
        with get_session() as session:
            today = date.today()
            start = date(today.year, today.month, 1)
            
            data = session.query(
                Category.name,
                func.sum(Transaction.amount_base)
            ).join(Transaction).filter(
                Transaction.type == "expense",
                Transaction.date >= start
            ).group_by(Category.name).all()
            
            ax = self.canvas.figure.subplots()
            ax.clear()
            
            if data:
                labels = [d[0] for d in data]
                values = [d[1] for d in data]
                ax.pie(values, labels=labels, autopct='%1.1f%%')
                ax.set_title(f"Expenses - {today.strftime('%B %Y')}")
            else:
                ax.text(0.5, 0.5, "No data yet", ha='center', va='center')
            
            self.canvas.draw()