from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager


class Bot:
    def start(self):
        """Start a selenium web driver"""
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("-headless")
        self.driver = webdriver.Firefox(
            service=webdriver.FirefoxService(executable_path=GeckoDriverManager().install()),
            options=firefox_options,
        )
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
