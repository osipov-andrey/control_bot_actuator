#!/usr/bin/env bash

python -m pytest tests
black --config=pyproject.toml .

git add .

ln -sf ../../pre-commit.sh .git/hooks/pre-commit