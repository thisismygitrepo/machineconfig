#!/bin/bash
# https://temp.sh/
# 📤 CLOUD FILE SHARING SCRIPT 📤
# This script uploads files or directories to transfer.sh for easy sharing
# Usage: share_cloud <file|directory> or command | share_cloud <file_name>

# Check if arguments are provided
if [ $# -eq 0 ]; then
    echo """        ❌ ERROR | No arguments specified
        
    📋 USAGE:
      share_cloud <file|directory>
      command | share_cloud <file_name>
    """>&2
    return 1
fi

# https://temp.sh/

# Process the input
if tty -s; then
    # Direct file/directory upload mode
    file="$1"
    file_name=$(basename "$file")
    
    # Check if the file exists
    if [ ! -e "$file" ]; then
        echo """                ❌ ERROR | File not found
                
        🔍 File \"$file\" does not exist
        """>&2
        return 1
    fi
    
    echo """        📤 UPLOADING | Sharing file to transfer.sh
        """
    
    # Handle directories by creating a zip archive
    if [ -d "$file" ]; then
        file_name="$file_name.zip"
        echo "📦 Compressing directory \"$file\" for upload..."
        (cd "$file" && zip -r -q - .) | curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name" | tee /dev/null
    else
        # Handle regular files
        echo "📄 Uploading file \"$file\"..."
        cat "$file" | curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name" | tee /dev/null
    fi
else
    # Pipe mode - reading from stdin
    file_name=$1
    echo """        📤 UPLOADING | Sharing from stdin to transfer.sh
        """
    echo "📋 Creating file \"$file_name\" from piped input..."
    curl --progress-bar --upload-file "-" "https://transfer.sh/$file_name" | tee /dev/null
    
    # Display QR code for the URL
    echo """        📱 QR CODE | Scan with mobile device to access file
        """
    qr "https://transfer.sh/$file_name"
fi

echo """✅ UPLOAD COMPLETE | File is available at the URL above
"""
echo "⚠️ NOTE: Files are automatically deleted after 14 days"
