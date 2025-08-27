#!/bin/bash
cd "$(dirname "$0")"

source .venv/bin/activate
python main.py --log info 2>>error-log.txt
read
