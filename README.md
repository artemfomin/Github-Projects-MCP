# GitHub Projects MCP Server

MCP (Model Context Protocol) server для работы с GitHub Projects с расширяемым интерфейсом для других task manager'ов.

## Особенности

- ✅ **Абстрактный интерфейс**: Легко заменить GitHub на Jira или другой task manager
- ✅ **Слабое связывание**: Чистая архитектура с разделением слоев
- ✅ **20 инструментов**: Полная поддержка работы с тикетами и их связями
- ✅ **GraphQL API**: Использует современный GitHub GraphQL API
- ✅ **Type-safe**: Полная типизация с Pydantic моделями

## Архитектура

```
┌─────────────────────────────┐
│    MCP Server (FastMCP)     │  ← 20 tools для Claude
│  - get_tickets, add_comment │
│  - add_parent, add_blocking │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  TaskManagerInterface (ABC) │  ← Абстрактный слой
│  - All task operations      │     (можно заменить на Jira)
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  GitHubProjectsClient       │  ← GitHub реализация
│  - GraphQL API calls        │
└─────────────────────────────┘
```

## Установка

### 1. Установка зависимостей

```bash
cd github-projects-mcp
uv sync --frozen --dev
```

Или с помощью pip:

```bash
pip install -e .
```

### 2. Настройка окружения

Создайте `.env` файл на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# GitHub Personal Access Token с правами:
# - repo (full control)
# - project (read:project, write:project)
GITHUB_TOKEN=ghp_your_token_here

# Владелец репозитория
GITHUB_OWNER=artemfomin

# Название репозитория
GITHUB_REPO=TestRepo

# Номер проекта (опционально)
GITHUB_PROJECT_NUMBER=1
```

### 3. Создание GitHub Personal Access Token

1. Перейдите в Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выберите права:
   - ✅ `repo` (full control of private repositories)
   - ✅ `project` (full control of projects)
4. Скопируйте токен в `.env` файл

## Использование

### Запуск сервера

```bash
# Через uv
uv run python -m github_projects_mcp.server

# Или напрямую
python src/github_projects_mcp/server.py
```

### Тестирование с MCP Inspector

```bash
mcp dev src/github_projects_mcp/server.py
```

Откроется веб-интерфейс для тестирования всех инструментов.

## Доступные инструменты

### Работа с тикетами

1. **get_tickets** - Получить список тикетов
   - Фильтры: status, assignee, label, milestone, limit

2. **get_ticket** - Получить один тикет по ID/номеру

### Комментарии

3. **get_comments** - Получить комментарии к тикету
4. **add_comment** - Добавить комментарий

### Лейблы

5. **get_labels** - Получить все доступные лейблы
6. **get_ticket_labels** - Получить лейблы конкретного тикета
7. **add_label** - Добавить лейбл к тикету

### Статусы

8. **update_status** - Изменить статус тикета

### Ветки и PR

9. **add_branch** - Привязать ветку к тикету
10. **add_pull_request** - Привязать PR к тикету

### Создание тикетов

11. **create_ticket** - Создать новый тикет
12. **create_subtask** - Создать подзадачу

### Связи между тикетами

13. **add_subtask** - Добавить подзадачу к тикету
14. **add_parent** - Установить родительский тикет
15. **add_blocked_by** - Отметить, что тикет заблокирован другим
16. **add_blocking** - Отметить, что тикет блокирует другой

### Назначение

17. **assign_ticket** - Назначить тикет на пользователя
18. **assign_to_self** - Назначить тикет на себя

### Майлстоуны

19. **get_milestones** - Получить список майлстоунов
20. **add_milestone** - Добавить тикет к майлстоуну

### Проекты

21. **add_ticket_to_project** - Добавить тикет в проект

## Интеграция с Claude Code

### Добавление в конфигурацию

Отредактируйте конфигурацию Claude Code (обычно `~/.claude/config.json` или через UI):

```json
{
  "mcpServers": {
    "github-projects": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Projects\\MCP\\GithubProjects\\github-projects-mcp",
        "run",
        "python",
        "-m",
        "github_projects_mcp.server"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo"
      }
    }
  }
}
```

### Проверка интеграции

После добавления перезапустите Claude Code и проверьте доступные инструменты:

```
You: Show me available MCP tools
Claude: [должен показать 15 инструментов github-projects]
```

### Примеры использования

```
You: Get all open tickets from TestRepo
Claude: [использует get_tickets tool]

You: Add comment "Working on this" to ticket #5
Claude: [использует add_comment tool]

You: Assign ticket #10 to myself
Claude: [использует assign_to_self tool]
```

## Тестирование

### Настройка тестов

Тесты используют репозиторий https://github.com/artemfomin/TestRepo

```bash
# Убедитесь что .env настроен правильно
export GITHUB_TOKEN=your_token
export GITHUB_OWNER=artemfomin
export GITHUB_REPO=TestRepo
```

### Запуск тестов

```bash
# Все тесты
uv run pytest

# С выводом логов
uv run pytest -v

# Конкретный тест
uv run pytest tests/test_github_client.py -k test_get_tickets
```

## Разработка

### Добавление нового task manager'а

1. Создайте новый модуль (например, `jira/client.py`)
2. Реализуйте `TaskManagerInterface`
3. Обновите `server.py` для использования нового клиента

```python
from .jira import JiraClient

# В server_lifespan:
task_manager = JiraClient(
    url=settings.jira_url,
    username=settings.jira_username,
    api_token=settings.jira_token,
)
```

### Линтинг и форматирование

```bash
# Форматирование
uv run ruff format .

# Проверка стиля
uv run ruff check .

# Исправление проблем
uv run ruff check . --fix

# Проверка типов
uv run pyright
```

## Структура проекта

```
github-projects-mcp/
├── src/
│   └── github_projects_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server с tools
│       ├── config.py               # Настройки
│       ├── interfaces/
│       │   └── task_manager.py    # Абстрактный интерфейс
│       ├── models/                 # Pydantic модели
│       │   ├── ticket.py
│       │   ├── comment.py
│       │   ├── label.py
│       │   └── milestone.py
│       └── github/                 # GitHub реализация
│           └── client.py
├── tests/
│   ├── conftest.py
│   └── test_github_client.py
├── pyproject.toml
├── .env.example
└── README.md
```

## Требования

- Python >= 3.10
- GitHub Personal Access Token
- uv (рекомендуется) или pip

## Лицензия

MIT

## Автор

Your Name
