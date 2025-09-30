# Path to prompt file inside the container (after volume mount)
PATH_PROMPT="/workspace/machineconfig/containers/prompt.txt"
#   -e "PATH_PROMPT=$PATH_PROMPT" \

docker run -it --rm \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -v "/home/alex/code/machineconfig:/workspace/machineconfig" \
  -w "/workspace/machineconfig" \
  gemini-cli:latest \
  gemini --prompt "$PATH_PROMPT"
