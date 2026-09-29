import argparse
import shlex
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================
#  VFS
# ============================================================

class VirtualFileSystem:
    """Виртуальная файловая система, загружаемая из директории на диске."""

    def __init__(self, root_path: str = None):
        self.root_path = root_path
        self.tree = {"type": "dir", "children": {}}
        self.current_path_components = []
        if root_path:
            self.load(root_path)

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Путь не найден: {path}")
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Не является директорией: {path}")
        self.tree = self._read_dir(path)
        self.root_path = path
        self.current_path_components = []

    def _read_dir(self, path: str) -> dict:
        node = {"type": "dir", "children": {}}
        try:
            for entry in os.listdir(path):
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    node["children"][entry] = self._read_dir(full)
                else:
                    try:
                        with open(full, "r", encoding="utf-8") as f:
                            content = f.read()
                    except (UnicodeDecodeError, PermissionError, OSError):
                        content = ""
                    node["children"][entry] = {"type": "file", "content": content}
        except PermissionError:
            raise PermissionError(f"Нет доступа к директории: {path}")
        return node

    @property
    def current_path(self) -> str:
        if not self.current_path_components:
            return "/"
        return "/" + "/".join(self.current_path_components)

    def info(self) -> str:
        if self.root_path:
            return f"VFS загружена из: {self.root_path}"
        return "VFS по умолчанию (пустая)"

    def count_elements(self) -> int:
        def _count(node):
            if node["type"] == "dir":
                return 1 + sum(_count(c) for c in node["children"].values())
            return 1
        return _count(self.tree)

    def resolve(self, path: str) -> list:
        if path in ("", "~"):
            return []
        if path.startswith("/"):
            components = []
        else:
            components = list(self.current_path_components)

        for part in path.split("/"):
            if part in ("", "."):
                continue
            elif part == "..":
                if components:
                    components.pop()
            else:
                components.append(part)
        return components

    def get_node(self, components: list):
        node = self.tree
        for part in components:
            if node["type"] != "dir":
                return None
            if part not in node["children"]:
                return None
            node = node["children"][part]
        return node


# ============================================================
#  Конфигурация
# ============================================================

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


# ============================================================
#  Парсер
# ============================================================

def parse_command(line: str) -> list:
    try:
        return shlex.split(line)
    except ValueError as e:
        print(f"Ошибка разбора: {e}")
        return []


# ============================================================
#  Команды (заглушки на этапе 3)
# ============================================================

def cmd_ls(args, vfs) -> bool:
    print(f"ls: {args}")
    print(f"    (текущая директория VFS: {vfs.current_path})")
    return True


def cmd_cd(args, vfs) -> bool:
    print(f"cd: {args}")
    return True


def cmd_vfs_info(args, vfs) -> bool:
    print(vfs.info())
    print(f"Всего элементов: {vfs.count_elements()}")
    return True


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "vfs-info": cmd_vfs_info,
}


def execute_command(command, args, vfs) -> bool:
    if command == "exit":
        return True
    if command in COMMANDS:
        return COMMANDS[command](args, vfs)
    print(f"vfs: команда не найдена: {command}")
    return False


# ============================================================
#  Скрипт и REPL
# ============================================================

def run_script(script_path, vfs) -> None:
    if not os.path.isfile(script_path):
        print(f"Ошибка: стартовый скрипт не найден: {script_path}")
        sys.exit(1)

    print(f"Выполнение стартового скрипта: {script_path}\n")

    with open(script_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            print(f"vfs> {line}")
            parts = parse_command(line)
            if not parts:
                print(f"Ошибка в строке {line_num}: пустая команда")
                print("Скрипт остановлен из-за ошибки.")
                sys.exit(1)
            command = parts[0]
            args = parts[1:]
            if command == "exit":
                print("Выход из эмулятора.")
                sys.exit(0)
            if not execute_command(command, args, vfs):
                print(f"\nСкрипт остановлен из-за ошибки в строке {line_num}.")
                sys.exit(1)

    print("\nСтартовый скрипт успешно выполнен.")


def repl(vfs) -> None:
    print(f"Добро пожаловать в эмулятор оболочки. {vfs.info()}")
    print("Введите 'exit' для выхода.\n")

    while True:
        try:
            line = input("vfs> ")
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


# ============================================================
#  Точка входа
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX-подобной ОС (Вариант 18)"
    )
    parser.add_argument("--vfs", type=str, default=None,
                        help="Путь к директории с VFS")
    parser.add_argument("--script", type=str, default=None,
                        help="Путь к стартовому скрипту")
    args = parser.parse_args()

    config = EmulatorConfig(vfs_path=args.vfs, script_path=args.script)
    config.debug_print()

    vfs = VirtualFileSystem()
    if args.vfs:
        try:
            vfs.load(args.vfs)
            print(f"VFS успешно загружена: {args.vfs}")
        except Exception as e:
            print(f"Ошибка загрузки VFS: {e}")
            sys.exit(1)
    else:
        print("VFS не указана, используется пустая по умолчанию.")

    if args.script:
        run_script(args.script, vfs)

    repl(vfs)


if __name__ == "__main__":
    main()