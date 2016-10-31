__author__ = 'mikahamalainen'

def start(request):
    request.response.content = "Hello World!"

def moi(request):
    request.response.content = "Moro"