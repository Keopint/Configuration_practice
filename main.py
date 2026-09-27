
"""
Эмулятор командной оболочки UNIX-подобной ОС.
Этап 1: REPL (Read-Eval-Print Loop).
Вариант 18.
"""

from VirtualFileSystem import VirtualFileSystem
from Prac1 import repl_one

def startVFS(number) -> None:
    vfs = VirtualFileSystem(name=str(number))
    if number == 1:
        repl_one(vfs)

if __name__ == "__main__":
    number = int(input("Введите номер VFS: "))
    startVFS(number)