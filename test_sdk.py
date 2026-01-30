#!/usr/bin/env python3
"""Тест Claude Code SDK"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions


async def simple_test():
    """Простой тест — один запрос"""
    print("=== Простой тест SDK ===")

    options = ClaudeCodeOptions(
        max_turns=1  # Ограничим для теста
    )

    try:
        async for message in query(
            prompt="Скажи 'Привет' и больше ничего",
            options=options
        ):
            print(f"Тип: {type(message).__name__}")
            print(f"Сообщение: {message}")
    except Exception as e:
        print(f"Ошибка: {type(e).__name__}: {e}")


async def parallel_test():
    """Тест параллельных запросов в одной директории"""
    print("\n=== Тест параллельных запросов ===")

    options = ClaudeCodeOptions(
        cwd="/tmp/test_parallel",
        max_turns=1
    )

    async def make_request(request_id: int):
        print(f"[{request_id}] Начинаю запрос...")
        try:
            async for message in query(
                prompt=f"Скажи 'Запрос номер {request_id}' и больше ничего",
                options=options
            ):
                print(f"[{request_id}] {type(message).__name__}: {message}")
        except Exception as e:
            print(f"[{request_id}] Ошибка: {type(e).__name__}: {e}")
        print(f"[{request_id}] Завершён")

    # Запускаем два запроса параллельно
    await asyncio.gather(
        make_request(1),
        make_request(2)
    )


if __name__ == "__main__":
    import os
    os.makedirs("/tmp/test_parallel", exist_ok=True)

    # Параллельный тест
    asyncio.run(parallel_test())
