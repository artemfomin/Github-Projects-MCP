# GitHub Projects MCP - Applied Fixes

## Fix: Added Repository Projects Support

**Date**: 2025-10-17

**Problem**: 
`add_ticket_to_project` не работал, потому что метод `_get_project_id` искал проекты только у пользователей и организаций, но не у репозиториев.

**Solution Applied**:
Обновлен метод `_get_project_id` в `github-projects-mcp/src/github_projects_mcp/github/client.py:121-161` для поддержки repository projects.

**Changes**:
- Добавлен запрос `repository(owner: $owner, name: $repo) { projectV2(number: $number) { id } }`
- Приоритет поиска: repository → user → organization
- Теперь метод принимает параметр `repo` в GraphQL запросе

**Status**: ✅ Исправлено

**Testing**: 
После перезапуска MCP сервера должен работать `add_ticket_to_project` с project_number=6

**Configuration**:
`.env` файл обновлен: `GITHUB_PROJECT_NUMBER=6`
