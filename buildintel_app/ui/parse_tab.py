"""
Вкладка парсинга сайтов
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal


class ParseUrlThread(QThread):
    """Поток для парсинга URL"""
    finished = pyqtSignal(dict)
    
    def __init__(self, api_client, url):
        super().__init__()
        self.api_client = api_client
        self.url = url
        
    def run(self):
        result = self.api_client.parse_url(self.url)
        self.finished.emit(result)


class ParseTab(QWidget):
    """Вкладка парсинга сайтов"""
    
    def __init__(self, api_client, save_history_callback):
        super().__init__()
        self.api_client = api_client
        self.save_history = save_history_callback
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Парсинг сайта конкурента")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #f1f5f9; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Введите URL сайта для автоматического извлечения и анализа контента")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Поле ввода URL
        url_layout = QVBoxLayout()
        url_label = QLabel("URL сайта:")
        url_label.setStyleSheet("color: #f1f5f9; margin-bottom: 8px;")
        url_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1320;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 12px;
                color: #f1f5f9;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #06b6d4;
            }
        """)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Кнопка парсинга
        self.parse_btn = QPushButton("Парсить и проанализировать")
        self.parse_btn.setStyleSheet("""
            QPushButton {
                background-color: #06b6d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0891b2;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
        """)
        self.parse_btn.clicked.connect(self.parse_url)
        layout.addWidget(self.parse_btn)
        
        # Область результатов
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #111827;
            }
        """)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_area.setWidget(self.results_widget)
        self.results_area.hide()
        layout.addWidget(self.results_area)
        
    def parse_url(self):
        """Парсинг URL"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL для парсинга")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
            
        self.parse_btn.setEnabled(False)
        self.parse_btn.setText("Парсю и анализирую...")
        
        # Запуск парсинга в отдельном потоке
        self.thread = ParseUrlThread(self.api_client, url)
        self.thread.finished.connect(self.on_parse_complete)
        self.thread.start()
        
    def on_parse_complete(self, result):
        """Обработка результата парсинга"""
        self.parse_btn.setEnabled(True)
        self.parse_btn.setText("Парсить и проанализировать")
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            self.display_results(data)
            
            # Сохранение в историю
            summary = data.get("title", data.get("url", "Парсинг выполнен"))
            self.save_history("parse", data.get("url", ""), summary)
        else:
            error = result.get("error", "Неизвестная ошибка")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при парсинге: {error}")
            
    def display_results(self, data):
        """Отображение результатов"""
        # Очистка предыдущих результатов
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
            
        # URL
        if data.get("url"):
            url_frame = QFrame()
            url_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a2234;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                }
            """)
            url_layout = QVBoxLayout(url_frame)
            
            url_label = QLabel(f"URL: {data['url']}")
            url_label.setWordWrap(True)
            url_label.setStyleSheet("color: #06b6d4; font-size: 14px;")
            url_layout.addWidget(url_label)
            
            self.results_layout.addWidget(url_frame)
            
        # Извлеченные данные
        if data.get("title"):
            self.add_info_item("Заголовок", data["title"])
        if data.get("h1"):
            self.add_info_item("H1", data["h1"])
        if data.get("first_paragraph"):
            self.add_info_item("Первый абзац", data["first_paragraph"])
        if data.get("full_text"):
            text = data["full_text"]
            if len(text) > 500:
                text = text[:500] + "..."
            self.add_info_item("Текст страницы", text)
            
        # Скриншот
        if data.get("screenshot_base64"):
            screenshot_label = QLabel("Скриншот страницы:")
            screenshot_label.setStyleSheet("color: #f1f5f9; font-weight: bold; margin-top: 12px;")
            self.results_layout.addWidget(screenshot_label)
            
            # Здесь можно добавить отображение скриншота, если нужно
            
        # Анализ
        if data.get("analysis"):
            analysis = data["analysis"]
            if analysis.get("strengths"):
                self.add_result_section("Сильные стороны", analysis["strengths"], "#10b981")
            if analysis.get("weaknesses"):
                self.add_result_section("Слабые стороны", analysis["weaknesses"], "#ef4444")
            if analysis.get("unique_offers"):
                self.add_result_section("Уникальные предложения", analysis["unique_offers"], "#06b6d4")
            if analysis.get("recommendations"):
                self.add_result_section("Рекомендации", analysis["recommendations"], "#f59e0b")
            if analysis.get("summary"):
                self.add_info_item("Резюме", analysis["summary"])
                
        self.results_area.show()
        
    def add_info_item(self, label, value):
        """Добавление информационного элемента"""
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
        
        title = QLabel(label)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #06b6d4; margin-bottom: 8px;")
        layout.addWidget(title)
        
        text = QLabel(value)
        text.setWordWrap(True)
        text.setStyleSheet("color: #94a3b8; line-height: 1.6;")
        layout.addWidget(text)
        
        self.results_layout.addWidget(frame)
        
    def add_result_section(self, title, items, color):
        """Добавление секции результатов"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1a2234;
                border: 1px solid #1e293b;
                border-left: 3px solid {color};
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
            }}
        """)
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        for item in items:
            item_label = QLabel(f"• {item}")
            item_label.setWordWrap(True)
            item_label.setStyleSheet("color: #94a3b8; margin-left: 8px; margin-bottom: 4px;")
            layout.addWidget(item_label)
            
        self.results_layout.addWidget(frame)
