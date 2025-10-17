# 🚀 START HERE - Быстрая установка MCP сервера

## ✅ Что уже готово:

- ✅ Проект создан и настроен
- ✅ Все зависимости установлены
- ✅ 15 MCP tools реализованы
- ✅ Тесты написаны
- ✅ Документация готова

## ⚠️ Что нужно сделать СЕЙЧАС:

### Шаг 1: Добавить GitHub токен (2 минуты)

1. Получите токен: https://github.com/settings/tokens
   - Права: `repo` + `project`

2. Откройте `.env` файл:
   ```bash
   notepad .env
   ```

3. Замените `your_token_here` на ваш токен:
   ```env
   GITHUB_TOKEN=ghp_ваш_настоящий_токен
   ```

### Шаг 2: Тестирование (3 минуты)

```bash
# Запустить MCP Inspector
mcp dev src/github_projects_mcp/server.py
```

Откроется браузер → протестируйте инструменты!

### Шаг 3: Настройка Claude Code (5 минут)

1. Откройте конфигурацию:
   ```bash
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Скопируйте содержимое из `claude_desktop_config.json`

3. **Замените `your_token_here` на ваш токен!**

4. Перезапустите Claude Code

### Шаг 4: Проверка

В Claude Code напишите:
```
Show me available MCP tools
```

Должны появиться 15 инструментов github-projects!

---

## 📚 Документация:

- **INSTALLATION_GUIDE.md** - Полная инструкция по установке
- **TEST_INSTRUCTIONS.md** - Как тестировать
- **QUICKSTART.md** - Быстрый старт
- **README.md** - Полная документация проекта
- **CLAUDE_CODE_SETUP.md** - Детали интеграции

---

## 🆘 Проблемы?

### Сервер не запускается:
```bash
uv sync
uv run python -c "from github_projects_mcp.github import GitHubProjectsClient; print('OK')"
```

### Claude не видит сервер:
1. Проверьте путь в конфиге (должен быть абсолютный)
2. Проверьте синтаксис JSON
3. Полностью перезапустите Claude Code

### Ошибки API:
- Проверьте токен (не истёк ли?)
- Проверьте права токена (repo + project)
- Проверьте доступ к your_repo_name

---

## 🎯 Тестовые команды для Claude Code:

После установки попробуйте:

```
Get all open tickets from your_repo_name
Show me ticket #1
Add comment "Testing" to ticket #1
Show me all labels
Assign ticket #2 to myself
```

---

## ✨ Готово!

После настройки вы сможете управлять GitHub Projects через Claude Code!

**Текущее расположение:**
```
/absolute/path/to/github-projects-mcp
```

**Следующий шаг:** Откройте `.env` и добавьте ваш GitHub токен!
