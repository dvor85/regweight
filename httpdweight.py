#!/usr/bin/env python

import pickle
from os import path
from wsgiref.simple_server import make_server

SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,"regweight.dump")


def application(environ, start_response):

    response_body=''
    if path.isfile(DUMP_FILE):
	with open(DUMP_FILE,"rb") as dump:
	    response_body=str(pickle.load(dump))


    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]

# Instantiate the WSGI server.
# It will receive the request, pass it to the application
# and send the application's response to the client
def main():
    httpd = make_server(
	'0.0.0.0', # The host name.
	8051, # A port number where to wait for the request.
	application # Our application object name, in this case a function.
    )
    httpd.serve_forever()

if __name__ == '__main__':
    main()

