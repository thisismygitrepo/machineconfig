#!/bin/sh
# previwers: bat
# chafa, viu
# from https://github.com/gokcehan/lf/wiki/Previews


# if [ $# -eq 0 ]; then
#     echo "No arguments provided"
#     exit 1
# fi

# if ! [ -f "$1" ] && ! [ -h "$1" ]; then
#   exit
# fi


file=$1
width="$2"
height="$3"
x="$4"
y="$5"
default_x="1920"
default_y="1080"


# if [[ "$( file -Lb --mime-type "$file")" =~ ^image ]]; then
#     viu "$file"
#     exit 1
# fi

case "$file" in
  *.jpg|*.jpeg|*.png|*.gif|*.bmp)
    # chafa -f sixel -s "$2x$3" --animate off --polite on "$file"
    echo "$FIFO_UEBERZUG"
    echo "x: $x, y: $y, width: $width, height: $height"
    
    # if $x is not empty string:
    if [ -n "$x" ]; then
        echo "Dimensions provided"
        viu "$file" -x "$x" -y "$y" -w "$width" -h "$height"
        echo "Finished viu"
        chafa "$file"
        echo "Finished chafa"
    else 
        echo "No dimensions provided"
        viu "$file"
    fi
    exit 0
    ;;

#   *.md)
#     glow "$file"
#     exit 0
#     ;;
  *)

esac

# case "$(file -Lb --mime-type -- "$1")" in
#     image/*)
#         chafa -f sixel -s "$2x$3" --animate off --polite on "$1"
#         exit 1
#         ;;
#     *)
#         pistol "$file"
#         ;;
# esac

pistol "$file"
