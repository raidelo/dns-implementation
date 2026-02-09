import re

from types_ import UpstreamServer

SERVER_ADDRESS = re.compile(
    r"^((\d{1,2}|1\d{2}|2[0-5]{2})\.){3}(\d{1,2}|1\d{2}|2[0-5]{2})$"
)
SERVER_PORT = re.compile(r"^(\d|[1-9]\d{1,3}|[1-5]\d{4}|6[1-5]{2}[1-3][1-5])$")

DEFAULT_REMOTE_PORT = 53


def parse_server_string(address: str) -> UpstreamServer:
    address, _, port = address.partition(":")

    address_match = SERVER_ADDRESS.match(address)
    if not address_match:
        raise ValueError(f"Invalid IPv4 format: {address}")
    else:
        naddress = address_match.group()

    if port:
        port_match = SERVER_PORT.match(port)
        if not port_match:
            raise ValueError(f"Invalid port: {port}")
        else:
            nport = int(port_match.group())
    else:
        nport = DEFAULT_REMOTE_PORT

    return UpstreamServer(naddress, nport)
