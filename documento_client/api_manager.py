import requests
from PySide2.QtCore import QObject


class APIException(Exception):
    pass


class AuthException(APIException):
    pass


class APIManager(QObject):
    base_url = "http://127.0.0.1:8000"
    login_url = base_url + "/api/auth/login/"
    jobs_url = base_url + "/api/print_jobs/"
    categories_url = base_url + "/api/categories/"

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
        r = requests.post(
            self.login_url,
            json={
                "username": username,
                "password": password,
            },
        )
        self.evaluate_res(r)
        self.token = r.json()["token"]
        return r.ok
