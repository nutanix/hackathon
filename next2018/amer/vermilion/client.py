#!/usr/local/bin/python

import socket
import sys
import re

HOST, PORT = "10.21.73.97", 9998
file_name = str(sys.argv[1])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print "Sending nano script: " + file_name
with open(file_name, 'r') as f:
  payload = f.read()

try:
    sock.connect((HOST, PORT))
    sock.sendall(payload + "\n")

    # Receive data from the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()

print "Received: {}".format(received)
