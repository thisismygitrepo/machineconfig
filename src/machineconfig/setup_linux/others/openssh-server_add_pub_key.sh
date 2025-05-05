#!/usr/bin/bash
#=======================================================================
# 🔑 SSH PUBLIC KEY AUTHENTICATION SETUP
#=======================================================================
# This script helps set up passwordless SSH authentication to remote Linux machines

echo """#=======================================================================
ℹ️ PASSWORDLESS SSH SETUP | Manual instructions for key deployment
#=======================================================================
"""

echo """🔐 There are two methods to copy your public key to a remote server:

📌 METHOD 1: Using ssh-copy-id (Linux clients only)
   ssh-copy-id username@hostname

📌 METHOD 2: Manual process (For Windows clients)
   Windows PowerShell command:
   type $env:USERPROFILE\.ssh\id_rsa.pub | ssh username@hostname "cat >> .ssh/authorized_keys"

📌 METHOD 3: Using SFTP (detailed below)
"""

echo """#=======================================================================
📋 MANUAL SFTP PROCESS | Step-by-step instructions
#=======================================================================

1️⃣ Connect to the server via SFTP (you'll need to enter password once):
   sftp username@hostname

2️⃣ Create .ssh directory on remote server if it doesn't exist:
   mkdir -p .ssh

3️⃣ Navigate to the .ssh directory:
   cd .ssh

4️⃣ Upload your public key:
   put /path/to/your/local/id_rsa.pub

5️⃣ Exit SFTP:
   exit

6️⃣ SSH to the server (password required this one last time):
   ssh username@hostname

7️⃣ Append the public key to authorized_keys:
   cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

8️⃣ Set proper permissions:
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh

9️⃣ Test the connection in a new terminal (should not ask for password)
"""

# Note: This script contains instructions only - you need to manually follow the steps
# replacing 'username@hostname' with your actual username and server hostname
