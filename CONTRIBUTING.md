# Contributing

Thanks for contributing to **glossina**.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Local checks

```bash
python -m glossina.cli --help
python -m py_compile glossina/*.py
```

## Pull requests

1. Create a branch from `master`.
2. Keep changes focused and include tests/checks in your PR description.
3. Open a PR with a short summary and validation output.

## Reporting bugs

Please open an issue with:
- the command you ran,
- expected vs. actual behavior,
- and sample input text (if shareable).

## License

By contributing, you agree that your contributions are licensed under the project license in `LICENSE`.
