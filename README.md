# Minimize

Replace deno `-A` with the actual used flags

## Usage

`./min.py deno_file.ts`

## How it works

- It runs the file with `deno run --unstable`
- Says yes to every prompt
- Record every permission that was asked for in `/tmp/scan.out`
- Parses scan.out into a deno cli format, for example:
  `deno run --unstable --allow-read=.. --allow-write=.. deno_file.ts`
