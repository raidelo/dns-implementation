from ipaddress import AddressValueError, IPv4Address

from types_ import UpstreamServer

DEFAULT_REMOTE_PORT = 53


def parse_server_string(address: str) -> UpstreamServer:
    address, port = address.split(":", 1)

    try:
        naddress = IPv4Address(address)
    except AddressValueError:
        raise ValueError(f"Invalid IPv4 format: {address}")

    if port:
        try:
            nport = int(port)
            if nport <= 0 or nport > 65535:
                raise ValueError()
        except ValueError:
            raise ValueError(f"Invalid port: {port}")
    else:
        nport = DEFAULT_REMOTE_PORT

    return UpstreamServer(naddress, nport)
