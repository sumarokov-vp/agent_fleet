# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Описание проекта

См. [CONCEPT.md](./CONCEPT.md)

## Технологический стек

- Python 3.14
- bot-framework — собственный фреймворк для Telegram-ботов
- claude-code-sdk — взаимодействие с Claude Code
- Redis — управление состоянием (флаги занятости с TTL)
- YAML — реестр окружений

## Дополнительные директории

- `/Users/vladimirsumarokov/dev/smartist/bot_framework` — исходный код bot-framework
