# Agent Fleet

Telegram-бот для управления Claude Code агентами на нескольких проектах одновременно.

## Что это?

Agent Fleet позволяет отправлять задачи Claude Code через Telegram и управлять выполнением на разных проектах. Вы выбираете проект, пишете промпт — Claude Code выполняет задачу в нужной директории.

## Возможности

- Работа с несколькими проектами из одного бота
- Выбор режима выполнения (Default, Accept Edits, Plan)
- Просмотр статуса и остановка выполнения
- Использование подписки Claude Max (без дополнительных API-затрат)

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/anthropics/agent_fleet.git
cd agent_fleet
```

### 2. Получите OAuth токен Claude

```bash
claude setup-token
```

Следуйте инструкциям — откроется браузер для авторизации. После успешного входа вы получите токен вида `sk-ant-oat01-...` (действителен 1 год).

### 3. Настройте окружение

Создайте `.env` файл:

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token
ALLOWED_USER_IDS=123456789,987654321

# Claude Code
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Projects Registry
ENVIRONMENTS_PATH=./environments.yaml
```

### 4. Настройте проекты

Создайте `environments.yaml`:

```yaml
projects:
  my-app:
    description: "My awesome app"
    path: /path/to/my-app

  another-project:
    description: "Another project"
    path: /path/to/another-project
```

### 5. Запустите

```bash
cd deploy/dev
./deploy.sh
```

## Архитектура

```
                                                                 ┌───────────┐
┌──────────────────┐                                             │ Project A │
│  Telegram Bot    │ ──┐                                    ┌──► │───────────│
└──────────────────┘   │                                    │    │ Project B │
                       │    ┌────────────┐    ┌──────────┐  │    └───────────┘
┌──────────────────┐   ├──► │            │    │  Claude  │  │
│  Taiga (planned) │ ──┼──► │  RabbitMQ  │◄──►│  Service │──┘
└──────────────────┘   │    │            │    │          │
                       │    └────────────┘    └──────────┘
┌──────────────────┐   │
│  Jira (planned)  │ ──┘
└──────────────────┘
```

- **Telegram Bot** — ручное управление через чат
- **Taiga / Jira** — автоматическое выполнение задач из таск-трекеров (в планах)
- **RabbitMQ** — очередь сообщений, точка интеграции
- **Claude Service** — выполняет запросы через Claude Code SDK

## Деплой

### Development (ARM64, Mac)

```bash
cd deploy/dev
./deploy.sh
```

### Production (AMD64, Linux)

```bash
cd deploy/prod
./deploy.sh
```

## Требования

- Docker / Podman
- Redis
- RabbitMQ
- Claude Max подписка (для OAuth токена)

## Лицензия

MIT
