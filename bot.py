from webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from twilio.rest import Client
import smtplib
import time
import random
import logging


class Bot:
    def __init__(self, start_page_url):
        self.webdriver = WebDriver()
        self.start_page_url = start_page_url

    def go_to_start_page(self):
        self.webdriver.open_url(self.start_page_url)

    def refresh(self):
        self.webdriver.refresh()

    def go_to_festival_page(self, festival_name):
        self.webdriver.fill_in_input_field("/html/body/div[1]/div[1]/section/div[2]/div/div/div[1]/label/div[2]/input",
                                           festival_name)
        time.sleep(1)
        self.select_item_by_x_path('//*[@id="site-search-item-0"]')

    def quit(self):
        self.webdriver.quit()

    def is_on_start_page(self):
        return self.webdriver.get_current_url() == self.start_page_url

    def select_item(self, item_name):
        item = self.webdriver.find_element_by_x_path(f'//*[text()="{item_name}"]')
        return self.webdriver.click_on_element(item)

    def select_item_by_x_path(self, item_x_path):
        item = self.webdriver.find_element_by_x_path(item_x_path)
        return self.webdriver.click_on_element(item)

    def go_to_ticket_page(self, otherCategory, ticketName):
        if otherCategory == "":
            self.select_item_by_x_path(f'//*[text()="{ticketName}"]')
        else:
            self.select_item(otherCategory)
            time.sleep(1)
            self.select_item_by_x_path(f'//*[text()="{ticketName}"]')

    def find_available(self):
        try:
            self.webdriver.driver.find_element_by_xpath('//*[text()="Er worden op dit moment geen tickets aangeboden."]')
        except NoSuchElementException:
            return True
        return False

    def refresher(self):
        random_decimal = random.randint(40000, 80000) / 10000
        time.sleep(random_decimal)
        self.refresh()

    def reserve_ticket(self):
        self.select_item_by_x_path("/html/body/div[1]/div[2]/div[3]/a[1]")
        time.sleep(0.355)
        self.select_item_by_x_path('//*[text()="Koop ticket"]')

    def dial_number(self, twilioNumber, number, sid, token):
        TWIML_INSTRUCTIONS_URL = \
            "https://static.fullstackpython.com/phone-calls-python.xml"
        client = Client(sid, token)

        client.calls.create(to=number, from_=twilioNumber,
                            url=TWIML_INSTRUCTIONS_URL, method="GET")

    def check_price(self, max_price):
        """Check if ticket price is within budget"""
        try:
            price_element = self.webdriver.find_element_by_x_path('//strong[@class="css-14yessp ebnsudl0"]')
            if price_element:
                price_text = price_element.text
                # Extract numeric value from "€296.79" format
                price_value = float(price_text.replace('€', '').replace(',', '.'))
                logging.info(f"Found ticket price: €{price_value}")
                
                if price_value <= max_price:
                    logging.info(f"Price €{price_value} is within budget (max: €{max_price})")
                    return True
                else:
                    logging.warning(f"Price €{price_value} exceeds budget (max: €{max_price})")
                    return False
        except:
            logging.warning("Could not find or parse ticket price")
            return True  # If can't find price, proceed anyway
        
        return False
