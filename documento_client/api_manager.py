from typing import Optional

import requests
from PyQt5.QtCore import QObject


class APIException(Exception):
    pass


class AuthException(APIException):
    pass


class APIManager(QObject):
    base_url = "http://127.0.0.1:8000"
    login_url = base_url + "/api/auth/login/"
    jobs_url = base_url + "/api/print_jobs/"
    categories_url = base_url + "/api/categories/"
    documents_url = base_url + "/api/documents/"
    print_report_url = documents_url + "{}/print_report/"

    def __init__(self):
        super().__init__()
        self.token = None

    @property
    def headers(self):
        return {"Authorization": f"Token {self.token}"}

    def evaluate_res(self, res):
        if res.ok:
            return
        if res.status_code in (403, 401):
            raise AuthException
        res.raise_for_status()

    def login(self, username, password):
        # Get auth token
        r = requests.post(self.login_url, json={"username": username, "password": password,},)
        self.evaluate_res(r)
        self.token = r.json()["token"]
        return r.ok

    def get_categories(self):
        r = requests.get(self.categories_url, headers=self.headers)
        self.evaluate_res(r)
        return r.json()

    def upload_document(self, path: str, title: str, category: Optional[int]) -> bool:
        print(path, title, category)
        r = requests.post(
            self.documents_url,
            data={"name": title, "category": category},
            files={"file": open(path, "rb")},
            headers=self.headers,
        )
        self.evaluate_res(r)
        return r.json()

    def print_report(self, document: int, report: str):
        r = requests.post(
            self.print_report_url.format(document), data={"report": report}, headers=self.headers
        )
        self.evaluate_res(r)
        return r.json()

    REPORTS = ["barcode_label", "info_page"]
