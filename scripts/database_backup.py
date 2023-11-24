"""
#
# Author - Anurag Rana
# anuragrana31189 at gmail dot com
# place in home directory. schedule with task tab on pythonanywhere server.
# https://www.pythoncircle.com/post/360/how-to-backup-database-periodically-on-pythonanywhere-server/
#
# Adapted by Santiago Lamora
# upload to Google Drive with [gdrive](https://github.com/glotlabs/gdrive)
"""
import datetime
import django
import logging
import os
import sys
import subprocess

from zipfile import ZipFile

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


BACKUP_DIR_NAME = "/home/santiago/vhosts/albaranes.lupierra.es/backups"
DAYS_TO_KEEP_BACKUP = 30

FILE_PREFIX = "backup_"
FILE_SUFFIX_DATE_FORMAT = "%Y%m%d%H%M%S"

USERNAME = settings.DATABASES['default']['USER']
PASSWORD = settings.DATABASES['default']['PASSWORD']
DBNAME = settings.DATABASES['default']['NAME']
DBHOST = settings.DATABASES['default']['HOST']
DBPORT = settings.DATABASES['default']['PORT']


# get today's date and time
timestamp = datetime.datetime.now().strftime(FILE_SUFFIX_DATE_FORMAT)
backup_filename = os.path.join(BACKUP_DIR_NAME, FILE_PREFIX + timestamp + ".dump")

logger.info("Creating database dump:" + backup_filename)

if not os.path.exists(BACKUP_DIR_NAME):
    os.mkdir(BACKUP_DIR_NAME)


os.system("PGPASSWORD={password} pg_dump --host={hostname} --port={port} --username={username} --format=c --file={filename} {database}".format(
    hostname=DBHOST, port=DBPORT, username=USERNAME, password=PASSWORD, filename=backup_filename, database=DBNAME
))

# creating zip file
zip_filename = os.path.join(BACKUP_DIR_NAME, FILE_PREFIX + timestamp + ".zip")
with ZipFile(zip_filename, 'w') as zip:
    zip.write(backup_filename, os.path.basename(backup_filename))

logger.debug("Delete dump file '{}' after create zipfile.".format(backup_filename))
os.remove(backup_filename)

# upload backup to Google Drive
subprocess.run(["gdrive", "files", "upload", zip_filename])

# deleting old files
list_files = os.listdir(BACKUP_DIR_NAME)
keep_back_date = datetime.datetime.now() - datetime.timedelta(days=DAYS_TO_KEEP_BACKUP)

for f in list_files:
    filename, file_extension = os.path.splitext(f)
    filepath = os.path.join(BACKUP_DIR_NAME, f)

    if file_extension == 'zip' and os.stat(filepath).st_mtime < keep_back_date.timestamp():
        logger.info("Deleting file : " + f)
        os.remove(filepath)
