from typing import List, Optional
from mistake.parser.ast import *
from enum import Enum
from mistake.runtime.errors.runtime_errors import InvalidLifetimeError
from datetime import datetime
import time
from mistake.utils import to_decimal_seconds
from mistake.runtime import environment as rte
import gevent
import socket
import re

class MLType:
    def to_string(self):
        raise NotImplementedError("to_string method not implemented")

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


class RuntimeUnit(MLType):
    def __init__(self, _=None):
        pass

    def to_string(self):
        return "Null"


class RuntimeNumber(MLType):
    def __init__(self, value: float):
        self.value = value

    def to_string(self):
        return f"{self.value}"


class RuntimeString(MLType):
    def __init__(self, value: str):
        self.value = value

    def to_string(self):
        return f'{self.value}'


class RuntimeBoolean(MLType):
    def __init__(self, value: bool | str):
        self.value = value in ["true", "True", True]

    def to_string(self):
        return "true" if self.value else "false"

    def __eq__(self, other):
        ov = other.value if isinstance(other, RuntimeBoolean) else other
        return self.value == ov


class Function(MLType):
    def __init__(self, parameter: str, body: List[ASTNode], impure: bool = False):
        self.param = parameter
        self.body = body
        self.impure = impure

    def to_string(self):
        return (
            f"{'Impure' if self.impure else ''}Function({self.param}, body={self.body})"
        )


class ClassType(MLType):
    def __init__(self, members: dict[str, MLType], public_members: set[str]):
        self.members = members
        self.public_members = public_members

    def to_string(self):
        return f"Class(fields={self.members}, public_fields={self.public_members})"



class ClassInstance(MLType):
    def __init__(
        self,
        class_type: ClassType,
        members: dict[str, MLType],
        environment: "rte.Environment",
    ):
        self.class_type = class_type
        self.members = members

        self.environment = environment
        # print("CLASS INSTANCE ENVIRONMENT", self.environment)

    def to_string(self):
        return f"InstanceOf({self.class_type.name}, fields={self.members})"

class ClassMemberReference(MLType):
    def __init__(self, instance: ClassInstance, member_name: str):
        self.instance = instance
        self.member_name = member_name

    def to_string(self):
        return f"ClassMemberReference({self.instance}, {self.member_name})"

    def get(self):
        # Get the actual value from the instance
        return self.instance.members[self.member_name]

    def set(self, value: MLType):
        # Update the instance's member
        self.instance.members[self.member_name] = value
        return RuntimeUnit()

class BuiltinFunction(MLType):
    def __init__(self, func: callable, imp=True, subtype=None):
        self.func = func
        self.impure = imp
        self.subtype = subtype
        self.subdata = {}

    def to_string(self):
        return f"BuiltinFunction({self.func}, impure={self.impure})"


class LifetimeType(Enum):
    DMS_TIMESTAMP = 0  # given in miliseconds since jan 1st 2020
    DECIMAL_SECONDS = 1
    LINES = 2
    INFINITE = 3
    TICKS = 4


def get_timestamp():
    reference_date = datetime(2020, 1, 1)
    current_time = datetime.now()
    time_difference = current_time - reference_date
    milliseconds = int(time_difference.total_seconds() * 1000)
    decimal_milliseconds = int(to_decimal_seconds(milliseconds))
    return decimal_milliseconds


class Lifetime(MLType):
    def __init__(self, type: LifetimeType, value: float, start: float = 0):
        self.value = value
        self.type = type
        self.start = start

        if self.value < 0:
            raise InvalidLifetimeError("Lifetime value must be greater than 0")
        if int(self.value) != self.value and self.type in [
            LifetimeType.LINES,
            LifetimeType.DMS_TIMESTAMP,
        ]:
            raise InvalidLifetimeError("Lifetime value must be an integer")
        elif int(self.value) == self.value:
            self.value = int(self.value)

    def to_string(self):
        return f"Lifetime({self.value}, {self.type})"

    def is_expired(self, line=None):
        match self.type:
            case LifetimeType.INFINITE:
                return False
            case LifetimeType.DMS_TIMESTAMP:
                return get_timestamp() >= self.value
            case LifetimeType.DECIMAL_SECONDS:
                return (
                    to_decimal_seconds(time.process_time()) - self.start >= self.value
                )  # 0.864 is the conversion from seconds to decimal seconds
            case LifetimeType.TICKS:
                return time.process_time() * 20 - self.start >= self.value
            case LifetimeType.LINES:
                if line is None:
                    raise InvalidLifetimeError(
                        "Line number must be provided for line lifetime"
                    )
                return line - self.start >= self.value
    
