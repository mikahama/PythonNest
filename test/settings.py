__author__ = 'mikahamalainen'

import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/mikahamalainen/PycharmProjects/')

from PythonNest import Url
import PythonNest.nest_wsgi
import views

urls = [Url("/", views.start, regex=True), Url("/moi", views.moi, regex=True)]

def application(e, r):
    return PythonNest.nest_wsgi.handle_request(e, r, urls)