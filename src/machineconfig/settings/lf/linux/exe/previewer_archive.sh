#!/bin/sh
# 📦 Archive and File Preview Script for LF File Manager

# 🎨 Image Drawing Function for Ueberzug
draw() {
  path="$(printf '%s' "$1" | sed 's/\\/\\\\/g;s/"/\\"/g')"
  printf '{"action": "add", "identifier": "preview", "x": %d, "y": %d, "width": %d, "height": %d, "scaler": "contain", "scaling_position_x": 0.5, "scaling_position_y": 0.5, "path": "%s"}\n' \
    "$x" "$y" "$width" "$height" "$path" >"$FIFO_UEBERZUG"
  exit 1
}

# 🗄️ Cache Management Functions
hash() {
  printf '%s/.cache/lf/%s' "$HOME" \
    "$(stat --printf '%n\0%i\0%F\0%s\0%W\0%Y' -- "$(readlink -f "$1")" | sha256sum | awk '{print $1}')"
}

cache() {
  if [ -f "$1" ]; then
    draw "$1"
  fi
}

# ⚡ Main Preview Logic
if ! [ -f "$1" ] && ! [ -h "$1" ]; then
  exit
fi

width="$2"
height="$3"
x="$4"
y="$5"
default_x="1920"
default_y="1080"

# 📂 File Type Handling
case "$1" in
  # 📦 Archive Files
  *.7z|*.a|*.ace|*.alz|*.arc|*.arj|*.bz|*.bz2|*.cab|*.cpio|*.deb|*.gz|*.jar|\
  *.lha|*.lrz|*.lz|*.lzh|*.lzma|*.lzo|*.rar|*.rpm|*.rz|*.t7z|*.tar|*.tbz|\
  *.tbz2|*.tgz|*.tlz|*.txz|*.tZ|*.tzo|*.war|*.xz|*.Z|*.zip)
    als -- "$1"
    exit 0
    ;;
  # 📚 Man Pages
  *.[1-8])
    man -- "$1" | col -b
    exit 0
    ;;
  # 🖼️ Images
  *.jpg|*.jpeg|*.png|*.gif|*.bmp)
    chafa "$1"
    ;;
  # 📄 PDF Documents
  *.pdf)
    if [ -n "$FIFO_UEBERZUG" ]; then
      cache="$(hash "$1")"
      cache "$cache.jpg"
      pdftoppm -f 1 -l 1 \
        -scale-to-x "$default_x" \
        -scale-to-y -1 \
        -singlefile \
        -jpeg \
        -- "$1" "$cache"
      draw "$cache.jpg"
    else
      pdftotext -nopgbrk -q -- "$1" -
      exit 0
    fi
    ;;
  # 📖 DJVU Documents
  *.djvu|*.djv)
    if [ -n "$FIFO_UEBERZUG" ]; then
      cache="$(hash "$1").tiff"
      cache "$cache"
      ddjvu -format=tiff -quality=90 -page=1 -size="${default_x}x${default_y}" \
        - "$cache" <"$1"
      draw "$cache"
    else
      djvutxt - <"$1"
      exit 0
    fi
    ;;
  # 📝 Office Documents
  *.docx|*.odt|*.epub)
    pandoc -s -t plain -- "$1"
    exit 0
    ;;
  # 🌐 Web Documents
  *.htm|*.html|*.xhtml)
    lynx -dump -- "$1"
    exit 0
    ;;
  # 🎨 Vector Graphics
  *.svg)
    if [ -n "$FIFO_UEBERZUG" ]; then
      cache="$(hash "$1").jpg"
      cache "$cache"
      convert -- "$1" "$cache"
      draw "$cache"
    fi
    ;;
esac

# 📋 MIME Type Based Preview
case "$(file -Lb --mime-type -- "$1")" in
  # 📝 Text Files
  text/*)
    clear
    bat --color=always --theme=base16 $1
    exit 0
    ;;
  # 🖼️ Image Files
  image/*)
    if [ -n "$FIFO_UEBERZUG" ]; then
      orientation="$(identify -format '%[EXIF:Orientation]\n' -- "$1")"
      if [ -n "$orientation" ] && [ "$orientation" != 1 ]; then
        cache="$(hash "$1").jpg"
        cache "$cache"
        convert -- "$1" -auto-orient "$cache"
        draw "$cache"
      else
        draw "$1"
      fi
    fi
    ;;
  # 🎥 Video Files
  video/*)
    if [ -n "$FIFO_UEBERZUG" ]; then
      cache="$(hash "$1").jpg"
      cache "$cache"
      ffmpegthumbnailer -i "$1" -o "$cache" -s 0
      draw "$cache"
    fi
    ;;
esac

# 📊 File Info Header
header_text="File Type Classification"
header=""
len="$(( (width - (${#header_text} + 2)) / 2 ))"
if [ "$len" -gt 0 ]; then
  for i in $(seq "$len"); do
    header="-$header"
  done
  header="$header $header_text "
  for i in $(seq "$len"); do
    header="$header-"
  done
else
  header="$header_text"
fi
printf '\033[7m%s\033[0m\n' "$header"
file -Lb -- "$1" | fold -s -w "$width"
exit 0
