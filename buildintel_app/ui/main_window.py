"""
Главное окно приложения
"""
import json
import base64
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QLabel, QFileDialog, QLineEdit,
    QScrollArea, QFrame, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette

import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import APIClient
from ui.text_tab import TextAnalysisTab
from ui.image_tab import ImageAnalysisTab
from ui.parse_tab import ParseTab
from ui.history_tab import HistoryTab


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.history_file = Path("history.json")
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("BuildIntel | AI Ассистент в сфере строительства")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Заголовок
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: #1a2234;
                border-bottom: 1px solid #1e293b;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 20, 40, 20)
        
        title = QLabel("BuildIntel")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #f1f5f9;
            }
        """)
        subtitle = QLabel("AI-ассистент в сфере строительства")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #94a3b8;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #111827;
            }
            QTabBar::tab {
                background-color: #1a2234;
                color: #94a3b8;
                padding: 12px 24px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #06b6d4;
                border-bottom: 2px solid #06b6d4;
                background-color: #111827;
            }
            QTabBar::tab:hover {
                background-color: #243049;
            }
        """)
        
        # Создание вкладок
        self.text_tab = TextAnalysisTab(self.api_client, self.save_history)
        self.image_tab = ImageAnalysisTab(self.api_client, self.save_history)
        self.parse_tab = ParseTab(self.api_client, self.save_history)
        self.history_tab = HistoryTab(self.load_history)
        
        self.tabs.addTab(self.text_tab, "Анализ текста")
        self.tabs.addTab(self.image_tab, "Планировки")
        self.tabs.addTab(self.parse_tab, "Парсинг сайта")
        self.tabs.addTab(self.history_tab, "История")
        
        main_layout.addWidget(self.tabs)
        
        # Статус бар
        self.statusBar().showMessage("Готово")
        
        # Применение темной темы
        self.apply_dark_theme()
        
    def apply_dark_theme(self):
        """Применение темной темы"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(17, 24, 39))
        palette.setColor(QPalette.WindowText, QColor(241, 245, 249))
        palette.setColor(QPalette.Base, QColor(26, 34, 52))
        palette.setColor(QPalette.AlternateBase, QColor(17, 24, 39))
        palette.setColor(QPalette.ToolTipBase, QColor(241, 245, 249))
        palette.setColor(QPalette.ToolTipText, QColor(241, 245, 249))
        palette.setColor(QPalette.Text, QColor(241, 245, 249))
        palette.setColor(QPalette.Button, QColor(26, 34, 52))
        palette.setColor(QPalette.ButtonText, QColor(241, 245, 249))
        palette.setColor(QPalette.BrightText, QColor(6, 182, 212))
        palette.setColor(QPalette.Link, QColor(6, 182, 212))
        palette.setColor(QPalette.Highlight, QColor(6, 182, 212))
        palette.setColor(QPalette.HighlightedText, QColor(17, 24, 39))
        self.setPalette(palette)
        
    def save_history(self, request_type, request_summary, response_summary):
        """Сохранение в историю"""
        history = self.load_history()
        
        import datetime
        item = {
            "id": str(len(history) + 1),
            "timestamp": datetime.datetime.now().isoformat(),
            "request_type": request_type,
            "request_summary": request_summary[:100] + "..." if len(request_summary) > 100 else request_summary,
            "response_summary": response_summary[:100] + "..." if len(response_summary) > 100 else response_summary
        }
        
        history.append(item)
        # Оставляем только последние 10
        history = history[-10:]
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")
            
        # Обновляем вкладку истории
        if hasattr(self, 'history_tab'):
            self.history_tab.refresh_history()
            
    def load_history(self):
        """Загрузка истории"""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []
