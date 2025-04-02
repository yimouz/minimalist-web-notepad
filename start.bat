@echo off
set FLASK_ENV=production
python -m waitress --host=0.0.0.0 --port=8082 wsgi:app