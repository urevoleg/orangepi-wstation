#!/bin/bash
cd ~/projects/orangepi-wstation && source venv/bin/activate
gunicorn app:app -b 0.0.0.0:8880 --workers=2 --reload