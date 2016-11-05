#!/bin/python
__author__ = 'mikahamalainen'
import sys
from subprocess import Popen
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
import os



help = "Usage:\n\tTo start your app: nest run <IP:PORT>\n\tTo start a new project: nest newproject project_name (not implemented)"

class PyChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.py"]

    def set_address_and_run(self, address):
        self.address = address
        self.p = self.run_server()

    def run_server(self):
        return Popen(['uwsgi', '--http', self.address, '--honour-stdin', '--wsgi-file', 'settings.py'])


    def process(self, event):
        print "Restarting server"
        self.p.terminate()
        self.p = self.run_server()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


if len(sys.argv) >1:
    if sys.argv[1] == "run":
        if len(sys.argv) > 2:
            address = sys.argv[2]
        else:
            address = ":9090"
        print "Starting server on " + address
        observer = Observer()
        handler = PyChangeHandler()
        handler.set_address_and_run(address)
        observer.schedule(handler, os.getcwd(), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            handler.p.terminate()
    else:
        print help
else:
    print help