__author__ = 'mikahamalainen'
import re
import sys, os
import codecs
from jinja2 import Template
import hashlib
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId

class Request():
    def __init__(self, url, cookies="", parameters={"get":{}, "post":{}}, method="get", headers = {}, settings ={}):
        self.url = url
        self.cookies = self.__cookies_to_dict__(cookies)
        self.get = parameters["get"]
        self.post = parameters["post"]
        self.parameters = parameters["get"].update(parameters["post"])
        self.method = method
        self.headers =headers
        if "id1" in self.cookies.keys() and "id2" in self.cookies.keys():
            id1 = self.cookies["id1"]
            id2 = self.cookies["id2"]
        else:
            id1 = None
            id2 = None
        self.response = Response(settings, id1, id2)

    def __cookies_to_dict__(self, cookie_string):
        items = cookie_string.split("; ")
        dict = {}
        for item in items:
            if "=" in item:
                key, value = item.split("=", 1)
            else:
                key = item
                value = True
            dict[key] = value
        return dict


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

class Session():
    def __init__(self, settings, id1=None, id2=None):
        self.settings = settings["mongo"]
        client = MongoClient(self.settings["url"])
        db = client[self.settings["database"]]
        self.has_changed = False

        if id1 is not None and id2 is not None:
            #session open -> check
            session = db.sessions.find_one({'_id': ObjectId(id1)})
            if session["id2"] == id2:
                #session secret is correct
                self.id1 = id1
                self.id2 = id2
                self.session_data = session
            else:
                #session secret incorrect -> new session
                id1 = None
                id2 = None


        if id1 is None or id2 is None:
            #new session
            self.has_changed = True
            session_secret = os.urandom(2000)
            self.id2 = hashlib.sha512(settings["secret_key"] + session_secret ).hexdigest()
            self.session_data = {"id2": self.id2, "last_renew": datetime.datetime.utcnow()}
            self.id1 = str(db.sessions.insert_one(self.session_data).inserted_id)

    def __setitem__(self, key, item):
        self.session_data[key] = item

    def __getitem__(self, key):
        return self.session_data[key]

    def __repr__(self):
        return repr(self.session_data)

    def __len__(self):
        return len(self.session_data)

    def __delitem__(self, key):
        del self.session_data[key]

    def __cmp__(self, dict):
        return cmp(self.session_data, dict)

    def __contains__(self, item):
        return item in self.session_data

    def __iter__(self):
        return iter(self.session_data)

    def __unicode__(self):
        return unicode(repr(self.session_data))

    def keys(self):
        return self.session_data.keys()

    def values(self):
        return self.session_data.values()

    def items(self):
        return self.session_data.items()

    def save(self):
        client = MongoClient(self.settings["url"])
        db = client[self.settings["database"]]
        self.session_data["last_renew"] = datetime.datetime.utcnow()
        db.sessions.mycollection.update({'_id': ObjectId(self.id1)}, {"$set": self.session_data}, upsert=False)
        self.has_changed = True

    def close(self):
        client = MongoClient(self.settings["url"])
        db = client[self.settings["database"]]
        db.sessions.delete_one({'_id': ObjectId(self.id1)})


class Response():
    def __init__(self, settings, id1, id2):
        self.content = ""
        self.code = 200
        self.headers = [('Content-Type','text/html; charset=utf-8')]
        self.session = Session(settings, id1, id2)
        self.settings = settings

    def get_headers(self):
        if self.session.has_changed:
            cookie_age = self.cookie_date(self.settings["session_length"])
            self.headers.append(("Set-Cookie", "id1=" + self.session.id1 + "; Expires="+cookie_age+"; HttpOnly; SameSite=Strict"))
            self.headers.append(("Set-Cookie", "id2=" + self.session.id2 + "; Expires="+cookie_age+"; HttpOnly; SameSite=Strict"))
        return self.headers

    def open_new_session(self):
        self.session.close()
        self.session = Session(self.settings)

    def cookie_date(self, seconds):
        now = datetime.datetime.utcnow()
        expires = now + datetime.timedelta(seconds=seconds)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        date = days[expires.weekday()] + ", " + str(expires.day) + " " + months[expires.month-1] + " " + expires.strftime("%Y %H:%M:%S") + " GMT"
        return date


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