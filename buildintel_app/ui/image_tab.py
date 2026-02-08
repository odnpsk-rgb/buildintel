"""
Вкладка анализа изображений (планировок)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path


class AnalyzeImageThread(QThread):
    """Поток для анализа изображения"""
    finished = pyqtSignal(dict)
    
    def __init__(self, api_client, image_path):
        super().__init__()
        self.api_client = api_client
        self.image_path = image_path
        
    def run(self):
        result = self.api_client.analyze_image(self.image_path)
        self.finished.emit(result)


class ImageAnalysisTab(QWidget):
    """Вкладка анализа планировок"""
    
    def __init__(self, api_client, save_history_callback):
        super().__init__()
        self.api_client = api_client
        self.save_history = save_history_callback
        self.selected_image_path = None
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Анализ планировок квартир")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #f1f5f9; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Загрузите изображение планировки квартиры для анализа удобства, расположения комнат, санузлов и лифтов")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Кнопка выбора файла
        self.select_btn = QPushButton("Выбрать планировку")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a2234;
                color: #f1f5f9;
                border: 2px dashed #1e293b;
                border-radius: 8px;
                padding: 40px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                border-color: #06b6d4;
                background-color: #243049;
            }
        """)
        self.select_btn.clicked.connect(self.select_image)
        layout.addWidget(self.select_btn)
        
        # Превью изображения
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #0d1320;
                min-height: 200px;
            }
        """)
        self.preview_label.hide()
        layout.addWidget(self.preview_label)
        
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
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
        """)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.analyze_image)
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
        
    def select_image(self):
        """Выбор изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите планировку",
            "",
            "Изображения (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Масштабирование для превью
                scaled_pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.show()
                self.analyze_btn.setEnabled(True)
                self.select_btn.setText(f"Выбрано: {Path(file_path).name}")
                
    def analyze_image(self):
        """Анализ изображения"""
        if not self.selected_image_path:
            QMessageBox.warning(self, "Ошибка", "Выберите планировку квартиры для анализа")
            return
            
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Анализирую...")
        
        # Запуск анализа в отдельном потоке
        self.thread = AnalyzeImageThread(self.api_client, self.selected_image_path)
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
            summary = analysis.get("description", "Анализ планировки выполнен")
            self.save_history("image", Path(self.selected_image_path).name, summary)
        else:
            error = result.get("error", "Неизвестная ошибка")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {error}")
            
    def display_results(self, analysis):
        """Отображение результатов"""
        # Очистка предыдущих результатов
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
            
        # Описание планировки
        if analysis.get("description"):
            desc_frame = QFrame()
            desc_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a2234;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                }
            """)
            desc_layout = QVBoxLayout(desc_frame)
            
            desc_title = QLabel("Описание планировки")
            desc_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #06b6d4; margin-bottom: 8px;")
            desc_layout.addWidget(desc_title)
            
            desc_text = QLabel(analysis["description"])
            desc_text.setWordWrap(True)
            desc_text.setStyleSheet("color: #94a3b8; line-height: 1.6;")
            desc_layout.addWidget(desc_text)
            
            self.results_layout.addWidget(desc_frame)
            
        # Оценка удобства
        if "visual_style_score" in analysis:
            score_frame = QFrame()
            score_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a2234;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                }
            """)
            score_layout = QVBoxLayout(score_frame)
            
            score_title = QLabel("Общая оценка удобства планировки")
            score_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #06b6d4; margin-bottom: 8px;")
            score_layout.addWidget(score_title)
            
            score_value = QLabel(f"{analysis['visual_style_score']}/10")
            score_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #f1f5f9; margin-bottom: 8px;")
            score_layout.addWidget(score_value)
            
            if analysis.get("visual_style_analysis"):
                score_text = QLabel(analysis["visual_style_analysis"])
                score_text.setWordWrap(True)
                score_text.setStyleSheet("color: #94a3b8; line-height: 1.6;")
                score_layout.addWidget(score_text)
                
            self.results_layout.addWidget(score_frame)
            
        # Анализ удобства планировки
        if analysis.get("marketing_insights"):
            self.add_result_section("Анализ удобства планировки", analysis["marketing_insights"], "#06b6d4")
            
        # Рекомендации
        if analysis.get("recommendations"):
            self.add_result_section("Сильные и слабые стороны, рекомендации", analysis["recommendations"], "#f59e0b")
            
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
