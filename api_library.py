import json
import shlex
import time
from datetime import datetime, timezone

import requests
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class ApiLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.builtin = BuiltIn()
        self.sessions = {}
        self.current_account = None
        self.previous_account = None

    @keyword("Use Account")
    def use_account(self, username, password):
        if username not in self.sessions:
            session = requests.Session()
            self.login(session, username, password)
            self.sessions[username] = session

        if username != self.current_account:
            self.previous_account = self.current_account
            self.current_account = username

    @keyword("Use Previous Account")
    def use_previous_account(self):
        if self.previous_account is None:
            raise RuntimeError("No previous account available.")

        self.current_account, self.previous_account = (
            self.previous_account,
            self.current_account
        )

    def login(self, session, username, password):
        response = session.post(
            "https://api.example.com/api/v1/login",
            json={
                "username": username,
                "password": password
            }
        )

        response.raise_for_status()

    def request(self, method, endpoint, *parameters, request_body=None):
        if self.current_account is None:
            raise RuntimeError(
                "No account selected. Use 'Use Account' first."
            )

        endpoint = endpoint.format(*parameters)
        session = self.sessions[self.current_account]

        request_time = datetime.now(timezone.utc)
        start_time = time.perf_counter()

        response = session.request(
            method=method,
            url=f"https://api.example.com{endpoint}",
            json=request_body
        )

        duration = time.perf_counter() - start_time

        self.log_request(
            response,
            request_time,
            duration
        )

        response_body = response.json()

        response.raise_for_status()

        self.builtin.set_test_variable(
            "${response_body}",
            response_body
        )

    def log_request(self, response, request_time, duration):
        request = response.request

        request_body = None

        if request.body:
            body = (
                request.body.decode()
                if isinstance(request.body, bytes)
                else request.body
            )

            try:
                request_body = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                request_body = body

        response_body = response.json()

        request_log = {
            "request_time": request_time.isoformat(
                timespec="milliseconds"
            ),
            "username": self.current_account,
            "request_body": request_body,
            "endpoint": request.path_url,
            "request_type": request.method,
            "response_body": response_body,
            "response_status": response.status_code,
            "duration": f"{duration:.3f}s",
            "execute": self.build_curl_command(request)
        }

        self.builtin.log(
            json.dumps(request_log, indent=2),
            html=False
        )

    def build_curl_command(self, request):
        command = [
            "curl",
            "-X",
            request.method,
            shlex.quote(request.url)
        ]

        for name, value in request.headers.items():
            command.extend([
                "-H",
                shlex.quote(f"{name}: {value}")
            ])

        if request.body:
            body = (
                request.body.decode()
                if isinstance(request.body, bytes)
                else str(request.body)
            )

            command.extend([
                "--data-raw",
                shlex.quote(body)
            ])

        return " ".join(command)

    @keyword("Make GET Request")
    def get(self, endpoint, *parameters):
        self.request(
            "GET",
            endpoint,
            *parameters
        )

    @keyword("Make POST Request")
    def post(self, endpoint, *parameters, request_body=None):
        self.request(
            "POST",
            endpoint,
            *parameters,
            request_body=request_body
        )

    @keyword("Make PUT Request")
    def put(self, endpoint, *parameters, request_body=None):
        self.request(
            "PUT",
            endpoint,
            *parameters,
            request_body=request_body
        )

    @keyword("Make PATCH Request")
    def patch(self, endpoint, *parameters, request_body=None):
        self.request(
            "PATCH",
            endpoint,
            *parameters,
            request_body=request_body
        )

    @keyword("Make DELETE Request")
    def delete(self, endpoint, *parameters):
        self.request(
            "DELETE",
            endpoint,
            *parameters
        )

    @keyword("Close All Sessions")
    def close_all_sessions(self):
        for session in self.sessions.values():
            session.close()

        self.sessions.clear()
        self.current_account = None
        self.previous_account = None