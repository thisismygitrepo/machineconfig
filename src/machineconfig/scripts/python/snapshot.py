# def main():
#     print("\n" + "=" * 50)
#     print("📸 Welcome to the Snapshot Tool")
#     print("=" * 50 + "\n")

#     parser = argparse.ArgumentParser(description='📷 Capture snapshots using your webcam.')
#     parser.add_argument("--to_text", "-t", help="📝 Convert the snapshot to text using OCR.", action="store_true")
#     args = parser.parse_args()

#     print("📷 Capturing image from webcam...")
#     img_path = capture_from_webcam(show=False, wait=False, save=True)
#     print(f"✅ Image captured and saved at: {img_path}\n")

#     if args.to_text:
#         print("🔍 Converting image to text using Tesseract OCR...")
#         q = Terminal().run(f"cd ~/AppData/Local/Tesseract-OCR; pytesseract '{img_path}'", shell="pwsh").capture().op
#         print("📝 Extracted Text:")
#         print("-" * 50)
#         print(q)
#         print("-" * 50 + "\n")
#     else:
#         print("📂 Image saved successfully. No text extraction requested.\n")

# if __name__ == '__main__':
#     main()
