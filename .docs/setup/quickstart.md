# GitHub Projects MCP - Quick Start

## 🚀 Быстрый старт (5 минут)

### 1. Установка

```bash
cd github-projects-mcp
uv sync
```

### 2. Настройка

Создайте `.env`:

```bash
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=artemfomin
GITHUB_REPO=TestRepo
```

Получить токен: https://github.com/settings/tokens (права: `repo`, `project`)

### 3. Тестирование

```bash
# Локальный запуск
uv run python -m github_projects_mcp.server

# MCP Inspector (веб-интерфейс)
mcp dev src/github_projects_mcp/server.py
```

### 4. Интеграция с Claude Code

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github-projects": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\полный\\путь\\к\\github-projects-mcp",
        "run",
        "python",
        "-m",
        "github_projects_mcp.server"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo"
      }
    }
  }
}
```

Перезапустите Claude Code.

## 🎯 Доступные команды

После подключения в Claude Code:

```
"Get all open tickets"
"Show me ticket #5"
"Add comment to ticket #3"
"Assign ticket #10 to myself"
"Add label 'bug' to ticket #2"
```

## 📚 Документация

- **README.md** - Полная документация
- **CLAUDE_CODE_SETUP.md** - Детальная инструкция по интеграции
- **tests/** - Примеры использования API

## 🔧 Troubleshooting

**Сервер не запускается?**
- Проверьте путь в конфигурации
- Убедитесь что GITHUB_TOKEN установлен
- Проверьте права токена

**Claude не видит инструменты?**
- Перезапустите Claude Code полностью
- Проверьте синтаксис JSON в конфигурации
- Посмотрите логи: `%APPDATA%\Claude\logs`

## ✅ Проверка установки

```bash
# Проверить импорты
uv run python -c "from github_projects_mcp.github import GitHubProjectsClient; print('OK')"

# Запустить тесты (требуется настроенный .env)
uv run pytest tests/test_github_client.py::test_client_initialization -v
```

## 🏗️ Архитектура

```
MCP Server (15 tools)
    ↓
TaskManagerInterface (абстракция)
    ↓
GitHubProjectsClient (реализация)
```

**Легко заменить на Jira/другой task manager** - просто реализуйте `TaskManagerInterface`!

## 📦 Что входит

- ✅ 15 MCP tools для работы с тикетами
- ✅ Абстрактный интерфейс для расширения
- ✅ Полная типизация (Pydantic)
- ✅ Тесты с использованием TestRepo
- ✅ Готовая интеграция с Claude Code

## 🔗 Ссылки

- Тестовый репозиторий: https://github.com/artemfomin/TestRepo
- MCP Documentation: https://modelcontextprotocol.io/
- GitHub GraphQL API: https://docs.github.com/en/graphql
