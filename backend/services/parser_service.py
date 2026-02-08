"""
Сервис для парсинга веб-страниц через Selenium
"""
import base64
import asyncio
import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
from PIL import Image

from backend.config import settings

# Подавление лишних логов Selenium и браузера
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote.webdriver').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.selenium_manager').setLevel(logging.ERROR)

# Подавление логов WDM (webdriver-manager)
logging.getLogger('WDM').setLevel(logging.ERROR)


class ParserService:
    """Парсинг веб-страниц через Selenium Chrome"""
    
    def __init__(self):
        self.timeout = settings.parser_timeout or 30
        self.user_agent = settings.parser_user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.yandex_browser_path = getattr(settings, 'yandex_browser_path', None) or ""
        
    def _get_driver(self) -> webdriver.Chrome:
        """Создает и настраивает Chrome/Яндекс браузер драйвер"""
        import os
        import platform
        
        # Определяем корень проекта СНАЧАЛА
        # __file__ = backend/services/parser_service.py
        # parent = backend/services
        # parent.parent = backend
        # parent.parent.parent = корень проекта (monitor_kp)
        project_root = Path(__file__).parent.parent.parent.resolve()  # Корень проекта (абсолютный путь)
        print(f"🔍 Корень проекта: {project_root}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Запуск без GUI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.user_agent}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Подавление ошибок и предупреждений в логах
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')  # Только критические ошибки
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--enable-automation')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--use-mock-keychain')
        
        # Подавление ошибок GPU и WebGL
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--ignore-gpu-blacklist')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Подавление логов DevTools и других сервисов браузера
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Определяем путь к браузеру (приоритет: Chrome из проекта > Яндекс браузер > системный Chrome)
        yandex_binary = None
        chrome_binary = None
        system = platform.system()
        
        # ПРИОРИТЕТ 1: Сначала проверяем Chrome в папке проекта (chrome-win64)
        # Это важно, так как версия ChromeDriver должна совпадать с версией браузера
        chrome_in_project = project_root / "chrome-win64" / "chrome.exe"
        
        # Также проверяем альтернативные пути
        chrome_paths_to_check = [
            project_root / "chrome-win64" / "chrome.exe",
            project_root / "chrome" / "chrome.exe",
            project_root.parent / "chrome-win64" / "chrome.exe",  # На уровень выше
        ]
        
        chrome_binary = None
        for chrome_path in chrome_paths_to_check:
            if chrome_path.exists():
                chrome_binary = str(chrome_path.absolute())
                print(f"✅ Найден Chrome в проекте (версия 131, совместим с ChromeDriver): {chrome_binary}")
                chrome_options.binary_location = chrome_binary
                break
        
        if not chrome_binary:
            print(f"⚠️ Chrome в папке проекта не найден. Проверенные пути:")
            for path in chrome_paths_to_check:
                print(f"   - {path} (существует: {path.exists()})")
        
        # ПРИОРИТЕТ 2: Если Chrome в проекте не найден, ищем Яндекс браузер
        # ВАЖНО: Яндекс браузер версии 142 не совместим с ChromeDriver 131!
        # РЕКОМЕНДАЦИЯ: Используйте Chrome из папки chrome-win64 для совместимости
        if not chrome_binary:
            yandex_paths = []
            if system == "Windows":
                yandex_paths = [
                    os.path.expanduser(r"~\AppData\Local\Yandex\YandexBrowser\Application\browser.exe"),
                    r"C:\Users\{}\AppData\Local\Yandex\YandexBrowser\Application\browser.exe".format(os.getenv("USERNAME", "")),
                    r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
                    r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
                ]
            elif system == "Linux":
                yandex_paths = [
                    "/usr/bin/yandex-browser",
                    "/usr/bin/yandex-browser-beta",
                    "/opt/yandex/browser/yandex-browser",
                ]
            elif system == "Darwin":  # macOS
                yandex_paths = [
                    "/Applications/Yandex.app/Contents/MacOS/Yandex",
                ]
            
            # Сначала проверяем путь из настроек
            if self.yandex_browser_path and os.path.exists(self.yandex_browser_path):
                yandex_binary = self.yandex_browser_path
            else:
                # Ищем автоматически
                for path in yandex_paths:
                    if os.path.exists(path):
                        yandex_binary = path
                        break
            
            if yandex_binary:
                print(f"⚠️ Используется Яндекс браузер: {yandex_binary}")
                print("⚠️ ВНИМАНИЕ: Версия Яндекс браузера может не совпадать с ChromeDriver!")
                print("⚠️ Рекомендуется использовать Chrome из папки chrome-win64")
                chrome_options.binary_location = yandex_binary
            else:
                print("Используется системный Chrome")
        
        # Автоматическая установка ChromeDriver (совместим с Яндекс браузером)
        # Сначала проверяем локальный ChromeDriver в папке проекта
        service = None
        
        # Возможные пути к локальному ChromeDriver
        # Проверяем все возможные варианты, включая новую версию 144
        local_driver_paths = [
            project_root / "chromedriver.exe",  # Windows - корень проекта
            project_root / "chromedriver",  # Linux/Mac - корень проекта
            project_root / "drivers" / "chromedriver.exe",  # Папка drivers
            project_root / "drivers" / "chromedriver",  # Linux/Mac в drivers
            project_root / "chromedriver-win64" / "chromedriver.exe",  # Новая версия 144 (приоритет)
            project_root / "chrome-win64" / "chromedriver.exe",  # Папка chrome-win64
            project_root / "chrome-win64" / "chromedriver",  # Linux/Mac вариант
            project_root / "chromedriver-win32" / "chromedriver.exe",  # 32-bit версия
            project_root / "chromedriver_win64" / "chromedriver.exe",
            project_root / "chromedriver_win32" / "chromedriver.exe",
        ]
        
        local_driver = None
        for path in local_driver_paths:
            if path.exists() and path.is_file():
                local_driver = str(path.absolute())
                # Определяем версию ChromeDriver из пути
                version_info = ""
                if "chromedriver-win64" in str(path):
                    version_info = " (версия 144)"
                print(f"✅ Найден локальный ChromeDriver{version_info}: {local_driver}")
                break
        
        try:
            if local_driver:
                # Используем локальный ChromeDriver (версия 144)
                service = Service(local_driver)
                print(f"✅ Используется локальный ChromeDriver версии 144: {local_driver}")
                
                # Проверяем совместимость с браузером
                if yandex_binary:
                    print(f"✅ ChromeDriver 144 совместим с Яндекс браузером 142")
                elif chrome_binary:
                    print(f"✅ ChromeDriver 144 совместим с Chrome из проекта")
            else:
                # Если локального драйвера нет, пробуем установить через webdriver_manager
                if yandex_binary:
                    print("⚠️ Для Яндекс браузера нужен ChromeDriver версии 142+")
                    print("⚠️ Локальный ChromeDriver не найден, пробуем системный...")
                    try:
                        # Пробуем использовать системный драйвер (может быть установлен отдельно)
                        service = Service()  # Пустой сервис - Selenium найдет драйвер в PATH
                        print("Используется системный ChromeDriver из PATH")
                    except Exception as e1:
                        error_str = str(e1)
                        print(f"Ошибка: {error_str}")
                        # Если системный драйвер не найден, пробуем установить через webdriver_manager
                        try:
                            manager = ChromeDriverManager(version="latest")
                            driver_path = manager.install()
                            if driver_path:
                                service = Service(str(driver_path).strip())
                                print(f"ChromeDriver установлен: {service.path}")
                        except:
                            raise ValueError("Не удалось найти или установить совместимый ChromeDriver для Яндекс браузера")
                else:
                    # Для Chrome используем стандартный способ
                    try:
                        manager = ChromeDriverManager()
                        driver_path = manager.install()
                        if driver_path:
                            service = Service(str(driver_path).strip())
                            print(f"ChromeDriver установлен: {service.path}")
                    except Exception as e:
                        print(f"Ошибка при установке ChromeDriver: {e}")
                        print("Используем системный ChromeDriver...")
                        service = Service()
            
            # Создаем драйвер с подавлением логов
            # Настройка сервиса для подавления логов ChromeDriver
            if service:
                # Подавляем логи ChromeDriver (но не stderr браузера, так как это может вызвать проблемы)
                try:
                    # Пытаемся установить log_path, но это может не работать на всех версиях
                    if hasattr(service, 'log_path'):
                        service.log_path = os.devnull
                except:
                    pass  # Игнорируем, если не поддерживается
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Создаем сервис с подавлением логов
                service = Service()
                try:
                    if hasattr(service, 'log_path'):
                        service.log_path = os.devnull
                except:
                    pass
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при создании WebDriver: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            raise WebDriverException(f"Не удалось создать WebDriver: {str(e)}")
        
        return driver
    
    async def parse_url(self, url: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Парсит URL через Selenium, делает скриншот и извлекает контент
        
        Returns:
            Tuple[title, h1, first_paragraph, screenshot_base64, full_text, error]
        """
        # Проверяем и нормализуем URL
        if not url or not isinstance(url, str):
            return None, None, None, None, None, "Некорректный URL"
        
        url = url.strip()
        if not url:
            return None, None, None, None, None, "Пустой URL"
        
        # Добавляем протокол если его нет
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        driver = None
        try:
            # Запускаем браузер в отдельном потоке (Selenium не async)
            loop = asyncio.get_event_loop()
            
            # Создаем драйвер с обработкой ошибок
            try:
                driver = await loop.run_in_executor(None, self._get_driver)
            except Exception as e:
                import traceback
                error_msg = f"Ошибка при создании драйвера: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                return None, None, None, None, None, f"Ошибка при создании браузера: {str(e)}"
            
            if not driver:
                return None, None, None, None, None, "Не удалось создать драйвер браузера"
            
            # Открываем страницу
            try:
                await loop.run_in_executor(None, driver.get, url)
            except Exception as e:
                import traceback
                error_msg = f"Ошибка при открытии URL {url}: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                return None, None, None, None, None, f"Ошибка при открытии страницы: {str(e)}"
            
            # Ждем загрузки страницы
            wait = WebDriverWait(driver, self.timeout)
            try:
                # Ждем загрузки body
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                # Дополнительная задержка для загрузки динамического контента
                await asyncio.sleep(2)
            except TimeoutException:
                pass  # Продолжаем даже если таймаут
            
            # Получаем HTML после выполнения JavaScript
            # page_source - это свойство, а не метод, поэтому нужна обертка
            def get_page_source():
                return driver.page_source
            
            html = await loop.run_in_executor(None, get_page_source)
            soup = BeautifulSoup(html, 'lxml')
            
            # Извлекаем title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Извлекаем h1
            h1 = None
            h1_tag = soup.find('h1')
            if h1_tag:
                h1 = h1_tag.get_text(strip=True)
            
            # Извлекаем первый абзац
            first_paragraph = None
            main_content = soup.find(['main', 'article']) or soup.find('body')
            if main_content:
                for p in main_content.find_all('p'):
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        first_paragraph = text[:500]
                        break
            
            # Извлекаем весь видимый текст страницы
            full_text = None
            try:
                def get_body_text():
                    body = driver.find_element(By.TAG_NAME, "body")
                    return body.text if body.text else ""
                
                body_text = await loop.run_in_executor(None, get_body_text)
                if body_text and isinstance(body_text, str) and body_text.strip():
                    full_text = body_text[:5000] if len(body_text) > 5000 else body_text
            except Exception as e:
                print(f"Ошибка при извлечении текста через Selenium: {e}")
                # Если не удалось получить через Selenium, используем BeautifulSoup
                if main_content:
                    try:
                        soup_text = main_content.get_text(strip=True)
                        if soup_text and isinstance(soup_text, str) and soup_text.strip():
                            full_text = soup_text[:5000] if len(soup_text) > 5000 else soup_text
                    except Exception as e2:
                        print(f"Ошибка при извлечении текста через BeautifulSoup: {e2}")
            
            # Делаем скриншот
            screenshot_base64 = None
            try:
                # get_screenshot_as_png - это метод, можно вызывать напрямую
                screenshot = await loop.run_in_executor(None, driver.get_screenshot_as_png)
                # Конвертируем в base64
                if screenshot:
                    screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            except Exception as e:
                print(f"Ошибка при создании скриншота: {e}")
                import traceback
                print(traceback.format_exc())
            
            return title, h1, first_paragraph, screenshot_base64, full_text, None
            
        except WebDriverException as e:
            import traceback
            error_msg = f"Ошибка WebDriver: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # Проверяем, не связана ли ошибка с split
            if "'NoneType' object has no attribute 'split'" in str(e) or "split" in str(e).lower():
                return None, None, None, None, None, f"Ошибка конфигурации браузера. Проверьте установку Chrome/Яндекс браузера и ChromeDriver."
            return None, None, None, None, None, f"Ошибка WebDriver: {str(e)}"
        except TimeoutException:
            return None, None, None, None, None, "Превышено время ожидания загрузки страницы"
        except AttributeError as e:
            import traceback
            error_msg = f"Ошибка атрибута: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            if "split" in str(e).lower():
                return None, None, None, None, None, f"Ошибка обработки данных. Проверьте корректность URL и установку браузера."
            return None, None, None, None, None, f"Ошибка атрибута: {str(e)}"
        except Exception as e:
            import traceback
            error_msg = f"Неизвестная ошибка: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # Специальная обработка ошибки split
            if "'NoneType' object has no attribute 'split'" in str(e) or ("split" in str(e).lower() and "NoneType" in str(e)):
                return None, None, None, None, None, f"Ошибка конфигурации. Возможно, проблема с установкой ChromeDriver или путем к браузеру. Проверьте логи сервера для деталей."
            return None, None, None, None, None, f"Неизвестная ошибка: {str(e)}"
        finally:
            # Закрываем браузер
            if driver:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, driver.quit)
                except:
                    pass


# Глобальный экземпляр
parser_service = ParserService()
