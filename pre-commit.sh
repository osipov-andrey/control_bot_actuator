#!/usr/bin/env bash

python -m pytest tests || exit 1
black --config=pyproject.toml .

git add .

ln -sf ../../pre-commit.sh .git/hooks/pre-commit