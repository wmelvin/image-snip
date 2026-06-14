@default:
  @just --list

# Run test, lint, check, build
@build: test lint check
  uv build

# Run ruff format --check
@check:
  uv run ruff format --check

# Run check and lint
@checks: check lint

# Remove dist and egg-info
@clean:
  -rm dist/*

# Run ruff format (may change files)
@format:
  uv run ruff format

# Redirect 'image_snip -h' to temp.txt
@help:
  uv run image_snip -h > temp.txt

# Run ruff check
@lint:
  uv run ruff check

# Write 'image_snip --template' to temp.txt
@template:
  -rm temp.txt
  uv run image_snip --template temp.txt

# Run pytest
@test:
  uv run pytest
