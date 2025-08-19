# """Convert image to text.
# """


# # import sys
# from rich.console import Console
# from rich.panel import Panel
# import pytesseract
# from PIL import Image

# console = Console()

# console.print(Panel("📸 Image to Text Converter", title="Status", expand=False))

# print("📷 Capturing image from webcam...")
# img_path = capture_from_webcam(show=False, wait=False, save=True)
# print(f"✅ Image captured and saved to: {img_path}")

# # img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
# # import cv2
# # img_cv = cv2.imread(r'C:\Users\alex\Downloads\name.jpg')

# # sys.path.insert(0, PathExtended.home().joinpath("AppData/Local/Tesseract-OCR").str)
# # import pytesseract
# # print(pytesseract.image_to_string(img_cv))

# print("\n🔍 Processing image with Tesseract OCR...")
# q = Terminal().run(f"cd ~/AppData/Local/Tesseract-OCR; pytesseract '{img_path}'", shell="pwsh").capture().op

# try:
#     text = pytesseract.image_to_string(Image.open(img_path))
#     console.print(Panel(text, title="📄 Extracted Text Result:", title_align="left", expand=False))
# except FileNotFoundError:
#     print(f"Error: Image file not found at {img_path}")
