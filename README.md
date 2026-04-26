# glossina 

A command line tool that compares user-provided text against SPDX licenses and exceptions, then reports the best matches.

## Install

```bash
yarn install
```

## Usage

```bash
yarn start -- --text "Permission is hereby granted, free of charge..."
```

You can also pipe text:

```bash
cat LICENSE | yarn start -- --top 5
```

Or read from a file:

```bash
yarn start -- --file ./LICENSE --json
```

## Options

- `--text <value>`: Input text directly
- `--file <path>`: Read input text from a file
- `--top <n>`: Number of matches to return (default: `10`)
- `--min-score <n>`: Minimum score threshold from `0` to `100` (default: `25`)
- `--no-exceptions`: Exclude SPDX exception texts from matching
- `--json`: Emit machine-readable JSON output

## Notes

- The tool downloads SPDX data from `https://spdx.org/licenses/` at runtime.
- For reproducible/offline workflows, you can fork and extend this project with local cache support.

## Project name

This project/repo has been renamed to **glossina**.

## License

GPL-3.0-or-later.
