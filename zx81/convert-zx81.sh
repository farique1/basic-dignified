#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    printf 'Usage: %s <program-name-without-extension>\n' "$0" >&2
    exit 2
fi

program_name=$1
if [[ "$program_name" =~ \.[dD][zZ][xX]$ ]]; then
    program_name=${program_name%.*}
fi
source_file="${program_name}.DZX"

if [[ ! -f "$source_file" ]]; then
    printf 'ZX-81 source not found: %s\n' "$source_file" >&2
    exit 1
fi

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_directory/.." && pwd)"
badig_path="$repository_root/badig.py"
python=${PYTHON:-python3}

"$python" "$badig_path" "$source_file" -id zx81 --tk_tokenize

ascii_file="${source_file%.*}.AZX"
program_file="${source_file%.*}.p"
if [[ ! -f "$ascii_file" ]]; then
    printf 'Numbered ASCII output not found: %s\n' "$ascii_file" >&2
    exit 1
fi
if [[ ! -f "$program_file" ]]; then
    printf 'Tokenized output not found: %s\n' "$program_file" >&2
    exit 1
fi

printf 'Created %s\n' "$ascii_file"
printf 'Created %s\n' "$program_file"