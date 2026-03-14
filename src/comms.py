import socket
from typing import Optional

from typing_extensions import deprecated

from low.create import create_request
from low.parse import DNSMessage
from types_ import UpstreamServer

CHUNK = 65536
TIMEOUT = 3


def _send_bytes(
    request: bytes,
    server: UpstreamServer,
    timeout: Optional[int] = None,
) -> bytes:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout or TIMEOUT)

    sock.sendto(request, (str(server.address), server.port))

    return sock.recv(CHUNK)


@deprecated("use send_message instead")
def send_query(
    server: UpstreamServer,
    domains: list[str],
    qtype: str = "A",
    qclass: str = "IN",
    recursive: bool = True,
    timeout: Optional[int] = None,
) -> bytes:
    req = create_request(domains, qtype, qclass, recursive)
    return _send_bytes(req, server, timeout)


def send_message(
    message: DNSMessage,
    server: UpstreamServer,
    timeout: Optional[int] = None,
) -> bytes:
    return _send_bytes(
        message.to_bytes(),
        server,
        timeout,
    )
