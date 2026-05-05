#!/bin/bash
pip install -r requirements.txt
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
