#!/bin/sh
# 🔍 File Preview Script for LF File Manager
# Uses: 
# 🖼️ chafa, viu - Image preview
# 📝 bat - Syntax-highlighted text/code preview
# 📄 pistol - General file preview

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
        # echo "📐 Dimensions provided by caller, passing to viu"
        # viu "$file" -x "$x" -y "$y" -w "$width" -h "$height"
        # chafa --fit-width -f sixel "$file"
        echo "✅ Finished viu"
        chafa "$file"
        echo "✅ Finished chafa"
    else 
        echo "⚠️ No dimensions provided"
        viu "$file"
    fi
    exit 0
    ;;
  # 📝 Text/Code Files - Use bat for syntax highlighting
  *.py|*.json|*.js|*.ts|*.html|*.css|*.scss|*.less|*.xml|*.yml|*.yaml|*.toml|*.ini|*.cfg|*.conf|*.sh|*.bash|*.zsh|*.fish|*.ps1|*.rs|*.go|*.java|*.cpp|*.c|*.h|*.hpp|*.cs|*.php|*.rb|*.pl|*.pm|*.lua|*.vim|*.sql|*.md|*.txt|*.log|*.csv|*.tsv)
    bat --color=always --style=plain --paging=never "$file"
    ;;
  *)
    # 📄 Default file preview
    pistol "$file"
    ;;
esac
