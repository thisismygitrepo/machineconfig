# Set error action preference to stop on error, like set -e
$ErrorActionPreference = "Stop"

$JOB_NAME = "outpatient_mapping"
$REPO_ROOT = "$HOME/code/work/winter_planning/"
$CONTEXT_PATH = "$REPO_ROOT/data/outpatient_mapping/op_services.csv"
$PROMPT_PATH = "$REPO_ROOT/data/outpatient_mapping/prompt"
$AGENTS_DIR = "$REPO_ROOT/.ai/agents/$JOB_NAME"

agents create --agents crush --host docker --model x-ai/grok-4-fast:free --provider openrouter --context-path $CONTEXT_PATH --prompt-path $PROMPT_PATH --job-name $JOB_NAME --agents-dir $AGENTS_DIR
sessions balance-load "$AGENTS_DIR/layout.json" --max-thresh 6 --breaking-method moreLayouts --thresh-type number --output-path "$AGENTS_DIR/layout_balanced.json"
sessions run "$AGENTS_DIR/layout_balanced.json" --kill-upon-completion

# agents collect $AGENTS_DIR "$REPO_ROOT/.ai/agents/$JOB_NAME/collected.txt"