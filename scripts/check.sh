#!/bin/bash

echo "Checking for syntax errors..."
pylint -E acres

echo "Checking for pylint warnings..."
pylint -d R,C acres

echo "Running tests..."
pytest -q --log-level=ERROR

echo "Checking static typing..."
mypy --strict --ignore-missing-imports acres

echo "Updating docs..."
sphinx-apidoc -fT -o docs acres > /dev/null

echo "Generating docs..."
sphinx-build -W -b html docs/ docs/_build/ > /dev/null
