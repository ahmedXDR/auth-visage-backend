#!/usr/bin/env bash

set -e
set -x

uv run mypy app                # type check
uv run ruff check app tests    # linter
uv run ruff format app --check # formatter
