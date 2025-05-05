#!/usr/bin/bash
#=======================================================================
# 🎨 ASCII ART TOOLS INSTALLATION SCRIPT
#=======================================================================
# This script installs various ASCII art and text formatting tools

echo """#=======================================================================
🖼️  ASCII ART TOOLS | Installing terminal visualization packages
#=======================================================================
"""

# Alternate Nix installation method (commented reference)
# if [ -f "$HOME/.nix-profile/bin/nix-env" ]; then
#   echo """#   #=======================================================================
#   📦 NIX PACKAGE INSTALLATION | Using Nix package manager
#   #=======================================================================
#   """
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.cowsay || true
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.lolcat || true
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.boxes || true
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.figlet || true
# else

# Check if cowsay is installed, if not install it
if [ ! -f "/usr/games/cowsay" ]; then
  echo """  #=======================================================================
  🐮 INSTALLING COWSAY | ASCII art animals with speech bubbles
  #=======================================================================
  
  📋 Usage examples:
     $ cowsay "Hello World"
     $ cowsay -l (to list available figures)
     $ cowsay -f tux "Linux rocks!"
  """
  sudo nala install cowsay -y || true
fi

# Check if lolcat is installed, if not install it
if [ ! -f "/usr/games/lolcat" ]; then
  echo """  #=======================================================================
  🌈 INSTALLING LOLCAT | Rainbow text colorizer for terminal
  #=======================================================================
  
  📋 Usage examples:
     $ echo "Hello World" | lolcat
     $ cowsay "Rainbow cow" | lolcat
  """
  sudo nala install lolcat -y || true
fi

# Check if boxes is installed, if not install it
if [ ! -f "/usr/bin/boxes" ]; then
  echo """  #=======================================================================
  📦 INSTALLING BOXES | ASCII art box drawing around text
  #=======================================================================
  
  📋 Usage examples:
     $ echo "Hello World" | boxes
     $ echo "Custom box" | boxes -d stone
     $ boxes -l (to list available box styles)
  """
  sudo nala install boxes -y || true
fi

# Check if figlet is installed, if not install it
if [ ! -f "/usr/bin/figlet" ]; then
  echo """  #=======================================================================
  📝 INSTALLING FIGLET | Large ASCII text generator
  #=======================================================================
  
  📋 Usage examples:
     $ figlet "Hello World"
     $ showfigfonts (to view available fonts)
     $ figlet -f slant "Custom font"
  """
  sudo nala install figlet -y || true
fi

echo """#=======================================================================
✅ INSTALLATION COMPLETE | All ASCII art tools installed successfully
#=======================================================================

🎨 Installed tools:
   ✓ cowsay - ASCII art animals with text
   ✓ lolcat - Rainbow text colorizer
   ✓ boxes  - Text in ASCII art boxes
   ✓ figlet - Large ASCII text generator

💡 Try combining them:
   $ figlet "Cool text" | boxes | lolcat
   $ cowsay -f tux "Linux" | lolcat
"""
# fi
