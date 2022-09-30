#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        dataString = self.data.decode('utf-8')
        lines = dataString.splitlines()
        # get the method type
        self.requestType = lines[0].split()[0]
        # get the relative path (which we will use for 301 since we don't want to append the abs path)
        self.relativePath = lines[0].split()[1]
        # this is the absolute path
        self.servedFilePath = os.path.abspath("www") + self.relativePath
        # will store our response
        self.response = None

        if self.requestType != "GET":
            self.handle405()
        else:
            # if it is a .css or a .html without  ending with a "/"
            if((".css" in self.servedFilePath or ".html" in self.servedFilePath) and self.servedFilePath[-1] != "/"):
                self.handleMimeType()
            elif self.servedFilePath[-1] == "/":
                self.handleIndex()
            elif self.servedFilePath[-1] != "/":
                self.handle301()
        self.request.sendall(bytearray(self.response,'utf-8'))

    def checkFileExists(self):
        # check to see if the file exists
        try:
            file = open(self.servedFilePath, 'r')
        except FileNotFoundError:
            return False
        else:
            return True


    def handleIndex(self):
        # will handle the requests ending with "/"
        self.servedFilePath += "index.html"
        if self.checkFileExists():
            content = open(self.servedFilePath, "r").read()
            self.response = "HTTP/1.1 200 OK\r\n" + "Content-type: text/html\r\n" + "Content-length: " + str(len(content)) +"\r\n" + content + "\r\n"
        else:
            # if the file doesn't exist
            self.handle404()


    def handleMimeType(self):
        # will handle the requests ending with a .cs and a .html (without the "/" ending)
        if self.checkFileExists():
            content = open(self.servedFilePath, 'r').read()
            if ".css" in self.servedFilePath:
                self.response = "HTTP/1.1 200 OK\r\n" + "Connection: Closed\r\n" + "Content-type: text/css\r\n" + "Content-length: " + str(len(content)) +"\r\n" + content + "\r\n"
            else:
                self.response = "HTTP/1.1 200 OK\r\n" + "Connection: Closed\r\n" + "Content-type: text/html\r\n" + "Content-length: " + str(len(content)) +"\r\n" + content + "\r\n"
        else:
            # if the file doesn't exist
            self.handle404()

    def handle404(self):
        # handles 404 errors
        self.response = "HTTP/1.1 404 Not Found\r\n" + "Connection: Closed\r\n" + "Content-type: text/html\r\n"

    def handle301(self):
        # handles redirects using the relative path
        self.response = "HTTP/1.1 301 Moved Permanently\r\n" + "Connection: Closed\r\n" + "Location: " + self.relativePath + "/" + "\r\n" + "Content-length: 0\r\n" + "Content-type: text/html\r\n"

    def handle405(self):
        # handles requests with other methods than GET
        self.response = "HTTP/1.1 405 Method Not Allowed\r\n" + "Connection: Closed\r\n" + "Content-type: text/html\r\n"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
