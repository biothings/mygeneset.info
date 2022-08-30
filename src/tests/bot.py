from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager, ChromeType


class Bot:
    def start(self):
        """Start a selenium web driver"""
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--lang=en")
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        self.driver = webdriver.Chrome(driver_path, options=chrome_options)
        self.driver.implicitly_wait(20)

    def stop(self):
        """Stop the selenium web driver"""
        self.driver.quit()

    def go_to_url(self, url):
        """Go to a url"""
        try:
            self.driver.get(url)
        except NoSuchElementException as ex:
            self.fail(ex.msg)
