from dataclasses import dataclass
from ipaddress import AddressValueError, IPv4Address

DEFAULT_REMOTE_PORT = 53


@dataclass
class UpstreamServer:
    address: IPv4Address
    port: int

    @classmethod
    def from_str(cls, address: str) -> "UpstreamServer":
        address, sep, port = address.partition(":")

        try:
            naddress = IPv4Address(address)
        except (AddressValueError, ValueError):
            raise ValueError(f"Invalid IPv4 format: {address}")

        if sep and port:
            try:
                nport = int(port)
                if not (0 < nport <= 65535):
                    raise ValueError()
            except ValueError:
                raise ValueError(f"Invalid port: {port}")
        else:
            nport = DEFAULT_REMOTE_PORT

        return cls(naddress, nport)
