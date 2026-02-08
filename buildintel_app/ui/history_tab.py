"""
Вкладка истории запросов
"""
import json
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt


class HistoryTab(QWidget):
    """Вкладка истории"""
    
    def __init__(self, load_history_callback):
        super().__init__()
        self.load_history = load_history_callback
        self.history_file = Path("history.json")
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Заголовок
        header_layout = QVBoxLayout()
        
        title = QLabel("История запросов")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #f1f5f9; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Последние 10 запросов")
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        header_layout.addWidget(subtitle)
        
        # Кнопка очистки
        clear_btn = QPushButton("Очистить историю")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Область истории
        self.history_area = QScrollArea()
        self.history_area.setWidgetResizable(True)
        self.history_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #111827;
            }
        """)
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setContentsMargins(20, 20, 20, 20)
        self.history_area.setWidget(self.history_widget)
        layout.addWidget(self.history_area)
        
        self.refresh_history()
        
    def refresh_history(self):
        """Обновление истории"""
        history = self.load_history()
        
        # Очистка предыдущих элементов
        for i in reversed(range(self.history_layout.count())):
            self.history_layout.itemAt(i).widget().setParent(None)
            
        if not history:
            no_history = QLabel("История пуста")
            no_history.setAlignment(Qt.AlignCenter)
            no_history.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px;")
            self.history_layout.addWidget(no_history)
        else:
            for item in reversed(history):  # Показываем последние первыми
                self.add_history_item(item)
                
    def add_history_item(self, item):
        """Добавление элемента истории"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1a2234;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Заголовок с типом и временем
        header_layout = QHBoxLayout()
        
        type_label = QLabel(self.get_type_label(item.get("request_type", "unknown")))
        type_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #06b6d4;")
        header_layout.addWidget(type_label)
        
        header_layout.addStretch()
        
        if item.get("timestamp"):
            try:
                dt = datetime.fromisoformat(item["timestamp"])
                time_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                time_str = item["timestamp"]
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: #64748b; font-size: 12px;")
            header_layout.addWidget(time_label)
            
        layout.addLayout(header_layout)
        
        # Запрос
        if item.get("request_summary"):
            request_label = QLabel(f"Запрос: {item['request_summary']}")
            request_label.setWordWrap(True)
            request_label.setStyleSheet("color: #94a3b8; margin-top: 8px; margin-bottom: 4px;")
            layout.addWidget(request_label)
            
        # Ответ
        if item.get("response_summary"):
            response_label = QLabel(f"Ответ: {item['response_summary']}")
            response_label.setWordWrap(True)
            response_label.setStyleSheet("color: #94a3b8; margin-top: 4px;")
            layout.addWidget(response_label)
            
        self.history_layout.addWidget(frame)
        
    def get_type_label(self, request_type):
        """Получение метки типа запроса"""
        types = {
            "text": "Анализ текста",
            "image": "Анализ планировки",
            "parse": "Парсинг сайта"
        }
        return types.get(request_type, "Неизвестно")
        
    def clear_history(self):
        """Очистка истории"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите очистить историю?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self.refresh_history()
                QMessageBox.information(self, "Успех", "История очищена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при очистке истории: {e}")