class RuntimeMutableBox(MLType):
    def __init__(self, value: any):   
        self.value = value
        
    def to_string(self):
        return f"MutableBox({self.value})"
    
    def write(self, value):
        self.value = value
        return RuntimeUnit()
    
class RuntimeListType(MLType):
    def __init__(self, list: dict[int, MLType]):
        self.list = list
    
    def get(self, idx: int):
        if idx < 1 or int(idx) != idx:
            raise IndexError("Index must be an integer greater than 0")
        return self.list.get(idx, RuntimeUnit())
    
    def length(self):
        i = 0
        while (i+1) in self.list:
            i += 1
        return RuntimeNumber(i)
    
    def set(self, idx: int, value: MLType):
        if idx < 1 or int(idx) != idx:
            raise IndexError("Index must be an integer greater than 0")
        self.list[idx] = value
        return RuntimeUnit()
    
    def to_string(self):
        return f"List({self.list})"
    
class RuntimeMatchObject(MLType):
    def __init__(self, match: re.Match):
        self.match = match
    
    def to_string(self):
        return f"MatchObject({self.match})"

class RuntimeChannel(MLType):
    def __init__(self, id: int, sent_callback: callable = lambda _: None, recieve_callback: callable = lambda: None):
        self.id = id
        self.sent_callback: callable = sent_callback
        self.receive_callback: callable = recieve_callback
        self.values: List[MLType] = []
    
    def send(self, value: MLType):
        self.values.append(value)
        self.sent_callback(value)
    
    def receive(self):
        self.receive_callback()

        while len(self.values) == 0:
            #print(self.channels[id])
            gevent.sleep(0.01)
        return self.values.pop(0)
    
    def to_string(self):
        return f"Channel({self.id})"
    
    
class RuntimeTask(MLType):
    def __init__(self, task_ref: gevent.Greenlet):
        self.task_ref = task_ref
        
    def kill(self):
        if self.task_ref:
            self.task_ref.kill()
            
    def to_string(self):
        return f"Task({self.task_ref})"
    
    
# NETWORKING
# ADD NEW CLASSES HERE

class RuntimeServer:
    def set_callback(self, callback: callable):
        raise NotImplementedError("Must implement set_callback method")

class RuntimeSocket:
    buffer_size = 1024
    
    def send(self, message: str):
        raise NotImplementedError("Must implement send method")
    
    def close(self):
        raise NotImplementedError("Must implement close method")
    
    def receive(self):
        raise NotImplementedError("Must implement recieve method")

class RuntimeUDPServer(RuntimeServer):
    def __init__(self, runtime):
        self.runtime = runtime
        self.hostname: str = None
        self.port: int = None
        self.socket: socket.socket = None
        self.listen_task = None
        self.callback: callable = None
        self.callback_task = None
        
        
    def set_hostname(self, hostname):
        hostname, port = hostname.value.split(":")
        
        self.hostname = hostname
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.hostname, self.port))
        
        def listen():
            while True:
                try:
                    self.receive()
                except gevent._socketcommon.cancel_wait_ex as e:
                    break
                gevent.sleep(0.01)
        self.listen_task = gevent.spawn(listen)
        
        self.runtime.add_task(self.listen_task)
                
        return RuntimeBoolean(True)

    def receive(self, buffer_size=1024):
        if not self.socket:
            return RuntimeBoolean(False)
        data = self.socket.recvfrom(buffer_size)[0]
        message = data.decode()
        if self.callback: 
            task = gevent.spawn(self.callback, RuntimeString(message))
            self.runtime.add_task(task)
            self.callback_task = task

    def set_callback(self, callback: callable):
        self.callback = callback
        return RuntimeUnit()

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.listen_task:
            self.listen_task.kill()
            self.listen_task = None
        if self.callback_task:
            self.callback_task.kill()
            self.callback_task = None
        return RuntimeBoolean(True)
    
    def kill(self):
        self.close()

    def to_string(self):
        return f"UDPServer(hostname={self.hostname}, port={self.port})"
    
    
