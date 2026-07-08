#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1
PYTHONPATH=. .venv/bin/python -m src.main
