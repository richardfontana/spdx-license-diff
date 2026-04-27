# Testing

Run the unit test suite:

```bash
python -m unittest discover -s tests -v
```

Additional lightweight checks:

```bash
python -m py_compile glossina/*.py
python -m glossina.cli --help
```

For an end-to-end check (requires network access to `spdx.org`):

```bash
python -m glossina.cli --text "Permission is hereby granted" --top 3
```
