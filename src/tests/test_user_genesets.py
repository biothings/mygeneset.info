"""
These are sort of like integration tests for user geneset operations.
It requires a running elasticsearch instance with a collection called 'user_genesets'
and also the tornado server running alongside the the web interface.
"""


import json
import os
import time

import pytest
from biothings.tests.web import BiothingsWebTest
from selenium.webdriver.common.by import By

from .bot import Bot


class MyGenesetLocalTestBase(BiothingsWebTest, Bot):
    HOST = 'http://localhost:8080'
    GITHUB_USERNAME = os.environ['GITHUB_USERNAME']
    GITHUB_PASSWORD = os.environ['GITHUB_PASSWORD']
    ORCID_USERNAME = os.environ['ORCID_USERNAME']
    ORCID_PASSWORD = os.environ['ORCID_PASSWORD']

class TestUserLogin(MyGenesetLocalTestBase):
    # @pytest.mark.skip(reason="May fail if GitHub requests a code")
    def test_01_login_logout_github(self):
        self.start()
        # Test login
        self.go_to_url(f'{self.HOST}/login/github')
        time.sleep(2)
        print('#####')
        print(self.driver)
        print(self.driver.__dict__)
        self.driver.find_element(By.ID, "login_field").send_keys(self.GITHUB_USERNAME)
        self.driver.find_element(By.ID, "password").send_keys(self.GITHUB_PASSWORD)
        self.driver.find_element("xpath", "//input[@value='Sign in']").click()
        time.sleep(15)
        cookies = self.driver.get_cookies()
        found_user_cookie = False
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

    @pytest.mark.skip(reason="Has to configure credentials")
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
        assert resp.json()["username"] == self.ORCID_USERNAME, "Unexpected username in user_info"
        # Test logout
        self.go_to_url(f'{self.HOST}/logout')
        time.sleep(2)
        for cookie in self.driver.get_cookies():
            assert cookie['name'] != "user", "User cookie not removed."
        self.stop()


