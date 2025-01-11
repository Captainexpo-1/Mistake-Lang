import re
from mistake.runtime.errors.runtime_errors import *
from mistake.runtime.runtime_types import *
import mistake.runtime.environment as environment
import mistake.runtime.interpreter as interpreter
from mistake.parser.ast import *
import requests
from mistake.utils import *
import gevent
import socket

"""
# TCP Documentation
* <=#=> creates a TCP server.
    * Servers are task objects and can also be killed. When they are killed, they stop listening on its port and any running callbacks are killed too.
    * ==># binds the server to the port set by its argument. Returns true if successful and false otherwise.
    * ==>! sets the server's callback.
        * For TCP servers, the server callback is called asynchronously with a TCP socket object. Callbacks may be impure.

* <=#= creates a TCP socket.
    * If a connection could not be made, returns unit instead.
    * << on a TCP socket sends a string. Blocking.
        * Returns true if successful and false otherwise.
    * >|< closes the socket on a TCP socket.
    * >> on a TCP socket receives a string. Blocking.

# UDP Documentation
* <=?=> creates a UDP server.
    * Servers are task objects and can also be killed. When they are killed, they stop listening on its port and any running callbacks are killed too.
    * ==>? binds the server to the hostname set by its argument. Returns true if successful and false otherwise.
    * ==>! sets the server's callback.
        * For UDP servers, the server callback is called asynchronously with a string object containing the message content. Callbacks may be impure.

* <=?= creates a UDP socket.
    * If a connection could not be made, returns unit instead.
    * << on a UDP socket sends a string. Blocking.
        * Returns true if successful and false otherwise.
    * >|< closes the socket on a UDP socket.
    * >> on a UDP socket does nothing.
"""


def create_UDP_server(arg, env, runtime):
    return RuntimeUDPServer(runtime)

def create_UDP_socket(arg, env, runtime):
    return RuntimeUDPSocket(runtime)