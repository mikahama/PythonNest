__author__ = 'mikahamalainen'
import re
import sys, os
import codecs
from jinja2 import Template

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

    def render_response(self, template=None, context=None, code=None, headers=None):
        if code is not None:
            self.response.code = code
        if headers is not None:
            self.response.headers = headers

        if context is None:
            context = sys._getframe().f_back.f_locals

        if template is None:
            template_file = sys._getframe().f_back.f_code.co_name
            template_path = os.path.dirname(os.path.abspath(sys._getframe().f_back.f_globals["__file__"]))
            try:
                t = codecs.open(os.path.join(template_path, "templates", template_file+".html"), "r")
                template = Template(t.read())
                self.response.content = template.render(context)
            except UnicodeError as e:
                self.response.code = 500
                self.response.content = e.message

    def serve_file(self, content_type, file_path):
        self.response.headers = [('Content-Type', content_type), ('X-Sendfile', os.path.abspath(file_path))]
        self.response.content = ""



class Response():
    def __init__(self):
        self.content = ""
        self.code = 200
        self.headers = [('Content-Type','text/html; charset=utf-8')]

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