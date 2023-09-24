#  coding: utf-8 
from os import walk, path
import socketserver
# Copyright (c) 2023, Kaelen Brown
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
# some of the code is Copyright © 2001-2023 Python Software
# Foundation; All Rights Reserved
# and some of the code is Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Apache 2.0 License (found above)


class MyWebServer(socketserver.BaseRequestHandler):
    PATH = 'www'
        
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print ("Got a request of: %s\n" % self.data)

        # Get all the files in the www directory
        # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        self.files = [path.join(dirpath,f) for (dirpath, _, filenames) in walk(self.PATH) for f in filenames]

        # If the start of data contains GET
        if self.data.startswith("GET"):
            # Get the path from the request
            self.path = self.data.split()[1]

            # If the path is a directory, add index.html to the path
            if self.path.endswith('/'):
                self.mime_type = b"text/html;"
                self.path = self.PATH + self.path + 'index.html'
            # If the path is a file, get the mime type
            elif self.path.endswith('.css'):
                self.mime_type = b"text/css;"
                self.path = self.PATH + self.path
            elif self.path.endswith('.html'):
                self.mime_type = b"text/html;"
                self.path = self.PATH + self.path
            else:
                # Redirect to the path with a slash
                self.request.sendall(b"HTTP/1.1 301 Moved Permanently\r\n")
                self.request.sendall(b"Location: %s/\r\n" % self.path + '/')
            
                return
            
            # If the path is not in the www directory, return 404
            if not self.path in self.files:
                self.request.sendall(b"HTTP/1.1 404 Not Found\r\n")
                return

            # Open the file and send it to the client
            with open(self.path, 'r') as f:
                self.request.sendall(b"HTTP/1.1 200 OK\r\n")
                self.request.sendall(b"Content-Type: %s\r\n" % self.mime_type)
                self.request.sendall(f.read().encode())
                f.close()

        # If the start of data does not contain GET, return 405
        else:
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n")

        # Close the connection
        self.request.close()


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
