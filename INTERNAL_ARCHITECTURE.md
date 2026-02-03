# Внутренняя архитектура Claude Service

Иерархия сущностей между сервисом работы с SDK и внешними системами.

## Решения по открытым вопросам

| Вопрос | Решение |
|--------|---------|
| История действий в реальном времени | Да, уже реализовано через стриминг ToolUseBlock в Telegram |
| Биллинг по задачам/проектам | Да, нужна фактическая оценка задачи (токены, итерации, комментарии) |
| Resume после сбоя сервера | Опционально, не усложнять архитектуру ради этого |
| Связь Tasks Claude Code с внешними задачами | Никак не связаны, не предусматриваем |

## Иерархия сущностей

```
┌─────────────────────────────────────────────────────────┐
│                    External Task                         │
│                  (Jira / Taiga)                         │
└─────────────────────┬───────────────────────────────────┘
                      │ 1:1
                      ▼
┌─────────────────────────────────────────────────────────┐
│                       Job                                │
│  • id                                                   │
│  • external_task_id (Jira/Taiga task_id)               │
│  • project_id                                           │
│  • status: pending | running | completed | failed       │
│  • created_at, completed_at                             │
│  • Агрегированные метрики (считаем из сессий)          │
└─────────────────────┬───────────────────────────────────┘
                      │ 1:N
                      ▼
┌─────────────────────────────────────────────────────────┐
│                     Session                              │
│  • job_id                                               │
│  • session_id (от Claude Code)                          │
│  • Детали НЕ храним — они есть в JSONL Claude Code     │
└─────────────────────────────────────────────────────────┘
```

## Что хранит Claude Code

Claude Code сохраняет сессии в `~/.claude/projects/{project}/`:
- `{session_id}.jsonl` — полный лог сессии
- `{session_id}/` — директория для файлов сессии

### Структура JSONL

```jsonl
{"type": "user", "sessionId": "...", "message": {...}, "timestamp": "..."}
{"type": "assistant", "message": {"content": [...], "usage": {...}}, "timestamp": "..."}
{"type": "progress", ...}
```

### Что есть в каждом assistant message

```json
{
  "message": {
    "model": "claude-opus-4-5-20251101",
    "content": [
      {"type": "thinking", "thinking": "..."},
      {"type": "text", "text": "..."},
      {"type": "tool_use", "name": "Edit", "input": {...}}
    ],
    "usage": {
      "input_tokens": 8,
      "cache_creation_input_tokens": 2071,
      "cache_read_input_tokens": 29994,
      "output_tokens": 2
    }
  },
  "timestamp": "2026-01-31T12:57:44.381Z"
}
```

### Что нужно считать самим

- Суммарные токены (суммировать `usage` из assistant messages)
- Количество turns (считать user messages)
- Количество tool_use
- Общую длительность (разница timestamps)

## Фактическая оценка задачи

Для последующей аналитики сохраняем в БД:

| Метрика | Источник |
|---------|----------|
| Токены потраченные | Суммировать из JSONL или ResultMessage |
| Количество сессий | Считать Session записи по job_id |
| Количество итераций (turns) | Считать из JSONL |
| Количество комментариев | Считать из Jira/Taiga API |
| Время человека на общение | Считать паузы между user messages |

## Минимальная реализация

### Job (в PostgreSQL)

```python
@dataclass
class Job:
    id: str
    external_task_id: str | None
    project_id: str
    status: JobStatus
    created_at: datetime
    completed_at: datetime | None

    # Агрегированные метрики
    total_input_tokens: int
    total_output_tokens: int
    total_sessions: int
```

### Session (в PostgreSQL)

```python
@dataclass
class Session:
    id: str  # наш id
    job_id: str
    claude_session_id: str  # session_id от Claude Code
    started_at: datetime
    ended_at: datetime | None
```

Детали сессии (turns, tool_uses) НЕ дублируем — читаем из JSONL при необходимости.

## Статус

Архитектура согласована — готово к реализации.
