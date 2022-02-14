#!/bin/bash
python3 manage.py check
gunicorn -b :8000 -w 2 --enable-stdio-inheritance --error-logfile '-' --access-logfile '-' --capture-output --log-level info root.wsgi
