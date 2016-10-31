__author__ = 'mikahamalainen'
import re

class Request():
    def __init__(self, url, cookies=[], parameters={"get":{}, "post":{}}, method="get", headers = {}):
        self.url = url
        self.cookies = cookies
        self.get = parameters["get"]
        self.post = parameters["post"]
        self.parameters = parameters["get"].update(parameters["post"])
        self.method = method
        self.headers =headers
        self.response = Response()

class Response():
    def __init__(self):
        self.content = ""
        self.code = "500"
        self.headers = [('Content-Type','text/html')]

class Url():
    def __init__(self, url, handler, id=None, regex=True):
        self.url = url
        self.handler = handler
        self.id = id
        self.regex = regex

    def test_url(self, url):
        if self.regex:
            m = re.match(self.url, url)
            if m:
                return True
            else:
                return False
        else:
            if url == self.url:
                return True
            else:
                return False