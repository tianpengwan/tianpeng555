#!/bin/bash
set -e

# 升级pip并绕过uv环境限制
python -m pip install --upgrade pip --break-system-packages

# 安装项目依赖（核心：添加--break-system-packages）
python -m pip install -r requirements.txt --break-system-packages

# 执行Django迁移和静态文件收集
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

# 保留原有其他命令（如果有）
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
