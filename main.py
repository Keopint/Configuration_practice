import argparse
import shlex
import sys
import os


class VirtualFileSystem:
    def __init__(self, name: str = "vfs", physical_path: str = None):
        self.name = name
        self.physical_path = physical_path


class EmulatorConfig:
    def __init__(self, vfs_path: str = None, script_path: str = None):
        self.vfs_path = vfs_path
        self.script_path = script_path

    def debug_print(self) -> None:
        print("=" * 40)
        print("Конфигурация эмулятора:")
        print(f"  Путь к VFS:                {self.vfs_path or 'не указан'}")
        print(f"  Путь к стартовому скрипту: {self.script_path or 'не указан'}")
        print("=" * 40)
        print()


def parse_command(line: str) -> list:
    """Разбирает строку ввода на команду и аргументы."""
    try:
        return shlex.split(line)
    except ValueError as e:
        print(f"Ошибка разбора: {e}")
        return []


def cmd_ls(args: list) -> None:
    print(f"ls: {args}")


def cmd_cd(args: list) -> None:
    print(f"cd: {args}")


def execute_command(command: str, args: list, vfs: VirtualFileSystem) -> bool:
    if command == "exit":
        return True
    elif command == "ls":
        cmd_ls(args)
        return True
    elif command == "cd":
        cmd_cd(args)
        return True
    else:
        print(f"{vfs.name}: команда не найдена: {command}")
        return False


def run_script(script_path: str, vfs: VirtualFileSystem) -> None:
    if not os.path.isfile(script_path):
        print(f"Ошибка: стартовый скрипт не найден: {script_path}")
        sys.exit(1)

    print(f"Выполнение стартового скрипта: {script_path}\n")

    with open(script_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue

            # Имитация диалога: показываем ввод пользователя
            print(f"{vfs.name}> {line}")

            parts = parse_command(line)
            if not parts:
                print(f"Ошибка в строке {line_num}: пустая команда после разбора")
                print("Скрипт остановлен из-за ошибки.")
                sys.exit(1)

            command = parts[0]
            args = parts[1:]

            if command == "exit":
                print("Выход из эмулятора.")
                sys.exit(0)

            success = execute_command(command, args, vfs)
            if not success:
                print(f"\nСкрипт остановлен из-за ошибки в строке {line_num}.")
                sys.exit(1)

    print("\nСтартовый скрипт успешно выполнен.")


def repl(vfs: VirtualFileSystem) -> None:
    """Основной цикл REPL."""
    print(f"Добро пожаловать в эмулятор оболочки. VFS: {vfs.name}")
    print("Введите 'exit' для выхода.\n")

    while True:
        try:
            line = input(f"{vfs.name}> ")
        except (EOFError, KeyboardInterrupt):
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

        execute_command(command, args, vfs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX-подобной ОС (Вариант 18)"
    )
    parser.add_argument(
        "--vfs",
        type=str,
        default=None,
        help="Путь к физическому расположению VFS"
    )
    parser.add_argument(
        "--script",
        type=str,
        default=None,
        help="Путь к стартовому скрипту для выполнения команд эмулятора"
    )

    args = parser.parse_args()

    config = EmulatorConfig(vfs_path=args.vfs, script_path=args.script)
    config.debug_print()

    vfs = VirtualFileSystem(name="vfs", physical_path=args.vfs)

    if args.script:
        run_script(args.script, vfs)

    repl(vfs)


if __name__ == "__main__":
    main()