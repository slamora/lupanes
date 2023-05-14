# Lupanes

Herramienta para gestionar los albaranes de la asociación Lupierra.


1. Clone this repository
```sh
git clone git@github.com:slamora/lupanes.git lupanes
```

2. Prepare python environment
```sh
cd lupanes
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt

```

3. Copy and update project settings via `.env` file
```sh
cp .env.example .env

# open .env with your favourite editor
vim .env
```

NOTE: you can generate a secure random private key by running
```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. Install development tools (precommit)
```sh
# with virtual environment active
pip install -r requirements-dev.txt
pre-commit install
```

## postgres - prepare your database
Prepare your PostGres database (create database, user and grant permissions):

```sh
sudo su - postgres
psql
```

```sql
CREATE DATABASE albaranes;
CREATE USER lupierra WITH PASSWORD 'VerYs3cretP4$$';
GRANT ALL PRIVILEGES ON DATABASE albaranes TO lupierra;
```
