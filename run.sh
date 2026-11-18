#!/bin/bash
python3 ./collection/ncku_hub.py
python3 ./collection/urschool.py
git add .
git commit -m "🆗"
git push
date
