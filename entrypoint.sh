#!/bin/bash

uvicorn app:app --host 0.0.0.0 --port 7860 &
python main.py

wait

#entrypoint.sh