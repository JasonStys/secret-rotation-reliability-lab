#!/usr/bin/env bash
# Jason Stys: strict portable tests and maintained source/documentation contracts; no Actions storage uploads.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# END CODE MAP
set -euo pipefail
python -m ruff check rotation scripts tests
python -m ruff format --check rotation scripts tests
python -m mypy
python -m pytest --cov --cov-report=term-missing --tb=short
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python -m scripts.benchmark
