"""
Главный модуль FastAPI приложения
BuildIntel - AI ассистент для анализа маркетинга в строительстве
"""
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from openai import APIError

from backend.config import settings
from backend.models.schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    ImageAnalysisResponse,
    ParseDemoRequest,
    ParseDemoResponse,
    ParsedContent,
    HistoryResponse,
    CompetitorAnalysis
)
from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service


# Инициализация приложения
app = FastAPI(
    title="BuildIntel",
    description="AI ассистент для анализа маркетинга в строительстве: анализ продающих текстов и планировок квартир",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Эндпоинты ===

@app.get("/")
async def root():
    """Главная страница - отдаём фронтенд"""
    return FileResponse("frontend/index.html")


@app.post("/analyze_text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Анализ продающего текста в строительстве
    
    Принимает продающий текст конкурента в строительной сфере и возвращает структурированный анализ с точки зрения маркетинга:
    - Сильные стороны текста (эффективность формулировок, использование триггеров, социальное доказательство)
    - Слабые стороны текста (что можно улучшить для повышения конверсии)
    - Уникальные предложения и УТП (выделенные преимущества, конкурентные отличия)
    - Рекомендации по улучшению продающего текста (конкретные советы для строительного маркетинга)
    - Резюме маркетинговой эффективности текста
    """
    try:
        if not request.text or not isinstance(request.text, str) or not request.text.strip():
            return TextAnalysisResponse(
                success=False,
                error="Текст для анализа не может быть пустым"
            )
        analysis = await openai_service.analyze_text(request.text)
        
        # Сохраняем в историю
        history_service.add_entry(
            request_type="text",
            request_summary=request.text[:100] + "..." if len(request.text) > 100 else request.text,
            response_summary=analysis.summary
        )
        
        return TextAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except APIError as e:
        # Специальная обработка ошибок OpenAI API
        error_message = str(e)
        if "unsupported_country_region_territory" in error_message or "403" in str(e.status_code):
            error_message = "OpenAI API недоступен в вашем регионе. Используйте VPN или прокси для доступа к API."
        elif "401" in str(e.status_code) or "invalid_api_key" in error_message.lower():
            error_message = "Неверный API ключ OpenAI. Проверьте файл .env"
        elif "429" in str(e.status_code) or "rate_limit" in error_message.lower():
            error_message = "Превышен лимит запросов к OpenAI API. Попробуйте позже."
        return TextAnalysisResponse(
            success=False,
            error=error_message
        )
    except Exception as e:
        return TextAnalysisResponse(
            success=False,
            error=f"Ошибка при анализе: {str(e)}"
        )


@app.post("/analyze_image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Анализ планировки квартиры
    
    Принимает изображение планировки квартиры и возвращает:
    - Описание планировки
    - Анализ удобства планировки (комнаты, санузлы, лифты)
    - Общую оценку удобства планировки (0-10)
    - Сильные и слабые стороны
    - Рекомендации по улучшению
    """
    # Проверяем тип файла
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
        )
    
    try:
        # Читаем и кодируем изображение
        content = await file.read()
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        # Анализируем
        analysis = await openai_service.analyze_image(
            image_base64=image_base64,
            mime_type=file.content_type
        )
        
        # Сохраняем в историю
        history_service.add_entry(
            request_type="image",
            request_summary=f"Изображение: {file.filename}",
            response_summary=analysis.description[:200] if analysis.description else "Анализ изображения"
        )
        
        return ImageAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except APIError as e:
        # Специальная обработка ошибок OpenAI API
        error_message = str(e)
        if "unsupported_country_region_territory" in error_message or "403" in str(e.status_code):
            error_message = "OpenAI API недоступен в вашем регионе. Используйте VPN или прокси для доступа к API."
        elif "401" in str(e.status_code) or "invalid_api_key" in error_message.lower():
            error_message = "Неверный API ключ OpenAI. Проверьте файл .env"
        elif "429" in str(e.status_code) or "rate_limit" in error_message.lower():
            error_message = "Превышен лимит запросов к OpenAI API. Попробуйте позже."
        return ImageAnalysisResponse(
            success=False,
            error=error_message
        )
    except Exception as e:
        return ImageAnalysisResponse(
            success=False,
            error=f"Ошибка при анализе изображения: {str(e)}"
        )


@app.post("/parse_demo", response_model=ParseDemoResponse)
async def parse_demo(request: ParseDemoRequest):
    """
    Парсинг и анализ сайта конкурента через Selenium
    
    Принимает URL, открывает в Chrome через Selenium:
    - Делает скриншот страницы
    - Извлекает title, h1, первый абзац и весь видимый текст
    - Передаёт скриншот и текст модели для анализа
    """
    try:
        # Проверяем URL
        if not request.url or not isinstance(request.url, str) or not request.url.strip():
            return ParseDemoResponse(
                success=False,
                error="URL не может быть пустым"
            )
        
        # Парсим страницу через Selenium
        title, h1, first_paragraph, screenshot_base64, full_text, error = await parser_service.parse_url(request.url.strip())
        
        if error:
            return ParseDemoResponse(
                success=False,
                error=error
            )
        
        # Анализируем контент
        analysis = None
        
        # Если есть скриншот, анализируем его как изображение
        if screenshot_base64:
            try:
                image_analysis = await openai_service.analyze_image(
                    image_base64=screenshot_base64,
                    mime_type="image/png"
                )
                # Конвертируем ImageAnalysis в CompetitorAnalysis для единообразия
                analysis = CompetitorAnalysis(
                    strengths=image_analysis.marketing_insights,
                    weaknesses=[],
                    unique_offers=[],
                    recommendations=image_analysis.recommendations,
                    summary=f"Визуальный анализ страницы. Оценка стиля: {image_analysis.visual_style_score}/10. {image_analysis.description}"
                )
            except Exception as e:
                print(f"Ошибка при анализе скриншота: {e}")
        
        # Если нет скриншота или анализ изображения не удался, анализируем текст
        if not analysis:
            # Используем весь текст или комбинируем с title/h1/paragraph
            text_to_analyze = None
            if full_text and full_text.strip():
                text_to_analyze = full_text
            elif title or h1 or first_paragraph:
                text_to_analyze = f"{title or ''}\n{h1 or ''}\n{first_paragraph or ''}".strip()
            
            if text_to_analyze:
                analysis = await openai_service.analyze_parsed_content(
                    title=title,
                    h1=h1,
                    paragraph=text_to_analyze
                )
            else:
                # Если нет контента для анализа
                analysis = CompetitorAnalysis(
                    summary="Не удалось извлечь контент для анализа"
                )
        
        parsed_content = ParsedContent(
            url=request.url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
            screenshot_base64=screenshot_base64,
            full_text=full_text[:1000] if (full_text and isinstance(full_text, str)) else None,  # Ограничиваем для JSON
            analysis=analysis
        )
        
        # Сохраняем в историю
        try:
            history_service.add_entry(
                request_type="parse",
                request_summary=f"URL: {request.url or 'N/A'}",
                response_summary=f"Title: {title or 'N/A'}" if title else "N/A"
            )
        except Exception as e:
            print(f"Ошибка при сохранении в историю: {e}")
        
        return ParseDemoResponse(
            success=True,
            data=parsed_content
        )
    except APIError as e:
        # Специальная обработка ошибок OpenAI API
        error_message = str(e)
        if "unsupported_country_region_territory" in error_message or "403" in str(e.status_code):
            error_message = "OpenAI API недоступен в вашем регионе. Используйте VPN или прокси для доступа к API."
        elif "401" in str(e.status_code) or "invalid_api_key" in error_message.lower():
            error_message = "Неверный API ключ OpenAI. Проверьте файл .env"
        elif "429" in str(e.status_code) or "rate_limit" in error_message.lower():
            error_message = "Превышен лимит запросов к OpenAI API. Попробуйте позже."
        return ParseDemoResponse(
            success=False,
            error=error_message
        )
    except Exception as e:
        return ParseDemoResponse(
            success=False,
            error=f"Ошибка при парсинге: {str(e)}"
        )


@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """
    Получить историю последних 10 запросов
    """
    items = history_service.get_history()
    return HistoryResponse(
        items=items,
        total=len(items)
    )


@app.delete("/history")
async def clear_history():
    """
    Очистить историю запросов
    """
    history_service.clear_history()
    return {"success": True, "message": "История очищена"}


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "BuildIntel",
        "version": "1.0.0"
    }


# Статические файлы для фронтенда
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
