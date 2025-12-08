#!/bin/bash

# This script allows searching through input (stdin) using 'tv' (television)
# while showing the context around the matching line in the preview window.
#
# Usage: command | ./search_with_context.sh
# Example: hyperfine --help | ./search_with_context.sh

# set -o pipefail


# Create a temporary file to store the stdin input
TEMP_FILE=$(mktemp)
# Capture stdin to the temp file
cat > "$TEMP_FILE"
# Ensure cleanup of the temp file on exit
trap "rm -f $TEMP_FILE" EXIT

# Run tv with the following configuration:
# 1. `nl -ba -w1 -s' '`: Add line numbers to the input (e.g., "1 line content").
#    -ba: number all lines
#    -w1: width of line numbers (minimal)
#    -s' ': separator is a single space
#
# 2. `tv`: The television fuzzy finder.
#
# 3. `--preview-command`: Use `bat` to show the file content.
#    - `--color=always`: Force color output for the preview.
#    - `--highlight-line {split: :0}`: Highlight the line number extracted from the entry.
#      `{split: :0}` splits the entry by space (default) and takes the first field (index 0), which is the line number.
#    - `$TEMP_FILE`: The file to preview.
#
# 4. `--preview-offset`: Scroll the preview to the matching line.
#    - `{split: :0}`: Use the extracted line number as the offset.
#
# 5. `--source-output`: Define what `tv` outputs when an entry is selected.
#    - `{}`: Output the full entry (including the line number).
#
# 6. `cut -d' ' -f2-`: Post-process the output to remove the line number.
#    - `-d' '`: Delimiter is space.
#    - `-f2-`: Keep fields from 2 onwards (dropping the line number).

nl -ba -w1 -s' ' "$TEMP_FILE" | tv \
    --preview-command "bat --color=always --highlight-line {split: :0} $TEMP_FILE" \
    --preview-size 80 \
    --preview-offset "{split: :0}" \
    --source-output "{}" \
    | cut -d' ' -f2-
