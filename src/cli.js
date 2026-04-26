#!/usr/bin/env node
// SPDX-FileCopyrightText: SPDX-License-Diff contributors
// SPDX-License-Identifier: GPL-3.0-or-later

import fs from 'node:fs/promises';
import process from 'node:process';
import { downloadSpdxCorpus } from './spdx-client.js';
import { rankMatches } from './matcher.js';

function printHelp() {
  console.log(`spdx-license-diff-cli

Compare pasted text against the SPDX License List.

Usage:
  spdx-license-diff [options]

Options:
  -t, --text <value>       Text input to compare directly
  -f, --file <path>        Read text input from a file
  --top <n>                Number of matches to return (default: 10)
  --min-score <n>          Minimum score threshold 0-100 (default: 25)
  --no-exceptions          Skip SPDX exceptions
  --json                   Output JSON
  -h, --help               Show help

Input behavior:
  If --text and --file are omitted, the command reads from stdin.
  Example: pbpaste | spdx-license-diff --top 5
`);
}

function parseArgs(argv) {
  const options = {
    top: 10,
    minScore: 25,
    includeExceptions: true,
    json: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === '-h' || arg === '--help') {
      options.help = true;
    } else if (arg === '-t' || arg === '--text') {
      options.text = argv[++i];
    } else if (arg === '-f' || arg === '--file') {
      options.file = argv[++i];
    } else if (arg === '--top') {
      options.top = Number(argv[++i]);
    } else if (arg === '--min-score') {
      options.minScore = Number(argv[++i]);
    } else if (arg === '--no-exceptions') {
      options.includeExceptions = false;
    } else if (arg === '--json') {
      options.json = true;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!Number.isFinite(options.top) || options.top < 1) {
    throw new Error('--top must be a positive number');
  }

  if (!Number.isFinite(options.minScore) || options.minScore < 0 || options.minScore > 100) {
    throw new Error('--min-score must be between 0 and 100');
  }

  return options;
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

async function resolveInput(options) {
  if (options.text) {
    return options.text;
  }

  if (options.file) {
    return fs.readFile(options.file, 'utf8');
  }

  if (process.stdin.isTTY) {
    throw new Error('No input detected. Pipe text to stdin, or use --text/--file.');
  }

  return readStdin();
}

function printTable(matches) {
  if (matches.length === 0) {
    console.log('No matches found for the configured threshold.');
    return;
  }

  for (const [index, match] of matches.entries()) {
    console.log(`${index + 1}. ${match.id} (${match.category})`);
    console.log(`   Name: ${match.name}`);
    console.log(`   Score: ${match.score.toFixed(2)} | Dice: ${match.dice.toFixed(2)} | Levenshtein: ${match.levPercent.toFixed(2)}`);
    console.log(`   Reference: ${match.reference}`);
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    printHelp();
    return;
  }

  const inputText = await resolveInput(options);

  const corpus = await downloadSpdxCorpus({
    includeExceptions: options.includeExceptions
  });

  const matches = rankMatches(inputText, corpus, {
    top: options.top,
    minScore: options.minScore
  });

  if (options.json) {
    console.log(JSON.stringify(matches, null, 2));
    return;
  }

  printTable(matches);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
