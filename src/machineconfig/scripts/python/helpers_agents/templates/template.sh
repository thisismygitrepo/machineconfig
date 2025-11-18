
#!/bin/bash
# set -e # Exit immediately if a command exits with a non-zero status.


REPO_ROOT="$HOME/code/machineconfig"

JOB_NAME="agentsTrial"
CONTEXT_PATH="$REPO_ROOT/.ai/agents/files.md"
PROMPT_PATH="$REPO_ROOT/.ai/agents/prompt.txt"
AGENTS_DIR="$REPO_ROOT/.ai/agents/$JOB_NAME"
rm -rfd "$AGENTS_DIR" || true

agents create \
    --agents gemini \
    --host docker \
    --model gemini-2.5-pro \
    --provider google \
    --agent-load 5 \
    --context-path $CONTEXT_PATH \
    --prompt-path $PROMPT_PATH \
    --job-name $JOB_NAME \
    --agents-dir $AGENTS_DIR

sessions balance-load "$AGENTS_DIR/layout.json" \
    --max-threshold 4 \
    --breaking-method moreLayouts \
    --threshold-type number \
    --output-path "$AGENTS_DIR/layout_balanced.json"

sessions run "$AGENTS_DIR/layout_balanced.json" --kill-upon-completion


# agents collect $AGENTS_DIR "$REPO_ROOT/.ai/agents/$JOB_NAME/collected.txt"
