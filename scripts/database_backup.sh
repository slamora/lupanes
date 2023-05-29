export DJANGO_SETTINGS_MODULE=proj.settings
export BASE=/home/santiago/vhosts/albaranes.lupierra.es
export PYTHONPATH=$PYTHONPATH:$BASE/lupanes/
$BASE/lupanes/env/bin/python $BASE/lupanes/scripts/database_backup.py >> $BASE/database_backup.log 2>&1
