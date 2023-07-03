# Minimize

Replace deno `-A` with the actual used flags

## Dependencies

- `pip install semver`
- `pip install ptyprocess`

## Usage

`./min.py deno_file.ts`

<img src="https://cdn.discordapp.com/attachments/712010403302866974/1007952292361818212/min.gif"/>

## How it works

- It runs the file with `deno run`
- Says yes to every prompt
- Record every permission that was asked for in `/tmp/scan.out`
- Parses `scan.out` into a deno cli format, for example:
  `deno run --unstable --allow-read=.. --allow-write=.. deno_file.ts`

## Why in python

Waiting for https://github.com/denoland/deno/issues/3994

**Update:**

There is a deno version now: https://github.com/sigmaSd/Minimize-Deno
