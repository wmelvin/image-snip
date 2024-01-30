@default:
  @just --list

# Run test, lint, check, pyproject-build
@build: test lint check
  pipenv run pyproject-build

# Run ruff format --check
@check:
  pipenv run ruff format --check

# Run check, lint, pipenv check
@checks: check lint
  pipenv check

# Remove dist and egg-info
@clean:
  rm dist/*
  rmdir dist
  rm image_snip.egg-info/*
  rmdir image_snip.egg-info

# Run ruff format (may change files)
@format:
  pipenv run ruff format

# Run ruff check
@lint:
  pipenv run ruff check

# Run pytest
@test:
  pipenv run pytest
