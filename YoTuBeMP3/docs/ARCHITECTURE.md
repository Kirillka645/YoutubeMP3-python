# Architecture Design: YouTube MP3 Downloader

## 📌 Обзор проекта

Python-приложение для скачивания аудио с YouTube в формате MP3 с выбором битрейта (128, 192, 320 kbps), оптимизированное для использования в РФ.

---

## 🎯 Выбор библиотек

### Основные библиотеки

| Библиотека | Версия | Назначение | Обоснование |
|------------|--------|------------|-------------|
| `yt-dlp` | 2024.x | Скачивание с YouTube | Активная поддержка, лучший парсер YouTube, встроенный прокси-менеджмент |
| `pycryptodome` | 3.20.x | Криптографические операции | Для дешифрования потоков при необходимости |
| `requests` | 2.31.x | HTTP-запросы | Для работы с прокси и API |
| `colorama` | 0.4.x | Цветной вывод в CLI | Улучшенный UX |

### FFmpeg (внешний)

| Компонент | Назначение |
|-----------|------------|
| `ffmpeg` | Конвертация аудио в MP3 с заданным битрейтом |
| `ffprobe` | Получение метаданных аудио |

**Установка FFmpeg:**
- Windows: `choco install ffmpeg` или скачать с ffmpeg.org
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

---

## 🏗️ Архитектура приложения

```
youtube_mp3_downloader/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Конфигурация приложения
│   │   └── proxies.py           # Менеджер прокси
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py        # Основной загрузчик (yt-dlp wrapper)
│   │   ├── converter.py         # Конвертер аудио (ffmpeg)
│   │   └── metadata.py          # Обработка метаданных
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── parser.py            # Argparse настройки
│   │   └── output.py            # Форматированный вывод
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Валидация URL
│       ├── path_utils.py        # Работа с путями
│       └── logging_utils.py     # Настройка логирования
├── tests/
│   ├── __init__.py
│   ├── test_downloader.py
│   └── test_converter.py
├── logs/
│   └── .gitkeep
├── output/
│   └── .gitkeep
├── requirements.txt
├── setup.py
├── README.md
└── .env.example
```

---

## 🔧 Основные компоненты

### 1. Config модуль

#### [`src/config/settings.py`](src/config/settings.py)
```python
class Settings:
    """Конфигурация приложения."""
    
    # Поддерживаемые битрейты
    BITRATES = {
        '128': 128,
        '192': 192,
        '320': 320
    }
    
    # Формат вывода
    DEFAULT_FORMAT = 'mp3'
    
    # Настройки yt-dlp
    YTDLP_OPTIONS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'writethumbnail': False,
        'nocheckcertificate': True,
    }
    
    # Таймауты
    DOWNLOAD_TIMEOUT = 300  # секунд
    CONNECTION_TIMEOUT = 30
```

#### [`src/config/proxies.py`](src/config/proxies.py)
```python
class ProxyManager:
    """Менеджер прокси для обхода блокировок."""
    
    def __init__(self):
        self.proxy_list = []
        self.current_proxy = None
    
    def load_proxies(self, proxy_file: str) -> list:
        """Загрузка списка прокси из файла."""
        pass
    
    def test_proxy(self, proxy: dict) -> bool:
        """Тестирование прокси."""
        pass
    
    def get_working_proxy(self) -> dict:
        """Получение рабочего прокси."""
        pass
    
    def rotate_proxy(self) -> dict:
        """Ротация прокси."""
        pass
```

### 2. Core модуль

#### [`src/core/downloader.py`](src/core/downloader.py)
```python
from yt_dlp import YoutubeDL
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass
class DownloadProgress:
    """Прогресс загрузки."""
    filename: str
    percent: float
    speed: str
    eta: str

class YouTubeDownloader:
    """Основной класс для скачивания аудио с YouTube."""
    
    def __init__(self, bitrate: int = 192, proxy: Optional[dict] = None):
        self.bitrate = bitrate
        self.proxy = proxy
        self.options = self._get_options()
    
    def _get_options(self) -> dict:
        """Формирование опций yt-dlp."""
        pass
    
    def set_progress_hook(self, hook: Callable[[dict], None]):
        """Установка колбэка для отслеживания прогресса."""
        pass
    
    def get_video_info(self, url: str) -> dict:
        """Получение информации о видео."""
        pass
    
    def download(self, url: str, output_path: str) -> str:
        """Скачивание аудио."""
        pass
```

