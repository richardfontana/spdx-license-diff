# Development Guide

## Architecture

- `glossina/cli.py`: CLI argument parsing and output formatting.
- `glossina/spdx_client.py`: SPDX corpus download + normalization.
- `glossina/matcher.py`: text normalization, scoring, and ranking.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m glossina.cli --help
```

## Packaging

`pyproject.toml` defines the package metadata and installs the `glossina` executable.
