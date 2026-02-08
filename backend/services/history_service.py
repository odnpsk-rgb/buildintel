"""
Сервис для работы с историей запросов
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from backend.config import settings
from backend.models.schemas import HistoryItem


class HistoryService:
    """Управление историей запросов"""
    
    def __init__(self):
        self.history_file = Path(settings.history_file)
        self.max_items = settings.max_history_items
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создать файл истории если его нет"""
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")
    
    def _load_history(self) -> List[dict]:
        """Загрузить историю из файла"""
        try:
            content = self.history_file.read_text(encoding="utf-8")
            return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self, history: List[dict]):
        """Сохранить историю в файл"""
        self.history_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8"
        )
    
    def add_entry(
        self,
        request_type: str,
        request_summary: str,
        response_summary: str
    ) -> HistoryItem:
        """Добавить запись в историю"""
        history = self._load_history()
        
        item = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "request_type": request_type,
            "request_summary": request_summary[:200],  # Ограничиваем длину
            "response_summary": response_summary[:500]
        }
        
        # Добавляем в начало
        history.insert(0, item)
        
        # Оставляем только последние N записей
        history = history[:self.max_items]
        
        self._save_history(history)
        
        return HistoryItem(**item)
    
    def get_history(self) -> List[HistoryItem]:
        """Получить всю историю"""
        history = self._load_history()
        return [HistoryItem(**item) for item in history]
    
    def clear_history(self):
        """Очистить историю"""
        self._save_history([])


# Глобальный экземпляр
history_service = HistoryService()