class RuntimeUDPSocket(RuntimeSocket):
    def __init__(self, runtime):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.runtime = runtime
        self.hostname = None
        self.port: int = None
    def set_hostname(self, hostname: str):
        self.hostname, self.port = hostname.value.split(":")
    
        self.socket.connect((self.hostname, int(self.port)))
        
    def send(self, message: RuntimeString):
        if not self.socket:
            return RuntimeBoolean(False)
        value = message.value.encode()
        self.socket.send(value)
        return RuntimeBoolean(True)
    
    def close(self):
        self.socket.close()
        return RuntimeBoolean(True)
    
    def kill(self):
        self.close()
    
    def receive(self):
        return RuntimeUnit()
    
    def to_string(self):
        return f"UDPSocket(id={self.id})"
    
    
class RuntimeTCPServer(RuntimeServer):
    def __init__(self, runtime):
        self.runtime = runtime
        self.hostname: str = None
        self.port: int = None
        self.socket: socket.socket = None
        self.listen_task = None
        self.callback: callable = None
        self.callback_task = None

    def bind_port(self, port: RuntimeString):
        self.hostname = "127.0.0.1"
        self.port = int(port.value)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(5)
        
        def listen():
            while True:
                try:
                    self.receive()
                except gevent._socketcommon.cancel_wait_ex as e:
                    break
                                
        self.listen_task = gevent.spawn(listen)
        self.runtime.add_task(self.listen_task)
        
        
        return RuntimeBoolean(True)

    def receive(self, buffer_size=1024):
        if not self.socket:
            return RuntimeBoolean(False)
        
        client_socket, client_address = self.socket.accept()
        
        new_sock = RuntimeTCPSocket(self.runtime)
        new_sock.set_socket(client_socket)

        if self.callback:
            self.callback_task = gevent.spawn(self.callback, new_sock)
            self.runtime.add_task(self.callback_task)
        return RuntimeUnit()

    def set_callback(self, callback: callable):
        self.callback = callback
        return RuntimeUnit()

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.listen_task:
            self.listen_task.kill()
            self.listen_task = None
        if self.callback_task:
            self.callback_task.kill()
            self.callback_task = None
        return RuntimeBoolean(True)
    
    def kill(self):
        self.close()

    def to_string(self):
        return f"TCPServer(hostname={self.hostname}, port={self.port})"
    
    
class RuntimeTCPSocket(RuntimeSocket):
    def __init__(self, runtime):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channel: Optional[RuntimeChannel] = None
        self.runtime = runtime
        self.hostname: Optional[str] = None
        self.port: Optional[int] = None

    def set_port(self, port: RuntimeString):
        try:
            self.hostname = socket.gethostname()
            self.port = int(port.value)
            self.socket.connect((self.hostname, self.port))
        except Exception as e:
            self.close()

    def set_socket(self, socket: socket.socket):
        self.socket = socket

    def send(self, message: RuntimeString):
        if not self.socket:
            return RuntimeBoolean(False)
        try:
            value = message.value.encode()
            self.socket.send(value)
            return RuntimeBoolean(True)
        except Exception as e:
            print(f"Error sending message: {e}")
            return RuntimeBoolean(False)

    def close(self):
        try:
            self.socket.close()
            if self.channel:
                self.runtime.close_channel(self.channel)
            return RuntimeBoolean(True)
        except Exception as e:
            print(f"Error closing socket: {e}")
            return RuntimeBoolean(False)

    def kill(self):
        self.close()

    def receive(self):
        try:
            data = self.socket.recv(1024)
            return RuntimeString(data.decode())
        except Exception as e:
            print(f"Error receiving data: {e}")
            return RuntimeString("")

    def to_string(self):
        return f"TCPSocket(hostname={self.hostname}, port={self.port})"