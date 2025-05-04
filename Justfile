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
  rm dist/*
  rmdir dist
  rm image_snip.egg-info/*
  rmdir image_snip.egg-info

# Run ruff format (may change files)
@format:
  uv run ruff format

# Run ruff check
@lint:
  uv run ruff check

# Run pytest
@test:
  uv run pytest
