# Path to prompt file inside the container (after volume mount)
PATH_PROMPT="/workspace/machineconfig/containers/prompt.txt"
docker run -it --rm \
  -e "GEMINI_API_KEY=" \
#   -e "PATH_PROMPT=$PATH_PROMPT" \
  -v "/home/alex/code/machineconfig:/workspace/machineconfig" \
  -w "/workspace/machineconfig" \
  gemini-cli:latest \
  gemini --prompt "$PATH_PROMPT"
