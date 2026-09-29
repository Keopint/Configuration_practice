#!/bin/bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8
# Тестирование всех поддерживаемых параметров командной строки эмулятора.
# Вариант 18.

echo "=== Запуск эмулятора без параметров ==="
winpty python3 main.py

echo ""
echo "=== Запуск с указанием VFS ==="
winpty python3 main.py --vfs ./my_vfs.json

echo ""
echo "=== Запуск со стартовым скриптом ==="
winpty  main.py --script start_scripts/basic_commands.txt

echo ""
echo "=== Запуск с обоими параметрами ==="
winpty python3 main.py --vfs ./my_vfs.json --script start_scripts/basic_commands.txt

echo ""
echo "=== Запуск эмулятора без параметров ==="
winpty python3 main.py