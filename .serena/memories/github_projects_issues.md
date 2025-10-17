# GitHub Projects MCP - Known Issues

## Issue: add_ticket_to_project не работает

**Проблема**: Инструмент `add_ticket_to_project` не может найти проект с номером 1 для пользователя artemfomin.

**Ошибка**:
```
GraphQL errors: [
  {'type': 'NOT_FOUND', 'path': ['organization'], 'message': "Could not resolve to an Organization with the login of 'artemfomin'."},
  {'type': 'NOT_FOUND', 'path': ['user', 'projectV2'], 'message': 'Could not resolve to a ProjectV2 with the number 1.'}
]
```

**Причина**: 
- У пользователя artemfomin нет GitHub Project V2 с номером 1
- Или проект существует но недоступен через API

**Решение**:
- Создать новый Project V2 на GitHub для TestRepo
- Или узнать правильный номер существующего проекта
- Или добавлять issues в проект вручную через GitHub UI

**Обходной путь**:
- Issues создаются корректно через `create_ticket`
- Их нужно добавлять в проект вручную через GitHub UI
- Все остальные инструменты работают (лейблы, комментарии, назначение, статусы и т.д.)

**Статус**: Известная проблема, требует настройки GitHub Project V2
