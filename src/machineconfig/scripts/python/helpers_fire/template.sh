
#!/bin/bash
# set -e # Exit immediately if a command exits with a non-zero status.

JOB_NAME="outpatient_mapping"
REPO_ROOT="$HOME/code/ machineconfig"
CONTEXT_PATH="$REPO_ROOT/src/machineconfig/scripts/python/fire_jobs.py"
PROMPT_PATH="$REPO_ROOT/src/machineconfig/scripts/python/helpers_fire/prompt.txt"

AGENTS_DIR="$REPO_ROOT/.ai/agents/$JOB_NAME"
LAYOUT_PATH_UNBALANCED="$REPO_ROOT/.ai/agents/$JOB_NAME/layout_unbalanced.json"

# agents make-todo --output-path $CONTEXT_PATH
ag create \
  --context-path "$CONTEXT_PATH" \
  --tasks-per-prompt 1 \
  --machine docker \
  --agent crush \
  --model "zai/glm-4.6" \
  --provider openrouter \
  --separator 'def ' \
  --prompt-path "$PROMPT_PATH" \
  --output-path "$LAYOUT_PATH_UNBALANCED" \
  --agents-dir "$AGENTS_DIR"

# LAYOUT_BALANCED_PATH="$REPO_ROOT/.ai/agents/$JOB_NAME/layout_balanced.json"
# sessions balance-load $LAYOUT_PATH --max-thresh 6 --breaking-method moreLayouts --thresh-type number  --output-path $LAYOUT_BALANCED_PATH
# sessions run $LAYOUT_BALANCED_PATH --kill-upon-completion

ses run $LAYOUT_PATH_UNBALANCED

# agents collect $AGENTS_DIR "$REPO_ROOT/.ai/agents/$JOB_NAME/collected.txt"
