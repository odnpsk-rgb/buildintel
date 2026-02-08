"""
Сервис для работы с OpenAI API
"""
import base64
import json
import re
from typing import Optional

from openai import OpenAI

from backend.config import settings
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis


class OpenAIService:
    """Сервис для анализа через OpenAI"""
    
    def __init__(self):
        # Настройка прокси, если указан
        client_kwargs = {"api_key": settings.openai_api_key}
        
        # Добавляем прокси, если указан
        if settings.https_proxy or settings.http_proxy:
            proxy = settings.https_proxy or settings.http_proxy
            try:
                import httpx
                client_kwargs["http_client"] = httpx.Client(
                    proxies=proxy,
                    timeout=30.0
                )
            except ImportError:
                # httpx уже должен быть установлен через requirements.txt
                pass
        
        self.client = OpenAI(**client_kwargs)
        self.model = settings.openai_model
        self.vision_model = settings.openai_vision_model
    
    def _parse_json_response(self, content: str) -> dict:
        """Извлечь JSON из ответа модели"""
        if not content or not isinstance(content, str):
            return {}
        
        # Пробуем найти JSON в markdown блоке
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        
        # Пробуем найти JSON объект
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}
    
    async def analyze_text(self, text: str) -> CompetitorAnalysis:
        """Анализ продающего текста в строительстве"""
        system_prompt = """Ты — эксперт по маркетингу в строительстве и недвижимости. Проанализируй предоставленный продающий текст конкурента в строительной сфере и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона текста 1", "сильная сторона текста 2", ...],
    "weaknesses": ["слабая сторона текста 1", "слабая сторона текста 2", ...],
    "unique_offers": ["уникальное предложение/УТП 1", "уникальное предложение/УТП 2", ...],
    "recommendations": ["рекомендация по улучшению текста 1", "рекомендация по улучшению текста 2", ...],
    "summary": "Краткое резюме анализа продающего текста с точки зрения маркетинга в строительстве"
}

Важно:
- Каждый массив должен содержать 3-5 пунктов
- Пиши на русском языке
- Будь конкретен и практичен в рекомендациях
- Оценивай текст с точки зрения маркетинга в строительстве:
  * Эффективности продающих формулировок и убедительности
  * Использования триггеров покупки (выгоды, преимущества, эмоции, срочность)
  * Презентации уникальных торговых предложений (УТП) и конкурентных преимуществ
  * Работы с возражениями клиентов (цена, сроки, качество, гарантии)
  * Использования социального доказательства (отзывы, кейсы, гарантии, сертификаты, опыт работы)
  * Структуры текста и призыва к действию (CTA) - насколько четко и убедительно
  * Использования конкретики (площади, цены, сроки, материалы, технологии, локация)
  * Эмоционального воздействия на целевую аудиторию (доверие, безопасность, комфорт, престиж)
  * Описания выгод для клиента (комфорт, безопасность, инвестиционная привлекательность, экология)
  * Использования строительной терминологии и профессиональных терминов
- Фокусируйся на специфике строительного маркетинга: доверие, надежность, качество материалов, сроки сдачи, гарантии, технологии строительства, локация, инфраструктура, экологичность"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Проанализируй этот продающий текст конкурента в строительстве с точки зрения маркетинга:\n\n{text}"}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Пустой ответ от OpenAI API")
        
        data = self._parse_json_response(content)
        
        return CompetitorAnalysis(
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            unique_offers=data.get("unique_offers", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", "")
        )
    
    async def analyze_image(self, image_base64: str, mime_type: str = "image/jpeg") -> ImageAnalysis:
        """Анализ планировки квартиры"""
        system_prompt = """Ты — эксперт по анализу планировок квартир и недвижимости. Проанализируй планировку квартиры на изображении и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "description": "Детальное описание планировки: количество комнат, общая площадь, расположение помещений, особенности планировки",
    "marketing_insights": [
        "Удобство планировки: [анализ удобства расположения комнат, проходных зон, изолированности]",
        "Лифты: [анализ удобства расположения лифтов, их количество, доступность]",
        "Санузлы: [анализ удобства расположения санузлов, их количество, доступность из разных зон]",
        "Комнаты: [анализ удобства комнат - размеры, форма, освещенность, расположение]",
        "Дополнительные помещения: [балконы, лоджии, кладовые, гардеробные и т.д.]"
    ],
    "visual_style_score": 7,
    "visual_style_analysis": "Общая оценка удобства планировки с учетом всех факторов: функциональность, комфорт, практичность использования пространства",
    "recommendations": [
        "Сильные стороны планировки: [что хорошо в этой планировке]",
        "Слабые стороны планировки: [что можно улучшить]",
        "Рекомендации по улучшению: [конкретные предложения]"
    ]
}

Важно:
- visual_style_score от 0 до 10 (общая оценка удобства планировки)
- Каждый массив marketing_insights должен содержать 4-6 пунктов с детальным анализом
- Каждый массив recommendations должен содержать 3-5 пунктов
- Пиши на русском языке
- Будь конкретен в анализе: указывай размеры, расположение, функциональность
- Оценивай: удобство использования пространства, логику расположения помещений, изолированность комнат, доступность санузлов, удобство лифтов"""

        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Проанализируй эту планировку квартиры. Оцени удобство планировки, расположение комнат, санузлов, лифтов. Опиши сильные и слабые стороны планировки."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Пустой ответ от OpenAI API")
        
        data = self._parse_json_response(content)
        
        return ImageAnalysis(
            description=data.get("description", ""),
            marketing_insights=data.get("marketing_insights", []),
            visual_style_score=data.get("visual_style_score", 5),
            visual_style_analysis=data.get("visual_style_analysis", ""),
            recommendations=data.get("recommendations", [])
        )
    
    async def analyze_parsed_content(
        self, 
        title: Optional[str], 
        h1: Optional[str], 
        paragraph: Optional[str]
    ) -> CompetitorAnalysis:
        """Анализ распарсенного контента сайта"""
        content_parts = []
        if title and isinstance(title, str) and title.strip():
            content_parts.append(f"Заголовок страницы (title): {title.strip()}")
        if h1 and isinstance(h1, str) and h1.strip():
            content_parts.append(f"Главный заголовок (H1): {h1.strip()}")
        if paragraph and isinstance(paragraph, str) and paragraph.strip():
            content_parts.append(f"Первый абзац: {paragraph.strip()}")
        
        if not content_parts:
            return CompetitorAnalysis(
                summary="Не удалось извлечь контент для анализа"
            )
        
        combined_text = "\n\n".join(content_parts)
        
        if not combined_text or not combined_text.strip():
            return CompetitorAnalysis(
                summary="Не удалось извлечь контент для анализа"
            )
        
        return await self.analyze_text(combined_text)


# Глобальный экземпляр
openai_service = OpenAIService()
