#!/bin/bash
TERMINAL_OUTPUT_PATH_RAW="/.ai/terminal/debug/terminal_output_raw.txt"
TERMINAL_OUTPUT_PATH="/.ai/terminal/debug/terminal_output.txt"
> $TERMINAL_OUTPUT_PATH
echo "New run is underway. If you are reading this message, it means the execution has not finished yet, and you will need to wait. Once done you won't see this message and you will see terminal output instead." >> $TERMINAL_OUTPUT_PATH
echo "Starting new uv run..."
COLUMNS=200 unbuffer uv run /home/alex/code/bytesense/exchanges/src/exchanges/cli/cli_binance.py b > $TERMINAL_OUTPUT_PATH_RAW 2>&1
cat $TERMINAL_OUTPUT_PATH_RAW | sed -r "s/\x1B\[[0-9;]*[mK]//g" > $TERMINAL_OUTPUT_PATH
# watchexec --watch ./.ai/terminal/command_runner.sh --watch . -e py -- bash ./.ai/terminal/command_runner.sh
