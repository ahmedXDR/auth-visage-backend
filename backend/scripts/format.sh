#!/usr/bin/env bash
set -x

uv run ruff check app scripts tests --fix
uv run ruff format app scripts tests
