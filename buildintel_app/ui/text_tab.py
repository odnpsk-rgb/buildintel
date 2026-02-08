"""
Вкладка анализа текста
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel,
    QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal


class AnalyzeTextThread(QThread):
    """Поток для анализа текста"""
    finished = pyqtSignal(dict)
    
    def __init__(self, api_client, text):
        super().__init__()
        self.api_client = api_client
        self.text = text
        
    def run(self):
        result = self.api_client.analyze_text(self.text)
        self.finished.emit(result)


class TextAnalysisTab(QWidget):
    """Вкладка анализа текста"""
    
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
        title = QLabel("Анализ продающего текста")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #f1f5f9; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Введите продающий текст конкурента в строительстве для маркетингового анализа")
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Поле ввода текста
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Вставьте продающий текст конкурента в строительстве...\n\nНапример: описание жилого комплекса, текст с лендинга застройщика, рекламное объявление о квартирах...")
        self.text_input.setMinimumHeight(200)
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #0d1320;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 12px;
                color: #f1f5f9;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #06b6d4;
            }
        """)
        layout.addWidget(self.text_input)
        
        # Кнопка анализа
        self.analyze_btn = QPushButton("Проанализировать")
        self.analyze_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #0e7490;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_text)
        layout.addWidget(self.analyze_btn)
        
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
        
    def analyze_text(self):
        """Анализ текста"""
        text = self.text_input.toPlainText().strip()
        
        if len(text) < 10:
            QMessageBox.warning(self, "Ошибка", "Введите продающий текст минимум 10 символов для анализа")
            return
            
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Анализирую...")
        
        # Запуск анализа в отдельном потоке
        self.thread = AnalyzeTextThread(self.api_client, text)
        self.thread.finished.connect(self.on_analysis_complete)
        self.thread.start()
        
    def on_analysis_complete(self, result):
        """Обработка результата анализа"""
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Проанализировать")
        
        if result.get("success") and result.get("analysis"):
            analysis = result["analysis"]
            self.display_results(analysis)
            
            # Сохранение в историю
            summary = analysis.get("summary", "Анализ текста выполнен")
            self.save_history("text", self.text_input.toPlainText()[:100], summary)
        else:
            error = result.get("error", "Неизвестная ошибка")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {error}")
            
    def display_results(self, analysis):
        """Отображение результатов"""
        # Очистка предыдущих результатов
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
            
        # Сильные стороны
        if analysis.get("strengths"):
            self.add_result_section("Сильные стороны", analysis["strengths"], "#10b981")
            
        # Слабые стороны
        if analysis.get("weaknesses"):
            self.add_result_section("Слабые стороны", analysis["weaknesses"], "#ef4444")
            
        # Уникальные предложения
        if analysis.get("unique_offers"):
            self.add_result_section("Уникальные предложения", analysis["unique_offers"], "#06b6d4")
            
        # Рекомендации
        if analysis.get("recommendations"):
            self.add_result_section("Рекомендации", analysis["recommendations"], "#f59e0b")
            
        # Резюме
        if analysis.get("summary"):
            summary_frame = QFrame()
            summary_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a2234;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 16px;
                    margin-top: 10px;
                }
            """)
            summary_layout = QVBoxLayout(summary_frame)
            
            summary_title = QLabel("Резюме")
            summary_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1f5f9; margin-bottom: 8px;")
            summary_layout.addWidget(summary_title)
            
            summary_text = QLabel(analysis["summary"])
            summary_text.setWordWrap(True)
            summary_text.setStyleSheet("color: #94a3b8; line-height: 1.6;")
            summary_layout.addWidget(summary_text)
            
            self.results_layout.addWidget(summary_frame)
            
        self.results_area.show()
        
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
