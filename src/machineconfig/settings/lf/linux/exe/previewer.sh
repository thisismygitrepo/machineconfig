#!/bin/sh
# 🔍 File Preview Script for LF File Manager
# Uses: 
# 🖼️ chafa, viu - Image preview
# 📝 pistol - General file preview

file=$1
width="$2"
height="$3"
x="$4"
y="$5"
default_x="1920"
default_y="1080"

# 🖼️ Image File Handling
case "$file" in
  *.jpg|*.jpeg|*.png|*.gif|*.bmp)
    echo "$FIFO_UEBERZUG"
    echo "x: $x, y: $y, width: $width, height: $height"
    
    if [ -n "$x" ]; then
        echo "📐 Dimensions provided by caller, passing to viu"
        viu "$file" -x "$x" -y "$y" -w "$width" -h "$height"
        echo "✅ Finished viu"
        chafa "$file"
        echo "✅ Finished chafa"
    else 
        echo "⚠️ No dimensions provided"
        viu "$file"
    fi
    exit 0
    ;;
  *)
    # 📄 Default file preview
    pistol "$file"
    ;;
esac
