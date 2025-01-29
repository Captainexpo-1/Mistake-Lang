from mistake.runtime.runtime_types import (
    RuntimeUDPServer,
    RuntimeUDPSocket,
    RuntimeTCPServer,
    RuntimeTCPSocket,
)


def create_UDP_server(arg, env, runtime):
    return RuntimeUDPServer(runtime)


def create_UDP_socket(arg, env, runtime):
    return RuntimeUDPSocket(runtime)


def create_TCP_server(arg, env, runtime):
    return RuntimeTCPServer(runtime)


def create_TCP_socket(arg, env, runtime):
    return RuntimeTCPSocket(runtime)
