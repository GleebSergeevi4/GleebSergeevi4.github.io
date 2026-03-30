# Генератор сайта киберспортивных матчей

Статический генератор сайта, который создает 3 страницы с информацией о киберспортивных матчах на основе данных PandaScore API.

## Выполнение требований ТЗ

### Функциональность
- [x] Генерация 3 страниц с матчами (вчера, сегодня, завтра)
- [x] SEO поля (title, description, canonical, og:*, twitter:card)
- [x] JSON-LD микроразметка schema.org (Organization + WebSite)
- [x] Автоматическое создание дизайна на HTML/CSS без фреймворков
- [x] Структурные URL без параметров (/yesterday/, /today/, /tomorrow/)
- [x] Единовременное развертывание одной командой

## Отреализованное

### Архитектура
Проект построен на Python 3.12 с использованием статической генерации сайта (SSG).

**Основные модули:**
- `generator/fetch_matches.py` - интеграция с PandaScore API, фильтрация матчей по датам
- `generator/render.py` - рендеринг HTML страниц, генерация JSON-LD микроразметки
- `generator/main.py` - оркестратор: координация загрузки данных и генерации файлов
- `generator/template/matches.html` - шаблон страницы с переменными

### Особенности реализации

**API интеграция:**
- Использование PandaScore API для получения данных о матчах
- Фильтрация по датам: вчерашние матчи через /matches/past, текущие/будущие через /matches/upcoming
- Обработка временных зон (система автоматически переводит в UTC)
- Кросс-платформенная совместимость (Windows падбэк для tzdata)

**HTML/CSS дизайн:**
- Отзывчивый дизайн (max-width: 960px, скалируемый с clamp())
- Единая система CSS переменных для цветов и стилей
- Градиентные фоны (orange-red + blue тона)
- Карточки матчей с информацией о командах, лигах, времени начала
- Консистентный дизайн для всех 3 страниц и главной

**SEO оптимизация:**
- Мета-теги для каждой страницы (title, description, canonical)
- OpenGraph теги (og:title, og:description, og:url, og:type)
- Twitter Card теги
- JSON-LD Organization и WebSite разметка

**Структура URL:**
- Страницы доступны по фиксированным маршрутам без параметров
- Главная страница: /
- Матчи вчера: /yesterday/
- Матчи сегодня: /today/
- Матчи завтра: /tomorrow/
- API выгрузки: /api/*.json

### Развертывание и автоматизация

**GitHub Pages + GitHub Actions:**
- Автоматическое развертывание при push в main
- Ручное развертывание через workflow_dispatch
- Автоматическое обновление по расписанию (каждые 30 минут)
- Python 3.12 + pip install на CI/CD сервере
- Артефакты выгружаются в GitHub Pages

**Локальное использование:**
```bash
# Установка
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Генерация
python generator/main.py

# Результат в output/
```

### Структура проекта

```
PageGenerator/
├── generator/
│   ├── main.py              # Оркестратор
│   ├── fetch_matches.py     # API интеграция
│   ├── render.py            # HTML/JSON-LD генерация
│   └── template/
│       └── matches.html     # Шаблон страницы
├── .github/
│   └── workflows/
│       └── deploy-pages.yml # GitHub Actions
├── requirements.txt         # Зависимости (requests)
├── .gitignore              # Git исключения
└── README.md               # Этот файл
```

### Генерируемые артефакты

При запуске `python generator/main.py`:

**HTML страницы:**
- output/index.html - главная страница с навигацией
- output/yesterday/index.html - матчи за вчера
- output/today/index.html - матчи на сегодня
- output/tomorrow/index.html - матчи на завтра

**API выгрузки:**
- output/api/yesterday.json - сырые данные матчей за вчера
- output/api/today.json - данные матчей на сегодня
- output/api/tomorrow.json - данные матчей на завтра

**Служебные файлы:**
- output/.nojekyll - сигнал GitHub Pages не обрабатывать Jekyll

### Технологический стек

- Python 3.12
- requests - HTTP клиент для API
- zoneinfo/pytz - работа с часовыми поясами
- PandaScore API - источник данных о киберспортивных матчах
- GitHub Pages - хостинг
- GitHub Actions - CI/CD

### Настройка

**Переменные окружения:**
- `PANDASCORE_TOKEN` - токен API (по умолчанию используется тестовый)
- `SITE_URL` - базовый URL сайта (по умолчанию https://gleebsergeevi4.github.io/)

**Требования к системе:**
- Python 3.9+
- Интернет для загрузки данных PandaScore API
- Git (для развертывания)

### Известные ограничения

- Сайт статический: обновляется через GitHub Actions (push, manual, cron)
- Дизайн оптимизирован для desktop/tablet (все страницы отзывчивые, но мобильный адаптив ограничен)
- PandaScore API имеет rate limits (рекомендуемый интервал обновления: от 60 секунд)

### Покрытие ТЗ - детали

| Требование ТЗ | Статус | Реализация |
|---|---|---|
| 3 страницы (вчера/сегодня/завтра) | ✓ | HTML в /yesterday/, /today/, /tomorrow/ |
| SEO поля | ✓ | title, description, canonical, og:*, twitter:card |
| Микроразметка schema.org | ✓ | JSON-LD Organization + WebSite |
| Автогенерация дизайна | ✓ | HTML/CSS без фреймворков, Template-based |
| Без параметров в URL | ✓ | Фиксированные маршруты без query params |
| Единовременное развертывание | ✓ | `python generator/main.py` или GitHub Actions |

### Возможные расширения

- Добавление sitemap.xml и robots.txt
- Кэширование данных на диск
- Поддержка других спортивных API помимо PandaScore
- Добавление фильтров (по лигам, командам, турнирам)
- Генерация статических JSON API для интеграции с другими приложениями
