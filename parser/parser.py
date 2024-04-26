from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from config import CONFIG
from parser.file_manager import FileManager
from parser.models import Residence
from parser.selectors import XPATH, CLASS, ID


class Parser:

    def __init__(self, driver):
        self.web_driver = driver
        self.count_of_pages = None
        self.count_of_residences = CONFIG.get('COUNT_OF_RESIDENCES')
        self.timeout = CONFIG.get('TIMEOUT')

    def find_elements_by(self, by, value, multiple=False, is_clickable=False):
        locator_methods = {
            "xpath": By.XPATH,
            "class": By.CLASS_NAME,
            "id": By.ID,
        }

        locator_method = locator_methods.get(by.lower())

        if not locator_method:
            raise ValueError("Unsupported 'by' argument")

        wait = WebDriverWait(self.web_driver, self.timeout)

        if multiple:
            wait_condition = ec.visibility_of_all_elements_located
            if is_clickable:
                wait_condition = ec.element_to_be_clickable
        else:
            wait_condition = ec.visibility_of_element_located
            if is_clickable:
                wait_condition = ec.element_to_be_clickable

        try:
            return wait.until(wait_condition((locator_method, value)))
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            return None

    def get_count_of_pages(self):
        try:
            count = self.find_elements_by(
                'xpath', XPATH.get('PAGE_PAGINATION')
            ).text.split()[-1]
        except NoSuchElementException:
            return 1
        return int(count)

    def get_residence_links(self):

        def find_residential_links():
            residential_objects = self.find_elements_by(
                'class', CLASS.get('RESIDENCE_LINK'), multiple=True
            )
            return [residential.get_attribute('href') for residential in residential_objects]

        if self.count_of_pages is None:
            self.count_of_pages = self.get_count_of_pages()

        links = find_residential_links()

        for _ in range(self.count_of_pages - 1):
            pagination_button = self.find_elements_by(
                'xpath', XPATH.get('NEXT_BUTTON')
            )
            if pagination_button and len(links) < self.count_of_residences:
                pagination_button.click()
                links.extend(find_residential_links())
            else:
                break
        return links[:self.count_of_residences]

    def get_images(self):
        primary_photo = self.find_elements_by('xpath', XPATH.get('IMAGES'), is_clickable=True)

        if not primary_photo:
            return []

        primary_photo.click()
        count_el = self.find_elements_by('xpath', XPATH.get('IMAGE_COUNT'))
        count = int(count_el.text.split('/')[-1]) if count_el else 0
        image_urls = list()
        while len(image_urls) < count != 0:
            try:
                image = self.find_elements_by('id', ID.get('FULL_IMAGE'), is_clickable=True)
                image_urls.append(image.get_attribute('src'))
                image.click()
            except ElementNotInteractableException:
                break
        return image_urls

    def get_residence_data(self, residence_link):
        def process_element_text(elements):
            return elements.text.strip() if elements else ''

        def process_int_value(elements):
            if elements:
                text = elements.text.strip().split()[0]
                return int(text) if text.isdigit() else None
            return None

        def process_float_value(elements):
            if elements:
                text = elements.text.strip().split()[0].replace(',', '.')
                if text:
                    return float(text[1:]) if text.startswith('$') else float(text)
            return None

        self.web_driver.get(residence_link)

        title_elements = self.find_elements_by('xpath', XPATH.get('TITLE'))
        region_elements = self.find_elements_by('xpath', XPATH.get('REGION'))
        address_elements = self.find_elements_by('xpath', XPATH.get('ADDRESS'))
        description_elements = self.find_elements_by('xpath', XPATH.get('DESCRIPTION'))
        price_elements = self.find_elements_by('xpath', XPATH.get('PRICE'))
        bedrooms_elements = self.find_elements_by('xpath', XPATH.get('ROOMS'))
        floor_area_elements = self.find_elements_by('xpath', XPATH.get('AREA'))

        title_text = process_element_text(title_elements)
        region_text = ",".join(region_elements.text.strip().split(",")[-2:]) if region_elements else ''
        address_text = process_element_text(address_elements)
        description_text = process_element_text(description_elements)
        price_value = process_float_value(price_elements)
        bedrooms_value = process_int_value(bedrooms_elements)
        floor_area_value = process_float_value(floor_area_elements)

        images = self.get_images()

        return Residence(
            link=residence_link,
            title=title_text,
            region=region_text,
            address=address_text,
            description=description_text,
            price=price_value,
            bedrooms=bedrooms_value,
            floor_area=floor_area_value,
            image_links=images
        )

    def collect_data(self):
        residences = self.get_residence_links()
        collected_data = []
        for residence in residences:
            data = self.get_residence_data(residence)
            collected_data.append(data)
        return collected_data

    def write_residences_to_json(self):
        residences_data = self.collect_data()
        FileManager.write_to_json(residences_data)