@pytest.mark.skip(reason="Has to configure credentials")
class TestUserGenesets(MyGenesetLocalTestBase):
    """These tests use the ORCID login method because it is easier to automate.
    GitHub sometimes requires verifying the login with a code if it detects an unrecognized device."""

    def test_get_cookie(self):
        self.start()
        # Login with ORCID
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
        # Write user cookie to file
        with open('user_cookie.txt', 'w') as f:
            f.write(user_cookie)
        self.stop()

    def test_create_geneset_dry_run(self):
        payload = json.dumps(
            {
                "name": "Test geneset",
                "is_public": True,
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
        expected_response = {
            "new_document": {
                "name": "Test geneset",
                "author": self.ORCID_USERNAME,
                "is_public": True,
                "count": 1,
                "genes":
                    {
                        "mygene_id": "1001",
                        "source_id": "1001",
                        "symbol": "CDH3",
                        "name": "cadherin 3",
                        "ncbigene": "1001",
                        "ensemblgene": "ENSG00000062038",
                        "uniprot": "P22223",
                        "taxid": 9606
                    },
                "taxid": 9606
            }
        }
        doc = res.json()["new_document"]
        for key, val in doc.items():
            assert key in expected_response["new_document"], f"{key} not found in response."
            assert val == expected_response["new_document"][key], f"{key} does not match the expected value"

    def test_create_public_geneset(self):
        payload = json.dumps(
            {
                "name": "Test public geneset",
                "description": "Test public geneset description",
                "genes": ["1001"],
                "is_public": "true"
            }
        )
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read()
        }
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        assert results["success"]
        assert results["result"] == "created"
        assert results["_id"] is not None
        assert results["name"] == "Test public geneset"
        assert results["author"] == self.ORCID_USERNAME
        assert results["count"] == 1
        time.sleep(2)  # Wait for the document to be indexed
        res = self.request(
            f'{self.HOST}/v1/geneset/{results["_id"]}',
            method='GET'
        )
        assert res.json()["name"] == "Test public geneset"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 1
        assert res.json()["is_public"] is True
        assert res.json()["taxid"] == 9606
        assert res.json()["description"] == "Test public geneset description"
        assert res.json()["genes"]["mygene_id"] == "1001"
        assert res.json()["genes"]["source_id"] == "1001"
        assert res.json()["genes"]["symbol"] == "CDH3"
        assert res.json()["genes"]["name"] == "cadherin 3"
        assert res.json()["genes"]["ncbigene"] == "1001"
        assert res.json()["genes"]["ensemblgene"] == "ENSG00000062038"
        assert res.json()["genes"]["uniprot"] == "P22223"
        assert res.json()["created"] is not None
        assert res.json()["updated"] is not None

    def test_create_private_geneset(self):
        payload = json.dumps(
            {
                "name": "Test private geneset",
                "description": "Test private geneset description",
                "genes": ["1001"],
                "is_public": "false"
            }
        )
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read()
        }
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        assert results["success"]
        assert results["result"] == "created"
        assert results["_id"] is not None
        assert results["name"] == "Test private geneset"
        assert results["author"] == self.ORCID_USERNAME
        assert results["count"] == 1
        time.sleep(2)
        # Expect 404 because the geneset is private
        res = self.request(
            f'{self.HOST}/v1/geneset/{results["_id"]}',
            method='GET', expect=404
        )
        # Passing the cookie should return the geneset
        res = self.request(
            f'{self.HOST}/v1/geneset/{results["_id"]}',
            method='GET',
            headers=headers
        )
        assert res.json()["name"] == "Test private geneset"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 1
        assert res.json()["is_public"] is False
        assert res.json()["taxid"] == 9606
        assert res.json()["description"] == "Test private geneset description"
        assert res.json()["genes"]["mygene_id"] == "1001"
        assert res.json()["genes"]["source_id"] == "1001"
        assert res.json()["genes"]["symbol"] == "CDH3"
        assert res.json()["genes"]["name"] == "cadherin 3"
        assert res.json()["genes"]["ncbigene"] == "1001"
        assert res.json()["genes"]["ensemblgene"] == "ENSG00000062038"
        assert res.json()["genes"]["uniprot"] == "P22223"
        assert res.json()["created"] is not None
        assert res.json()["updated"] is not None

    def test_delete_public_geneset(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read()
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset to delete",
                "genes": ["1001"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        # Without the cookie, expect 401
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='DELETE', expect=401
        )
        # Delete the geneset
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='DELETE',
            headers=headers
        )
        assert res.json()["success"]
        assert res.json()["result"] == "deleted"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test geneset to delete"
        assert res.json()["author"] == self.ORCID_USERNAME
        time.sleep(2)
        # Query to make sure it's gone
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET', expect=404
        )

    def test_delete_private_geneset(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read()
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test private geneset to delete",
                "genes": ["1001"],
                "is_public": "false"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        # Without the cookie, expect 401
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='DELETE', expect=401
        )
        # Delete the geneset
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='DELETE',
            headers=headers
        )
        assert res.json()["success"]
        assert res.json()["result"] == "deleted"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test private geneset to delete"
        assert res.json()["author"] == self.ORCID_USERNAME
        time.sleep(2)
        # Query to make sure it's gone
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            headers=headers,
            method='GET', expect=404
        )

    def test_update_geneset_add(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
            'Content-Type': 'application/json'
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset to update",
                "genes": ["1001"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        time.sleep(2)
        # Without the cookie, expect 401
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='PUT', expect=401
        )
        # Update the geneset
        payload = json.dumps(
            {
                "description": "Added one gene",
                "genes": ["1002"],
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=add',
            method='PUT',
            headers=headers,
            data=payload,
        )
        assert res.json()["success"]
        assert res.json()["result"] == "updated"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 2
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["description"] == "Added one gene"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 2
        assert res.json()["is_public"] is True
        assert res.json()["genes"][0]["mygene_id"] == "1001"
        assert res.json()["genes"][1]["mygene_id"] == "1002"

    def test_update_geneset_remove(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
            'Content-Type': 'application/json'
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset to update",
                "genes": ["1001", "1002"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        time.sleep(2)
        # Without the cookie, expect 401
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='PUT', expect=401
        )
        # Update the geneset
        payload = json.dumps(
            {
                "description": "Removed one gene",
                "genes": ["1002"],
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=remove',
            method='PUT',
            headers=headers,
            data=payload,
        )
        assert res.json()["success"]
        assert res.json()["result"] == "updated"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 1
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["description"] == "Removed one gene"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 1
        assert res.json()["is_public"] is True
        assert res.json()["genes"][0]["mygene_id"] == "1001"

    def test_update_geneset_replace(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset to update",
                "genes": ["1001", "1002"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        time.sleep(2)
        # Without the cookie, expect 401
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}',
            method='PUT', expect=401
        )
        # Update the geneset
        payload = json.dumps(
            {
                "description": "Replaced with 3 new genes",
                "is_public": False,
                "genes": ["1003", "1004", "1005"],
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=replace',
            method='PUT',
            headers=headers,
            data=payload,
        )
        assert res.json()["success"]
        assert res.json()["result"] == "updated"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 3
        time.sleep(2)
        # Geneset was changed to private
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET', expect=404
        )
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET',
            headers=headers
        )
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["description"] == "Replaced with 3 new genes"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 3
        assert res.json()["is_public"] is False
        assert res.json()["genes"][0]["mygene_id"] == "1003"
        assert res.json()["genes"][1]["mygene_id"] == "1004"
        assert res.json()["genes"][2]["mygene_id"] == "1005"

    def test_update_geneset_replace_with_empty(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset to update",
                "genes": ["1001", "1002"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        time.sleep(2)
        # Update the geneset
        payload = json.dumps(
            {
                "description": "Replaced with empty gene list",
                "is_public": False,
                "genes": [],
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=replace',
            method='PUT',
            headers=headers,
            data=payload,
        )
        assert res.json()["success"]
        assert res.json()["result"] == "updated"
        assert res.json()["_id"] == _id
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 0
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET',
            headers=headers
        )
        assert res.json()["name"] == "Test geneset to update"
        assert res.json()["description"] == "Replaced with empty gene list"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 0
        assert res.json()["is_public"] is False
        assert res.json()["genes"] == []

    def test_update_geneset_does_not_exist(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Update the geneset
        payload = json.dumps(
            {
                "description": "Replace genes on a non-existent geneset",
                "is_public": False,
                "genes": ["1003", "1004", "1005"],
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/fake-id?gene_operation=replace',
            method='PUT',
            headers=headers,
            data=payload,
            expect=404
        )
        assert res.json()["success"] is False
        assert res.json()["error"] == "Document does not exist."

    def test_create_geneset_empty(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test empty geneset",
                "genes": [],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        results = res.json()
        _id = results["_id"]
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["name"] == "Test empty geneset"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 0
        assert res.json()["is_public"] is True
        assert res.json().get("genes") is None

    def test_create_geneset_invalid(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset with invalid gene",
                "genes": "none",
                "is_public": True
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload, expect=400
        )
        assert res.reason == "Body element 'genes' must be a list."

    def test_create_geneset_invalid2(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test geneset without genes",
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload, expect=400
        )
        assert res.reason == "Body element 'genes' is required."

    def test_create_geneset_invalid3(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "genes": ["1001", "1002"],
                "is_public": "true"
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload, expect=400
        )
        assert res.reason == "Missing required body element 'name'."

    def test_create_multispecies_geneset(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        payload = json.dumps(
            {
                "name": "Test multispecies geneset",
                "description": "This geneset contains one human gene and one mouse gene",
                "genes": ["98660", "147968"],
                "is_public": True
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        _id = res.json()["_id"]
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["name"] == "Test multispecies geneset"
        assert res.json()["author"] == self.ORCID_USERNAME
        assert res.json()["count"] == 2
        assert res.json()["is_public"] is True
        assert res.json()["taxid"] == [10090, 9606]
        assert res.json()["genes"][0]["mygene_id"] == "98660"
        assert res.json()["genes"][1]["mygene_id"] == "147968"
        assert res.json()["genes"][0]["taxid"] == 10090
        assert res.json()["genes"][1]["taxid"] == 9606

    def test_update_multispecies_geneset_add(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test multispecies geneset",
                "description": "This geneset contains one human gene and one mouse gene",
                "genes": ["98660", "147968"],
                "is_public": True
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        _id = res.json()["_id"]
        time.sleep(2)
        # Add one more gene of another species
        payload = json.dumps(
            {
                "genes": ["1001", "507781"]
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=add',
            method='PUT',
            headers=headers,
            data=payload
        )
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["count"] == 4
        assert res.json()["genes"][0]["mygene_id"] == "98660"
        assert res.json()["genes"][0]["taxid"] == 10090
        assert res.json()["genes"][1]["mygene_id"] == "147968"
        assert res.json()["genes"][1]["taxid"] == 9606
        assert res.json()["genes"][2]["mygene_id"] == "1001"
        assert res.json()["genes"][2]["taxid"] == 9606
        assert res.json()["genes"][3]["mygene_id"] == "507781"
        assert res.json()["genes"][3]["taxid"] == 9913
        assert len(res.json()["taxid"]) == 3

    def test_update_multispecies_geneset_remove(self):
        """Remove a gene from a multispecies geneset, and see if the species is removed from the taxid list"""
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test multispecies geneset",
                "description": "This geneset contains one human gene and one mouse gene",
                "genes": ["98660", "147968", "507781"],
                "is_public": True
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        _id = res.json()["_id"]
        time.sleep(2)
        # Remove two genes
        payload = json.dumps(
            {
                "genes": ["98660", "507781"]
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=remove',
            method='PUT',
            headers=headers,
            data=payload
        )
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["count"] == 1
        assert res.json()["genes"][0]["mygene_id"] == "147968"
        assert res.json()["taxid"] == 9606
        assert res.json()["genes"][0].get("taxid") == 9606

    def test_update_multispecies_geneset_replace(self):
        headers = {
            'Cookie': 'user=%s' % open('user_cookie.txt').read(),
        }
        # Create a geneset
        payload = json.dumps(
            {
                "name": "Test multispecies geneset",
                "description": "This geneset contains one human gene and one mouse gene",
                "genes": ["98660", "147968"],
                "is_public": True
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset',
            method='POST',
            headers=headers,
            data=payload
        )
        _id = res.json()["_id"]
        time.sleep(2)
        # Replace genes
        payload = json.dumps(
            {
                "genes": ["1001", "507781"]
            }
        )
        res = self.request(
            f'{self.HOST}/v1/user_geneset/{_id}?gene_operation=replace',
            method='PUT',
            headers=headers,
            data=payload
        )
        time.sleep(2)
        # Query to make sure it's updated
        res = self.request(
            f'{self.HOST}/v1/geneset/{_id}',
            method='GET'
        )
        assert res.json()["count"] == 2
        assert res.json()["genes"][0]["mygene_id"] == "1001"
        assert res.json()["genes"][0]["taxid"] == 9606
        assert res.json()["genes"][1]["mygene_id"] == "507781"
        assert res.json()["genes"][1]["taxid"] == 9913
        assert len(res.json()["taxid"]) == 2
