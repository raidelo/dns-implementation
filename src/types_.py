from dataclasses import dataclass


@dataclass
class UpstreamServer:
    address: str
    port: int
