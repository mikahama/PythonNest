__author__ = 'mikahamalainen'

import sys
import test_app.views as views
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/mikahamalainen/PycharmProjects/')

from PythonNest import Url
import PythonNest.nest_wsgi


settings =  {"secret_key": "rewrweras93r2aagdfga",
             "mongo" : {"url":"mongodb://localhost:27017/",
                        "database":"python_nest",
                        }
             }

urls = [Url("/", views.start, regex=True), Url("/moi", views.moi, regex=True)]

def application(e, r):
    return PythonNest.nest_wsgi.handle_request(e, r, urls, settings)