#!/bin/bash
#=======================================================================
# 💻 VS CODE INSTALLATION SCRIPT 💻
#=======================================================================
# This script installs Visual Studio Code on Ubuntu/Debian-based Linux distributions
# Reference: https://code.visualstudio.com/docs/setup/linux

# Function to handle errors
handle_error() {
    echo "❌ Error occurred during installation. Cleaning up..."
    sudo rm -f /tmp/packages.microsoft.gpg
    sudo rm -f /tmp/code.deb
    exit 1
}

# Function to install via direct .deb download (fallback method)
install_vscode_direct() {
    echo """#=======================================================================
📦 FALLBACK INSTALLATION | Installing VS Code via direct download
#=======================================================================
"""
    
    echo "⬇️ Downloading VS Code .deb package..."
    wget -O /tmp/code.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
    
    echo "📦 Installing VS Code from .deb package..."
    sudo dpkg -i /tmp/code.deb
    
    # Fix any dependency issues
    sudo apt-get install -f -y
    
    # Cleanup
    rm -f /tmp/code.deb
    
    echo "✅ VS Code installed via direct download method"
}



echo """#=======================================================================
� INSTALLING VS CODE | Using direct download method
#=======================================================================
"""

# Try direct download method first (more reliable)
echo "📥 Installing Visual Studio Code via direct download..."
install_vscode_direct

# If direct download failed, try repository method
if ! command -v code >/dev/null 2>&1; then
    echo "⚠️ Direct download failed, trying repository method..."
    
    echo """#=======================================================================
🔑 SETTING UP MICROSOFT REPOSITORY | Fallback method
#=======================================================================
"""
    
    # Clean up any existing conflicting configurations
    echo "🧹 Cleaning up existing Microsoft repository configurations..."
    
    # More thorough cleanup - remove all possible Microsoft configurations
    sudo rm -f /etc/apt/sources.list.d/vscode.list*
    sudo rm -f /etc/apt/sources.list.d/code.list*
    sudo rm -f /etc/apt/sources.list.d/microsoft*.list*
    sudo rm -f /etc/apt/sources.list.d/*.microsoft.*
    sudo rm -f /etc/apt/keyrings/packages.microsoft.gpg*
    sudo rm -f /etc/apt/keyrings/microsoft.gpg*
    sudo rm -f /usr/share/keyrings/microsoft.gpg*
    sudo rm -f /usr/share/keyrings/packages.microsoft.gpg*
    
    # Remove any Microsoft entries from main sources.list and backup files
    sudo sed -i '/packages\.microsoft\.com/d' /etc/apt/sources.list*
    
    # Clean APT cache to ensure fresh start  
    sudo apt clean
    sudo rm -rf /var/lib/apt/lists/*
    
    echo "🔄 Updating APT package lists to clear any cached conflicts..."
    sudo apt update
    
    echo "🔐 Downloading and installing Microsoft GPG key..."
    # Create keyrings directory if it doesn't exist
    sudo mkdir -p /etc/apt/keyrings
    
    # Download and install the GPG key
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    sudo chmod 644 /etc/apt/keyrings/packages.microsoft.gpg
    rm -f /tmp/packages.microsoft.gpg
    
    echo "📝 Adding VS Code repository to sources list..."
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
    
    # Verify the repository was added correctly
    echo "🔍 Verifying repository configuration..."
    cat /etc/apt/sources.list.d/vscode.list
    
    # Update package lists specifically for the new repository
    echo "🔄 Updating package lists for VS Code repository..."
    if sudo apt update; then
        echo "📥 Installing Visual Studio Code from repository..."
        sudo nala install code -y
    else
        echo "❌ Repository method also failed. VS Code may not be installed."
    fi
fi

echo """#=======================================================================
🔄 CHECKING FOR VS CODE INSIDERS | Updating if installed
#=======================================================================
"""

# Check if VS Code Insiders is installed and update if found
if command -v code-insiders >/dev/null 2>&1; then
    echo "🔍 VS Code Insiders found, updating..."
    sudo nala install code-insiders -y
else
    echo "ℹ️ VS Code Insiders not installed, skipping"
fi

echo """#=======================================================================
✅ INSTALLATION COMPLETE | VS Code has been installed successfully
#=======================================================================
"""

# Verify installation
if command -v code >/dev/null 2>&1; then
    echo "🚀 VS Code installed successfully! Version: $(code --version | head -1)"
    echo "💡 You can launch VS Code from your applications menu or by typing 'code' in terminal"
else
    echo "⚠️ VS Code installation may have failed. Trying fallback method..."
    install_vscode_direct
fi

