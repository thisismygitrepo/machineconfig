
#!/bin/bash

# Configuration variables
IMAGE_NAME="gemini-cli:latest"
LOCAL_REPO_PATH="$HOME/code/machineconfig"
CONTAINER_REPO_PATH="/workspace/machineconfig"

# Default script (can be overridden)

DEFAULT_SCRIPT_PATH=".ai/tmp_prompts/ylL4BHKfdW/agent2_cmd.sh"
SCRIPT_TO_RUN_HOST="$LOCAL_REPO_PATH/$DEFAULT_SCRIPT_PATH"
SCRIPT_TO_RUN_CONTAINER="$CONTAINER_REPO_PATH/$DEFAULT_SCRIPT_PATH"

# Function to run Docker container with repo mounted and script execution
run_container_with_script() {
    local mode=${1:-"attach"}  # Options: attach, copy, interactive
    local script_path=${2:-"$DEFAULT_SCRIPT_PATH"}  # Script to run (relative to repo root)
    
    # Update script paths if custom script provided
    if [ "$script_path" != "$DEFAULT_SCRIPT_PATH" ]; then
        SCRIPT_TO_RUN_HOST="$LOCAL_REPO_PATH/$script_path"
        SCRIPT_TO_RUN_CONTAINER="$CONTAINER_REPO_PATH/$script_path"
    fi
    
    echo "🐳 Starting Docker container with machineconfig repo..."
    echo "📁 Local repo: $LOCAL_REPO_PATH"
    echo "📁 Container path: $CONTAINER_REPO_PATH"
    echo "📜 Script to run (host): $SCRIPT_TO_RUN_HOST"
    echo "📜 Script to run (container): $SCRIPT_TO_RUN_CONTAINER"
    echo "🔧 Mode: $mode"
    
    case $mode in
        "attach"|"mount")
            # Mount the repo directory (recommended - changes persist)
            echo "📎 Mounting repo directory (changes will persist)..."
            docker run -it --rm \
                -v "$LOCAL_REPO_PATH:$CONTAINER_REPO_PATH" \
                -w "$CONTAINER_REPO_PATH" \
                "$IMAGE_NAME" \
                bash -c "
                    echo '🚀 Container started with mounted repo'
                    echo '📍 Current directory: \$(pwd)'
                    echo '📂 Contents:'
                    ls -la
                    echo ''
                    if [ -f '$SCRIPT_TO_RUN_CONTAINER' ]; then
                        echo '▶️  Executing script: $SCRIPT_TO_RUN_CONTAINER'
                        chmod +x '$SCRIPT_TO_RUN_CONTAINER'
                        
                        # Create a wrapper script that fixes path issues
                        cat > /tmp/script_wrapper.sh << 'EOF'
#!/bin/bash
# Wrapper script to fix path references
ORIGINAL_SCRIPT='$SCRIPT_TO_RUN_CONTAINER'
echo \"🔧 Fixing path references in script...\"
# Replace host paths with container paths in the script execution
sed 's|/home/alex/code/machineconfig|/workspace/machineconfig|g' \"\$ORIGINAL_SCRIPT\" > /tmp/fixed_script.sh
chmod +x /tmp/fixed_script.sh
echo \"▶️  Running fixed script...\"
/tmp/fixed_script.sh
EOF
                        chmod +x /tmp/script_wrapper.sh
                        /tmp/script_wrapper.sh
                        script_exit_code=\$?
                        echo ''
                        echo '✅ Script execution completed with exit code: \$script_exit_code'
                        echo '💡 Container will remain running for interaction...'
                        exec bash
                    else
                        echo '❌ Script not found: $SCRIPT_TO_RUN_CONTAINER'
                        echo '💡 Available scripts in .ai/tmp_prompts/:'
                        find '$CONTAINER_REPO_PATH/.ai/tmp_prompts' -name '*.sh' 2>/dev/null || echo 'No .ai/tmp_prompts directory found'
                        echo '💡 Dropping to interactive shell...'
                        exec bash
                    fi
                "
            ;;
        "copy")
            # Copy repo into container (changes don't persist)
            echo "📋 Copying repo into container (changes will NOT persist)..."
            docker run -it --rm \
                "$IMAGE_NAME" \
                bash -c "
                    echo '🚀 Container started, copying repo...'
                    mkdir -p '$CONTAINER_REPO_PATH'
                    echo '📥 Repo will be copied by Docker...'
                    echo '💡 Dropping to interactive shell...'
                    exec bash
                " &
            
            # Copy files to the running container
            CONTAINER_ID=$(docker ps -q --filter ancestor="$IMAGE_NAME" | head -n1)
            if [ -n "$CONTAINER_ID" ]; then
                echo "📤 Copying files to container $CONTAINER_ID..."
                docker cp "$LOCAL_REPO_PATH/." "$CONTAINER_ID:$CONTAINER_REPO_PATH/"
                docker exec -it "$CONTAINER_ID" bash -c "
                    cd '$CONTAINER_REPO_PATH'
                    if [ -f '$SCRIPT_TO_RUN_CONTAINER' ]; then
                        echo '▶️  Executing script: $SCRIPT_TO_RUN_CONTAINER'
                        chmod +x '$SCRIPT_TO_RUN_CONTAINER'
                        '$SCRIPT_TO_RUN_CONTAINER'
                        echo '✅ Script execution completed'
                    else
                        echo '❌ Script not found: $SCRIPT_TO_RUN_CONTAINER'
                    fi
                    exec bash
                "
            fi
            ;;
        "interactive")
            # Interactive mode - just mount and start shell
            echo "🖥️  Starting interactive container with mounted repo..."
            docker run -it --rm \
                -v "$LOCAL_REPO_PATH:$CONTAINER_REPO_PATH" \
                -w "$CONTAINER_REPO_PATH" \
                "$IMAGE_NAME" \
                bash
            ;;
        *)
            echo "❌ Unknown mode: $mode"
            echo "Available modes: attach, copy, interactive"
            return 1
            ;;
    esac
}

# Function to build the image if it doesn't exist
ensure_image_exists() {
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        echo "🔨 Image $IMAGE_NAME not found. Building it..."
        docker build -f containers/gemini-cli-container -t "$IMAGE_NAME" .
    else
        echo "✅ Image $IMAGE_NAME already exists"
    fi
}

# Main execution
show_usage() {
    echo "🚀 Docker Container Launcher"
    echo "============================"
    echo ""
    echo "Usage: $0 [mode] [script_path]"
    echo ""
    echo "Modes:"
    echo "  attach       - Mount repo (changes persist) [default]"
    echo "  copy         - Copy repo (changes don't persist)"
    echo "  interactive  - Just interactive shell"
    echo ""
    echo "Script path (optional):"
    echo "  Relative path from repo root (e.g., '.ai/tmp_prompts/ylL4BHKfdW/agent0_cmd.sh')"
    echo "  Default: $DEFAULT_SCRIPT_PATH"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Default: attach mode with default script"
    echo "  $0 attach                             # Attach mode with default script"
    echo "  $0 interactive                        # Just shell access"
    echo "  $0 attach .ai/tmp_prompts/ylL4BHKfdW/agent1_cmd.sh  # Run different script"
    echo ""
}

# Check for help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

echo "🚀 Docker Container Launcher"
echo "============================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Ensure image exists
ensure_image_exists

# Run the container (default to attach mode)
MODE=${1:-"attach"}
SCRIPT_PATH=${2:-""}
run_container_with_script "$MODE" "$SCRIPT_PATH"