#### [`src/core/converter.py`](src/core/converter.py)
```python
import subprocess
from pathlib import Path
from typing import Optional

class AudioConverter:
    """Конвертер аудио с использованием FFmpeg."""
    
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path
    
    def convert_to_mp3(
        self,
        input_file: Path,
        output_file: Path,
        bitrate: int,
        metadata: Optional[dict] = None
    ) -> bool:
        """Конвертация аудио в MP3 с заданным битрейтом."""
        pass
    
    def extract_audio(
        self,
        video_file: Path,
        output_file: Path,
        bitrate: int
    ) -> bool:
        """Извлечение аудио из видео."""
        pass
    
    def add_metadata(
        self,
        audio_file: Path,
        metadata: dict
    ) -> bool:
        """Добавление метаданных к аудиофайлу."""
        pass
```

### 3. CLI модуль

#### [`src/cli/parser.py`](src/cli/parser.py)
```python
import argparse
from pathlib import Path

def create_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов командной строки."""
    
    parser = argparse.ArgumentParser(
        description='YouTube MP3 Downloader - скачивание аудио с YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  %(prog)s "https://youtube.com/watch?v=..."
  %(prog)s "https://youtube.com/watch?v=..." --bitrate 320
  %(prog)s "https://youtube.com/watch?v=..." --output ./music
  %(prog)s "https://youtube.com/watch?v=..." --proxy http://proxy:8080
        '''
    )
    
    parser.add_argument('url', help='URL видео YouTube')
    parser.add_argument(
        '-b', '--bitrate',
        type=int,
        choices=[128, 192, 320],
        default=192,
        help='Битрейт MP3 (128, 192, 320). По умолчанию: 192'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('./output'),
        help='Путь для сохранения файлов'
    )
    parser.add_argument(
        '-p', '--proxy',
        type=str,
        help='Прокси-сервер (http://user:pass@host:port)'
    )
    parser.add_argument(
        '--proxy-file',
        type=Path,
        help='Файл со списком прокси'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='Показать доступные форматы'
    )
    
    return parser
```

---

## 🇷🇺 Рекомендации по обходу блокировок в РФ

### 1. Прокси-серверы

| Тип | Протокол | Плюсы | Минусы |
|-----|----------|-------|--------|
| HTTP/HTTPS | HTTP | Простая настройка | Может блокироваться |
| SOCKS5 | SOCKS5 | Более стабильный | Требует настройки |
| VPN | WireGuard/OpenVPN | Надежный | Требует VPN-сервис |

### 2. Реализация в приложении

```python
# Пример использования прокси в yt-dlp
proxy_options = {
    'proxy': 'http://user:pass@proxy:port',
    'socket_timeout': 30,
}

# Для VPN можно использовать --ffmpeg-location
```

### 3. Стратегии обхода

1. **Ротация прокси**: Автоматическая смена при недоступности
2. **Cloudflare Worker**: Проксирование через Cloudflare
3. **IPv6**: Использование IPv6 при наличия
4. **DNS-over-HTTPS**: Скрытие DNS-запросов

---

## 📊 Диаграмма потока данных

```mermaid
flowchart TD
    A[Ввод URL] --> B{Валидация URL}
    B -->|Невалидный| C[Ошибка]
    B -->|Валидный| D[Получение информации о видео]
    D --> E[Проверка прокси]
    E -->|Нужен прокси| F[Выбор прокси]
    F --> G[Скачивание аудио yt-dlp]
    E -->|Не нужен| G
    G --> H{Успех?}
    H -->|Нет| I[Ротация прокси]
    I --> E
    H -->|Да| J[Конвертация в MP3 ffmpeg]
    J --> K[Установка битрейта]
    K --> L[Добавление метаданных]
    L --> M[Сохранение файла]
    M --> N[Вывод результата]
```

---

## ⚠️ Обработка ошибок

| Ошибка | Код | Обработка |
|--------|-----|-----------|
| `VideoUnavailable` | 1001 | Видео недоступно - проверить URL |
| `DownloadError` | 1002 | Ошибка загрузки - попробовать прокси |
| `ConversionError` | 1003 | Ошибка конвертации - проверить FFmpeg |
| `ProxyError` | 1004 | Прокси не работает - сменить прокси |
| `AuthError` | 1005 | Ошибка аутентификации прокси |

### Логирование

```python
import logging

# Уровни логирования
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}

# Формат логов
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

---

## 🚀 План реализации

1. **Фаза 1**: Базовый функционал
   - [ ] Создать структуру проекта
   - [ ] Реализовать yt-dlp интеграцию
   - [ ] Добавить CLI интерфейс
   - [ ] Реализовать конвертацию MP3

2. **Фаза 2**: Расширенный функционал
   - [ ] Добавить поддержку прокси
   - [ ] Реализовать ротацию прокси
   - [ ] Добавить пакетное скачивание
   - [ ] Интегрировать плейлисты

3. **Фаза 3**: UX улучшения
   - [ ] GUI интерфейс (опционально)
   - [ ] Системные уведомления
   - [ ] История загрузок
