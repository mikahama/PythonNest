__author__ = 'mikahamalainen'
import sys, os
current_file = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.join(current_file, '../')
sys.path.append(parent_dir)
from PythonNest import Request

"""
    Env
    'wsgi.multiprocess', 'HTTP_COOKIE', 'SCRIPT_NAME', 'REQUEST_METHOD',
     'UWSGI_ROUTER', 'SERVER_PROTOCOL', 'QUERY_STRING', 'HTTP_USER_AGENT',
     'HTTP_CONNECTION', 'SERVER_NAME', 'REMOTE_ADDR', 'wsgi.url_scheme',
     'SERVER_PORT', 'uwsgi.node', 'wsgi.input', 'HTTP_DNT', 'HTTP_HOST',
     'wsgi.multithread', 'HTTP_UPGRADE_INSECURE_REQUESTS', 'HTTP_CACHE_CONTROL',
     'REQUEST_URI', 'HTTP_ACCEPT', 'wsgi.version', 'wsgi.run_once', 'wsgi.errors',
     'REMOTE_PORT', 'HTTP_ACCEPT_LANGUAGE', 'uwsgi.version', 'wsgi.file_wrapper',
     'HTTP_ACCEPT_ENCODING', 'PATH_INFO'

"""


def handle_request(env, start_response, urls):
    code = "500 Internal Server Error"
    headers = [('Content-Type','text/html')]
    content = "Internal Server error - no matching URL"
    for url in urls:
        if url.test_url(env['REQUEST_URI']):
            code, headers, content =  __create_request__(env, url,  url.handler)
    start_response(code, headers)
    return content


def __create_request__(env, url, handler):
    request = Request(url,env["HTTP_COOKIE"], method=env['REQUEST_METHOD'])
    handler(request)
    return request.response.code, request.response.headers, request.response.content