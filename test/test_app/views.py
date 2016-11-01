__author__ = 'mikahamalainen'

def start(request):
    teksti = "Morjens, kaikki!"
    request.render_response()

def moi(request):
    request.response.content = "Moro"