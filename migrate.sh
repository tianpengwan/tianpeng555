#!/bin/bash
set -e

# 升级 pip 并绕过 uv 限制
python -m pip install --upgrade pip --break-system-packages

# 安装依赖（无需额外参数）
python -m pip install -r requirements.txt --break-system-packages

# 执行 Django 迁移
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
