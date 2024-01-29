@default:
  @just --list

# test lint check pyproject-build
@build: test lint check
  pipenv run pyproject-build

# ruff format --check
@check:
  pipenv run ruff format --check

# Remove dist and egg-info
@clean:
  rm dist/*
  rmdir dist
  rm image_snip.egg-info/*
  rmdir image_snip.egg-info

# ruff format
@format:
  pipenv run ruff format

# ruff check
@lint:
  pipenv run ruff check

# pytest
@test:
  pipenv run pytest
