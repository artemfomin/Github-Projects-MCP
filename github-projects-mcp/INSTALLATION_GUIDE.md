# 🚀 Полная инструкция по установке и тестированию

## Текущий статус

✅ Проект создан: `C:\Projects\MCP\GithubProjects\github-projects-mcp`
✅ Зависимости установлены
✅ Структура готова
⏳ Требуется: GitHub токен и настройка Claude Code

---

## Часть 1: Локальное тестирование (без Claude Code)

### 1.1. Получить GitHub токен

1. Перейдите: https://github.com/settings/tokens
2. Нажмите **"Generate new token (classic)"**
3. Выберите права:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `project` (Full control of projects)
4. Нажмите **"Generate token"**
5. **Скопируйте токен** (будет показан только один раз!)

### 1.2. Настроить .env файл

Отредактируйте файл `.env` в корне проекта:

```bash
# Windows
notepad C:\Projects\MCP\GithubProjects\github-projects-mcp\.env

# Или в VS Code
code C:\Projects\MCP\GithubProjects\github-projects-mcp\.env
```

Замените `your_token_here` на ваш токен:

```env
GITHUB_TOKEN=ghp_ваш_настоящий_токен_здесь
GITHUB_OWNER=artemfomin
GITHUB_REPO=TestRepo
GITHUB_PROJECT_NUMBER=1
```

### 1.3. Тестирование через MCP Inspector

```bash
cd C:\Projects\MCP\GithubProjects\github-projects-mcp
mcp dev src/github_projects_mcp/server.py
```

Откроется браузер с веб-интерфейсом на http://localhost:5173

#### Что тестировать:

**1. Инструмент: `get_tickets`**
```json
{"status": "open", "limit": 10}
```
Должен вернуть список открытых тикетов

**2. Инструмент: `get_ticket`**
```json
{"ticket_id": "1"}
```
Должен показать детали тикета #1

**3. Инструмент: `get_labels`**
```json
{}
```
Должен показать все лейблы

**4. Инструмент: `get_milestones`**
```json
{}
```
Должен показать майлстоуны

**5. Инструмент: `add_comment`** (опционально)
```json
{"ticket_id": "1", "body": "Test from MCP Inspector"}
```
Добавит тестовый комментарий

---

## Часть 2: Интеграция с Claude Code

### 2.1. Найти конфигурацию Claude Code

Конфигурация находится по пути:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

Полный путь обычно:
```
C:\Users\ВашеИмя\AppData\Roaming\Claude\claude_desktop_config.json
```

**Проверить существование:**
```bash
dir %APPDATA%\Claude\claude_desktop_config.json
```

Если файл не существует - создайте его!

### 2.2. Настроить конфигурацию

Готовый файл уже создан: `claude_desktop_config.json`

**Вариант А: Скопировать конфигурацию**

1. Откройте файл `claude_desktop_config.json` из проекта
2. **Замените `your_token_here` на ваш GitHub токен**
3. Скопируйте весь content

**Если у вас уже есть `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
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
        "GITHUB_TOKEN": "ВАШ_ТОКЕН",
        "GITHUB_OWNER": "artemfomin",
        "GITHUB_REPO": "TestRepo",
        "GITHUB_PROJECT_NUMBER": "1"
      }
    }
  }
}
```

**Если файл не существует - создайте новый:**

```bash
# Windows PowerShell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Вставьте содержимое из `claude_desktop_config.json` (не забудьте заменить токен!)

### 2.3. Перезапустить Claude Code

1. **Полностью закройте Claude Code**
2. Откройте Task Manager (Ctrl+Shift+Esc)
3. Найдите процесс "Claude" и завершите его (если есть)
4. **Запустите Claude Code заново**

### 2.4. Проверка подключения

Спросите Claude:

```
Show me available MCP tools
```

или

```
List all MCP servers
```

Вы должны увидеть сервер **"github-projects"** с 15 инструментами:
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

---

## Часть 3: Тестирование в Claude Code

### Тестовые команды:

**1. Список тикетов:**
```
Get all open tickets from TestRepo
```

**2. Детали тикета:**
```
Show me details of ticket #1
```

**3. Комментарии:**
```
Get comments for ticket #1
```

**4. Добавить комментарий:**
```
Add comment "Testing MCP integration from Claude Code" to ticket #1
```

**5. Лейблы:**
```
Show me all available labels in TestRepo
```

**6. Назначить тикет:**
```
Assign ticket #2 to myself
```

**7. Изменить статус:**
```
Close ticket #3
```

**8. Майлстоуны:**
```
Show me all milestones in TestRepo
```

---

## Troubleshooting

### ❌ Сервер не запускается в MCP Inspector

```bash
# Проверить .env
cd C:\Projects\MCP\GithubProjects\github-projects-mcp
cat .env

# Проверить зависимости
uv sync

# Проверить импорты
uv run python -c "from github_projects_mcp.github import GitHubProjectsClient; print('OK')"

# Проверить токен
echo $GITHUB_TOKEN  # Linux/Mac
echo %GITHUB_TOKEN% # Windows
```

### ❌ Claude Code не видит сервер

1. **Проверить синтаксис JSON:**
   - Используйте JSON validator: https://jsonlint.com/
   - Все кавычки должны быть двойными
   - Путь должен использовать двойные обратные слэши `\\`

2. **Проверить путь:**
   ```bash
   # Должна существовать директория
   dir C:\Projects\MCP\GithubProjects\github-projects-mcp
   ```

3. **Посмотреть логи Claude Code:**
   ```
   %APPDATA%\Claude\logs
   ```

4. **Полностью перезапустить Claude Code:**
   - Task Manager → End Task "Claude"
   - Запустить заново

### ❌ Ошибки API при выполнении команд

1. **"Authentication failed"**
   - Проверить что токен правильный
   - Проверить права токена (repo, project)

2. **"Ticket not found"**
   - Убедитесь что тикет существует в TestRepo
   - Проверьте GITHUB_OWNER и GITHUB_REPO

3. **"GraphQL errors"**
   - Проверьте что у вас есть доступ к репозиторию
   - Проверьте что токен не истёк

---

## Проверка установки

### ✅ Checklist:

- [ ] `.env` файл создан и содержит валидный токен
- [ ] MCP Inspector запускается (`mcp dev src/github_projects_mcp/server.py`)
- [ ] Инструменты работают в Inspector
- [ ] `claude_desktop_config.json` настроен с правильным путём и токеном
- [ ] Claude Code перезапущен
- [ ] Claude видит 15 инструментов github-projects
- [ ] Тестовые команды выполняются успешно

---

## Быстрый старт (TL;DR)

```bash
# 1. Настроить токен
notepad C:\Projects\MCP\GithubProjects\github-projects-mcp\.env
# Вставить токен

# 2. Тест локально
cd C:\Projects\MCP\GithubProjects\github-projects-mcp
mcp dev src/github_projects_mcp/server.py

# 3. Настроить Claude Code
notepad %APPDATA%\Claude\claude_desktop_config.json
# Скопировать конфигурацию из claude_desktop_config.json проекта

# 4. Перезапустить Claude Code

# 5. Проверить
# В Claude Code: "Show me available MCP tools"
```

---

## Полезные ссылки

- 🔗 TestRepo: https://github.com/artemfomin/TestRepo
- 🔗 GitHub Tokens: https://github.com/settings/tokens
- 🔗 MCP Documentation: https://modelcontextprotocol.io/
- 🔗 Claude Code: https://claude.ai/claude-code

---

## 🎉 Готово!

После успешной установки вы сможете управлять тикетами GitHub Projects прямо из Claude Code через естественный язык!
