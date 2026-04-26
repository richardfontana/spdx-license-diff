# Testing

Current lightweight checks:

```bash
python -m py_compile glossina/*.py
python -m glossina.cli --help
```

For an end-to-end check (requires network access to `spdx.org`):

```bash
python -m glossina.cli --text "Permission is hereby granted" --top 3
```
