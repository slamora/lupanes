#!/bin/bash

# Crontab script to run post_office's send_queued_mail
# It logs output to a file with 7-day rotation.

# --- Configuration ---
HOME_DIR="/home/lupierra"
PROJECT_DIR="$HOME_DIR/albaranes"
VENV_PYTHON="$HOME_DIR/.virtualenvs/albaranes/bin/python"

# --- Log Management (7-day rotation) ---
DATE_STAMP=$(date +%Y-%m-%d)
LOG_FILE="$PROJECT_DIR/mail_$DATE_STAMP.log"

# Delete logs older than 7 days
find "$PROJECT_DIR" -name "mail_*.log" -type f -mtime +7 -delete

# --- Execution ---
$VENV_PYTHON "$PROJECT_DIR/manage.py" send_queued_mail --log-level 1 >> "$LOG_FILE" 2>&1
STATUS=$?

# --- Error Handling via Django's SMTP ---
if [ $STATUS -ne 0 ]; then
    # Use our new python script to send the alert using your .env credentials
    $VENV_PYTHON "$PROJECT_DIR/send_alert.py" "$LOG_FILE"
fi
