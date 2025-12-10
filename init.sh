#!/bin/sh

set -e

python -m venv .
( . bin/activate
  pip3 install -r requirements.txt )
