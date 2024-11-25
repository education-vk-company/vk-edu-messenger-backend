#!/bin/bash

pip freeze > before.txt
python3 -m pip install black isort
python3 -m black . --line-length 79 --exclude '(^|/)(tests?|migrations?|venv)/'
python3 -m isort . --line-length 79 --profile black --skip-glob '**/migrations/*'
python3 -m pip uninstall -y black isort
pip freeze > after.txt
comm -13 <(sort before.txt) <(sort after.txt) | xargs python3 -m pip uninstall -y
rm before.txt after.txt
