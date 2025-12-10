#!/bin/sh

set -e

if command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    PY=python
fi

$PY -m venv .

( . bin/activate
pip install -r requirements.txt )

echo -e "\nNow run:\n\
      . bin/activate\n"
