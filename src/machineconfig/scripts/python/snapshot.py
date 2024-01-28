
from crocodile.msc.odds import capture_from_webcam
from crocodile.meta import Terminal
import argparse


def main():
    parser = argparse.ArgumentParser(description='FTP client')
    parser.add_argument("--to_text", "-t", help="Send recursively.", action="store_true")  # default is False
    args = parser.parse_args()

    img_path = capture_from_webcam(show=False, wait=False, save=True)
    if args.to_text:
        q = Terminal().run(f"cd ~/AppData/Local/Tesseract-OCR; pytesseract '{img_path}'", shell="pwsh").capture().op
        print(q)
    else:
        print(img_path)


if __name__ == '__main__':
    main()
