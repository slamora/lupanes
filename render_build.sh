#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
pip install -r requirements-deploy.txt

python manage.py migrate
python manage.py collectstatic --no-input
