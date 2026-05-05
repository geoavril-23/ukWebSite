#!/bin/bash

echo "BUILD START"

# Installer les dépendances
python3.12 -m pip install -r requirements.txt

# Collecter les fichiers statiques
python3.12 manage.py collectstatic --noinput --clear

echo "BUILD END"
