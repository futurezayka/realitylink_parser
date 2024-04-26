from selenium import webdriver
from config import CONFIG
from parser.parser import Parser

if __name__ == '__main__':

    if CONFIG.get('USE_DRIVER_OPTIONS'):
        from config import CHROME_OPTIONS
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()

        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)

        scraper = Parser(webdriver.Chrome(options=chrome_options))
    else:
        scraper = Parser(webdriver.Chrome())

    scraper.web_driver.get(CONFIG.get('BASE_URL'))
    scraper.write_residences_to_json()
