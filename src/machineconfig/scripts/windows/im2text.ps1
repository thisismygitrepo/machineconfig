
activate_ve
$orig_path = $pwd
$target_path = Resolve-Path $args[0]
cd ~/AppData/Local/Tesseract-OCR/
pytesseract.exe $target_path
deactivate
cd $orig_path
