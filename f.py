from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import time
import os

def take_screenshot(url: str) -> str:
    options = Options()
    options.add_argument("--headless")

    service = Service()

    try:
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)
        driver.set_window_size(1920, 1080)
        time.sleep(5)  # Wait for 5 seconds before taking screenshot

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        driver.save_screenshot(filename)
        return filename
    except Exception as e:
        raise Exception(f"Failed to take screenshot: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    url: str = "http://10.17.62.79:49981/"
    try:
        screenshot_file: str = take_screenshot(url)
        print(f"Screenshot saved as: {screenshot_file}")
    except Exception as e:
        print(f"Error: {e}")

