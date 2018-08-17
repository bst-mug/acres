#!/bin/bash

echo "Checking for syntax errors..."
pylint -E acres

echo "Running tests..."
pytest -q --log-level=ERROR

echo "Checking static typing..."
mypy --ignore-missing-imports acres

echo "Updating docs..."
sphinx-apidoc -fT -o docs acres > /dev/null
