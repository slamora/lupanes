#!/bin/bash

BASE="/home/lupierra"
PROJECT_DIR="$BASE/albaranes"
PYTHON="$BASE/.virtualenvs/albaranes/bin/python"
LOG_FILE="$PROJECT_DIR/mail.log"

export PYTHONPATH="$PROJECT_DIR"
export DJANGO_SETTINGS_MODULE="proj.settings"

$PYTHON "$PROJECT_DIR/scripts/database_backup.py" >> $LOG_FILE 2>&1
