from dataclasses import dataclass
from ipaddress import IPv4Address


@dataclass
class UpstreamServer:
    address: IPv4Address
    port: int
