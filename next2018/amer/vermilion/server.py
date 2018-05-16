#!/usr/bin/python

import socket
import SocketServer
import re
from subprocess import call
import os
from sets import Set

library_cache_ = Set()

def update_package_cache():
  os.system("cp -rn /usr/lib64/python2.7/site-packages/* /var/lib/docker/volumes/my-vol/_data/site-packages/")

def exec_cmd(script):
  os.system("docker run -v my-vol:/app continuumio/anaconda:latest python -c '" + script + "'")

class MyTCPHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    self.script = self.request.recv(1024).strip()

    # Ensure all libraries required for this script are installed.
    libraries = re.findall('import (.*)', self.script)
    for library in libraries:
      if library in library_cache_:
        print "Found in cache: " + library
        continue
      library_cache_.add(library)
      print "Caching library: " + library
      os.system("pip install " + library + " 2> /dev/null 1> /dev/null")
    update_package_cache()

    # Point this script to the package cache
    self.script = "sys.path.append(\"/app/site-packages\")\n" + self.script
    if "sys" not in libraries:
      self.script = "import sys\n" + self.script

    exec_cmd(self.script)

class MyTCPServer(SocketServer.TCPServer):
  def server_bind(self):
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind(self.server_address)

server = MyTCPServer(("10.21.73.97", 9998), MyTCPHandler)
server.serve_forever()
