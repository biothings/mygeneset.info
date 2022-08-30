
import json
import time
import os

from biothings.tests.web import BiothingsWebTest
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode

from .bot import Bot


class MyGenesetLocalTestBase(BiothingsWebTest, Bot):
    HOST = 'http://localhost:8000'
    GITHUB_USERNAME = os.environ['GITHUB_USERNAME']
    GITHUB_PASSWORD = os.environ['GITHUB_PASSWORD']
    ORCID_USERNAME = os.environ['ORCID_USERNAME']
    ORCID_PASSWORD = os.environ['ORCID_PASSWORD']
    ORCID_ID = os.environ['ORCID_ID']


class TestUserLogin(MyGenesetLocalTestBase):
    def test_01_login_logout_github(self):
        self.start()
        # Test login
        self.go_to_url(f'{self.HOST}/login/github')
        time.sleep(2)
        self.driver.find_element(By.ID, "login_field").send_keys(self.GITHUB_USERNAME)
        self.driver.find_element(By.ID, "password").send_keys(self.GITHUB_PASSWORD)
        self.driver.find_element("xpath", "//input[@value='Sign in']").click()
        time.sleep(5)
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == "user":
                found_user_cookie = True
                user_cookie = cookie['value']
        assert found_user_cookie is True, "User cookie not found."
        # Check user info
        resp = self.request(f'{self.HOST}/user_info', cookies={"user": user_cookie})
        assert resp.status_code == 200, "User info request failed."
        assert resp.json()["username"] == self.GITHUB_USERNAME, "Unexpected username in user_info"
        # Test logout
        self.go_to_url(f'{self.HOST}/logout')
        time.sleep(2)
        for cookie in self.driver.get_cookies():
            assert cookie['name'] != "user", "User cookie not removed."
        self.stop()

    def test_02_login_logout_orcid(self):
        self.start()
        # Test login
        self.go_to_url(f'{self.HOST}/login/orcid')
        time.sleep(2)
        self.driver.find_element(By.ID, "username").send_keys(self.ORCID_USERNAME)
        self.driver.find_element(By.ID, "password").send_keys(self.ORCID_PASSWORD)
        self.driver.find_element(By.ID, "signin-button").click()
        time.sleep(5)
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == "user":
                found_user_cookie = True
                user_cookie = cookie['value']
        assert found_user_cookie is True, "User cookie not found."
        # Check user info
        resp = self.request(f'{self.HOST}/user_info', cookies={"user": user_cookie})
        assert resp.status_code == 200, "User info request failed."
        assert resp.json()["username"] == self.ORCID_ID, "Unexpected username in user_info"
        # Test logout
        self.go_to_url(f'{self.HOST}/logout')
        time.sleep(2)
        for cookie in self.driver.get_cookies():
            assert cookie['name'] != "user", "User cookie not removed."
        self.stop()


class TestUserGenesets(MyGenesetLocalTestBase):

    def test_get_cookie(self):
        self.start()
        # Login and get user cookie
        self.go_to_url(f'{self.HOST}/login/github')
        time.sleep(2)
        self.driver.find_element(By.ID, "login_field").send_keys(self.GITHUB_USERNAME)
        self.driver.find_element(By.ID, "password").send_keys(self.GITHUB_PASSWORD)
        self.driver.find_element("xpath", "//input[@value='Sign in']").click()
        time.sleep(5)
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == "user":
                user_cookie = cookie['value']
        # Write user cookie to file
        with open('user_cookie.txt', 'w') as f:
            f.write(user_cookie)
        self.stop()

    def test_create_geneset_dry_run(self):
        payload = json.dumps(
            {
                "name": "Test",
                "is_public": True,
                "taxid": "9606",
                "genes": ["1001"]
            }
        )
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'user=%s' % open('user_cookie.txt').read()
        }
        res = self.request(
            f'{self.HOST}/v1/user_geneset?dry_run=true',
            method='POST',
            headers=headers,
            data=payload
        )
        assert res.status_code == 200, "Response status is not 200."
        expected_respone = {
            "new_document": {
                "name": "Test",
                "author": "ravila4",
                "is_public": True,
                "genes": [
                    {
                        "mygene_id": "1001",
                        "source_id": "1001",
                        "symbol": "CDH3",
                        "name": "cadherin 3",
                        "ncbigene": "1001",
                        "ensemblgene": "ENSG00000062038",
                        "uniprot": "P22223"
                    }
                ]
            }
        }
        assert res.json() == expected_respone, "The response document does not match the expected one."


if __name__ == '__main__':
    TestUserLogin().test_login_github()
