# Интеграция с Claude Code

Пошаговая инструкция по подключению GitHub Projects MCP сервера к Claude Code.

## Шаг 1: Установка зависимостей

```bash
cd github-projects-mcp
uv sync --frozen --dev
```

## Шаг 2: Настройка переменных окружения

1. Создайте `.env` файл:

```bash
cp .env.example .env
```

2. Получите GitHub Personal Access Token:
   - Откройте https://github.com/settings/tokens
   - "Generate new token (classic)"
   - Выберите права:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `project` (Full control of projects)
   - Скопируйте токен

3. Заполните `.env`:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=artemfomin
GITHUB_REPO=TestRepo
GITHUB_PROJECT_NUMBER=1
```

## Шаг 3: Тестирование сервера

### Локальное тестирование

```bash
# Запуск сервера
uv run python -m github_projects_mcp.server

# Или через MCP Inspector
mcp dev src/github_projects_mcp/server.py
```

### Проверка функциональности

```bash
# Установите зависимости для тестов
uv sync --frozen --dev

# Запустите тесты
uv run pytest -v
```

## Шаг 4: Конфигурация Claude Code

### Для Windows

1. Найдите файл конфигурации Claude Code:
   - Обычно: `%APPDATA%\Claude\claude_desktop_config.json`
   - Или: `C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json`

2. Откройте файл в редакторе

3. Добавьте конфигурацию MCP сервера:

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
        "GITHUB_REPO": "TestRepo",
        "GITHUB_PROJECT_NUMBER": "1"
      }
    }
  }
}
```

**Важно**: Замените путь на актуальный путь к вашему проекту!

### Для Linux/macOS

1. Найдите файл конфигурации:
   - Linux: `~/.config/Claude/claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Добавьте конфигурацию:

```json
{
  "mcpServers": {
    "github-projects": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/username/github-projects-mcp",
        "run",
        "python",
        "-m",
        "github_projects_mcp.server"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo",
        "GITHUB_PROJECT_NUMBER": "1"
      }
    }
  }
}
```

### Альтернативная конфигурация (через Python напрямую)

Если у вас не установлен `uv`, можно использовать Python напрямую:

```json
{
  "mcpServers": {
    "github-projects": {
      "command": "python",
      "args": [
        "-m",
        "github_projects_mcp.server"
      ],
      "cwd": "C:\\Projects\\MCP\\GithubProjects\\github-projects-mcp\\src",
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo",
        "GITHUB_PROJECT_NUMBER": "1"
      }
    }
  }
}
```

## Шаг 5: Перезапуск Claude Code

1. Полностью закройте Claude Code
2. Запустите заново
3. MCP сервер должен автоматически подключиться

## Шаг 6: Проверка интеграции

### Проверка доступных инструментов

Спросите Claude:

```
You: Show me available MCP tools for github-projects
```

Claude должен показать список из 15 инструментов:
- get_tickets
- get_ticket
- get_comments
- add_comment
- get_labels
- get_ticket_labels
- add_label
- update_status
- add_branch
- add_pull_request
- add_subtask
- assign_ticket
- assign_to_self
- get_milestones
- add_milestone

### Тестовые команды

#### 1. Получить список тикетов

```
You: Get all open tickets from TestRepo
```

#### 2. Получить конкретный тикет

```
You: Show me details of ticket #1
```

#### 3. Добавить комментарий

```
You: Add comment "Testing MCP integration" to ticket #1
```

#### 4. Назначить тикет на себя

```
You: Assign ticket #2 to myself
```

#### 5. Добавить лейбл

```
You: Add label "bug" to ticket #3
```

## Troubleshooting

### Сервер не запускается

1. **Проверьте пути в конфигурации**
   ```bash
   # Проверьте что путь существует
   ls "C:\Projects\MCP\GithubProjects\github-projects-mcp"
   ```

2. **Проверьте переменные окружения**
   ```bash
   # Убедитесь что GITHUB_TOKEN установлен
   echo $GITHUB_TOKEN  # Linux/macOS
   echo %GITHUB_TOKEN% # Windows
   ```

3. **Проверьте права токена**
   - Токен должен иметь права `repo` и `project`
   - Токен должен быть активным

### Claude не видит инструменты

1. **Проверьте логи Claude Code**
   - Windows: `%APPDATA%\Claude\logs`
   - Linux: `~/.config/Claude/logs`
   - macOS: `~/Library/Logs/Claude`

2. **Проверьте синтаксис JSON**
   - Используйте валидатор JSON для проверки конфигурации
   - Убедитесь что все скобки закрыты

3. **Перезапустите Claude Code полностью**
   - Закройте все окна
   - Завершите процесс в диспетчере задач (Windows) или Activity Monitor (macOS)
   - Запустите заново

### Ошибки при выполнении команд

1. **"Ticket not found"**
   - Убедитесь что тикет существует в репозитории
   - Проверьте правильность GITHUB_OWNER и GITHUB_REPO

2. **"GraphQL errors"**
   - Проверьте права токена
   - Убедитесь что у вас есть доступ к репозиторию

3. **"Authentication failed"**
   - Проверьте что токен правильно скопирован
   - Убедитесь что токен не истёк

## Дополнительные возможности

### Работа с несколькими репозиториями

Создайте несколько конфигураций:

```json
{
  "mcpServers": {
    "github-projects-testrepo": {
      "command": "uv",
      "args": ["--directory", "C:\\...\\github-projects-mcp", "run", "python", "-m", "github_projects_mcp.server"],
      "env": {
        "GITHUB_TOKEN": "ghp_token",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo"
      }
    },
    "github-projects-mainproject": {
      "command": "uv",
      "args": ["--directory", "C:\\...\\github-projects-mcp", "run", "python", "-m", "github_projects_mcp.server"],
      "env": {
        "GITHUB_TOKEN": "ghp_token",
        "GITHUB_OWNER": "myorg",
        "GITHUB_REPO": "MainProject"
      }
    }
  }
}
```

### Логирование

Для отладки можно добавить логирование в `server.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server.log'
)
```

## Полезные ссылки

- [MCP Documentation](https://modelcontextprotocol.io/)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [Claude Code](https://claude.ai/claude-code)

## Поддержка

Если возникли проблемы:

1. Проверьте логи сервера
2. Запустите тесты: `uv run pytest -v`
3. Проверьте конфигурацию через MCP Inspector: `mcp dev src/github_projects_mcp/server.py`
4. Создайте issue в репозитории проекта
