# Инструкция по тестированию MCP сервера

## Шаг 1: Настройка токена

Отредактируйте файл `.env` и замените `your_token_here` на ваш GitHub токен:

```bash
# Открыть .env в редакторе
notepad .env

# Или через PowerShell
code .env
```

Получить токен: https://github.com/settings/tokens
- Права: `repo` и `project`

## Шаг 2: Тестирование через MCP Inspector

```bash
cd github-projects-mcp
mcp dev src/github_projects_mcp/server.py
```

Откроется веб-интерфейс на http://localhost:5173

## Шаг 3: Тестирование инструментов

В Inspector'е протестируйте каждый инструмент:

### 1. get_tickets
```json
{
  "status": "open",
  "limit": 10
}
```

### 2. get_ticket
```json
{
  "ticket_id": "1"
}
```

### 3. get_labels
```json
{}
```

### 4. add_comment (опционально)
```json
{
  "ticket_id": "1",
  "body": "Test comment from MCP"
}
```

## Шаг 4: Настройка Claude Code

### Найти конфигурацию Claude Code:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Добавить конфигурацию:

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
        "GITHUB_TOKEN": "ВАШ_ТОКЕН_ЗДЕСЬ",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo",
        "GITHUB_PROJECT_NUMBER": "1"
      }
    }
  }
}
```

**Важно:** Замените путь на актуальный!

## Шаг 5: Перезапуск Claude Code

1. Полностью закройте Claude Code
2. Завершите процесс в Task Manager (если нужно)
3. Запустите Claude Code заново

## Шаг 6: Проверка в Claude Code

Спросите Claude:

```
Show me available MCP tools for github-projects
```

Должны появиться 15 инструментов.

## Тестовые команды:

```
Get all open tickets from TestRepo
Show me details of ticket #1
Add comment "Testing MCP" to ticket #1
Assign ticket #2 to myself
Get all labels
```

## Troubleshooting

### Сервер не запускается
```bash
# Проверить зависимости
cd github-projects-mcp
uv sync

# Проверить .env
cat .env

# Проверить импорты
uv run python -c "from github_projects_mcp.github import GitHubProjectsClient; print('OK')"
```

### Claude не видит инструменты
- Проверить синтаксис JSON конфигурации
- Проверить пути (должны быть абсолютные)
- Посмотреть логи Claude Code
- Перезапустить Claude Code полностью

### Ошибки API
- Проверить что токен валиден
- Проверить права токена (repo, project)
- Проверить что есть доступ к репозиторию artemfomin/TestRepo
