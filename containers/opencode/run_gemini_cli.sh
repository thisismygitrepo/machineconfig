# Path to prompt file inside the container (after volume mount)
PATH_PROMPT="/workspace/machineconfig/containers/prompt.txt"
#   -e "PATH_PROMPT=$PATH_PROMPT" \

docker run -it --rm \
  -v "/home/alex/code/machineconfig:/workspace/machineconfig" \
  -w "/workspace/machineconfig" \
  opencode:latest \
  opencode run "$PATH_PROMPT"
