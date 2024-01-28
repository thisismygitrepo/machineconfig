
"""Convert image to text.
"""


# import sys
from crocodile.msc.odds import capture_from_webcam
from crocodile.meta import Terminal

img_path = capture_from_webcam(show=False, wait=False, save=True)
# img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
# import cv2
# img_cv = cv2.imread(r'C:\Users\alex\Downloads\name.jpg')

# sys.path.insert(0, P.home().joinpath("AppData/Local/Tesseract-OCR").str)
# import pytesseract
# print(pytesseract.image_to_string(img_cv))

q = Terminal().run(f"cd ~/AppData/Local/Tesseract-OCR; pytesseract '{img_path}'", shell="pwsh").capture().op
