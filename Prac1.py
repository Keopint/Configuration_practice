
"""
Эмулятор командной оболочки UNIX-подобной ОС.
Этап 1: REPL (Read-Eval-Print Loop).
Вариант 18.
"""

import shlex
import sys
from VirtualFileSystem import VirtualFileSystem

def parse_command(line: str) -> list:
    try:
        # shlex.split корректно обрабатывает кавычки и пробелы внутри них
        parts = shlex.split(line)
    except ValueError as e:
        print(f"Ошибка разбора: {e}")
        return []
    return parts

def cmd_ls(args: list) -> None:
    print(f"ls: {args}")

def cmd_cd(args: list) -> None:
    print(f"cd: {args}")

def repl_one(vfs: VirtualFileSystem) -> None:
    """Основной цикл REPL (Read-Eval-Print Loop)."""
    print(f"Добро пожаловать в эмулятор оболочки. VFS: {vfs.name}")
    print("Введите 'exit' для выхода.\n")

    while True:
        try:
            line = input(f"{vfs.name}> ")
        except (EOFError, KeyboardInterrupt):
            # Позволяет выйти по Ctrl+D или Ctrl+C
            print("\nВыход.")
            break

        if not line.strip():
            continue

        parts = parse_command(line)
        if not parts:
            continue

        command = parts[0]
        args = parts[1:]

        if command == "exit":
            print("Выход из эмулятора.")
            break
        elif command == "ls":
            cmd_ls(args)
        elif command == "cd":
            cmd_cd(args)
        else:
            print(f"{vfs.name}: команда не найдена: {command}")
