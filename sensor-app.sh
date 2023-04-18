#!/bin/bash
cd ~/projects/orangepi-wstation && source venv/bin/activate
gunicorn app:app -b 0.0.0.0:5000 --workers=2 --reload