
#!/bin/bash
# set -e # Exit immediately if a command exits with a non-zero status.

JOB_NAME="outpatient_mapping"
REPO_ROOT="$HOME/code/machineconfig"
CONTEXT_PATH="$REPO_ROOT/.ai/todo/files.md"
# agents make-todo --strategy keywords from machineconfig.utils.path_extended import PathExtended
PROMPT_PATH="$REPO_ROOT/src/machineconfig/scripts/python/helpers_agents/templates/prompt.txt"
AGENTS_DIR="$REPO_ROOT/.ai/agents/$JOB_NAME"

agents create --agents crush \
    --host docker \
    --model x-ai/grok-4-fast:free \
    --provider openrouter \
    --context-path $CONTEXT_PATH \
    --prompt-path $PROMPT_PATH \
    --job-name $JOB_NAME \
    --agents-dir $AGENTS_DIR
sessions balance-load "$AGENTS_DIR/layout.json" --max-thresh 6 --breaking-method moreLayouts --thresh-type number --output-path "$AGENTS_DIR/layout_balanced.json"
sessions run "$AGENTS_DIR/layout_balanced.json" --kill-upon-completion


# agents collect $AGENTS_DIR "$REPO_ROOT/.ai/agents/$JOB_NAME/collected.txt"
