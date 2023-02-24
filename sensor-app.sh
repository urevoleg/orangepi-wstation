#!/bin/bash
cd /root/projects/orangepi-wstation && source venv/bin/activate
gunicorn app:app -b 0.0.0.0:8080 --workers=2 --reload