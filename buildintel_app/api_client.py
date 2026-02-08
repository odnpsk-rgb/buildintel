"""
Клиент для работы с API бэкенда
"""
import requests
import base64
from pathlib import Path
from typing import Optional, Dict, Any


class APIClient:
    """Клиент для взаимодействия с FastAPI бэкендом"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста"""
        try:
            response = requests.post(
                f"{self.base_url}/analyze_text",
                json={"text": text},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка запроса: {str(e)}"
            }
            
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Анализ изображения"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, 'image/jpeg')}
                response = requests.post(
                    f"{self.base_url}/analyze_image",
                    files=files,
                    timeout=120
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка запроса: {str(e)}"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Файл не найден"
            }
            
    def parse_url(self, url: str) -> Dict[str, Any]:
        """Парсинг URL"""
        try:
            response = requests.post(
                f"{self.base_url}/parse_demo",
                json={"url": url},
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка запроса: {str(e)}"
            }
            
    def get_history(self) -> Dict[str, Any]:
        """Получение истории"""
        try:
            response = requests.get(f"{self.base_url}/history", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "items": [],
                "total": 0
            }
