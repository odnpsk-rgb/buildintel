"""
Pydantic схемы для API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# === Запросы ===

class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""
    text: str = Field(..., min_length=10, description="Текст для анализа")


class ParseDemoRequest(BaseModel):
    """Запрос на парсинг URL"""
    url: str = Field(..., description="URL для парсинга")


# === Ответы ===

class CompetitorAnalysis(BaseModel):
    """Структурированный анализ продающего текста в строительстве"""
    strengths: List[str] = Field(default_factory=list, description="Сильные стороны продающего текста")
    weaknesses: List[str] = Field(default_factory=list, description="Слабые стороны продающего текста")
    unique_offers: List[str] = Field(default_factory=list, description="Уникальные предложения и УТП в тексте")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации по улучшению продающего текста")
    summary: str = Field("", description="Общее резюме анализа текста с точки зрения маркетинга в строительстве")


class ImageAnalysis(BaseModel):
    """Анализ планировки квартиры"""
    description: str = Field("", description="Описание планировки (комнаты, площадь, расположение)")
    marketing_insights: List[str] = Field(default_factory=list, description="Анализ удобства планировки (комнаты, санузлы, лифты, дополнительные помещения)")
    visual_style_score: int = Field(0, ge=0, le=10, description="Общая оценка удобства планировки (0-10)")
    visual_style_analysis: str = Field("", description="Анализ удобства планировки с учетом всех факторов")
    recommendations: List[str] = Field(default_factory=list, description="Сильные и слабые стороны, рекомендации по улучшению")


class ParsedContent(BaseModel):
    """Результат парсинга страницы"""
    url: str
    title: Optional[str] = None
    h1: Optional[str] = None
    first_paragraph: Optional[str] = None
    screenshot_base64: Optional[str] = None  # Base64 скриншота страницы
    full_text: Optional[str] = None  # Весь видимый текст страницы
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class TextAnalysisResponse(BaseModel):
    """Ответ на анализ текста"""
    success: bool
    analysis: Optional[CompetitorAnalysis] = None
    error: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    """Ответ на анализ изображения"""
    success: bool
    analysis: Optional[ImageAnalysis] = None
    error: Optional[str] = None


class ParseDemoResponse(BaseModel):
    """Ответ на парсинг"""
    success: bool
    data: Optional[ParsedContent] = None
    error: Optional[str] = None


# === История ===

class HistoryItem(BaseModel):
    """Элемент истории"""
    id: str
    timestamp: datetime
    request_type: str  # "text", "image", "parse"
    request_summary: str
    response_summary: str


class HistoryResponse(BaseModel):
    """Ответ со списком истории"""
    items: List[HistoryItem]
    total: int
