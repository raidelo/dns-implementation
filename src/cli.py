from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomNamespace:
    domains: list[str]
    server: str
    qtype: str
    qclass: str
    recursive: bool


def argument_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument("domains", nargs="+")

    parser.add_argument("-s", "--server", default="8.8.8.8:53", dest="server")

    parser.add_argument("-t", "--qtype", default="A", dest="qtype")
    parser.add_argument("-c", "--qclass", default="IN", dest="qclass")

    parser.add_argument(
        "-R",
        "--no-recursive",
        action="store_false",
        default=True,
        dest="recursive",
    )

    return parser


def parse_args() -> CustomNamespace:
    args = argument_parser().parse_args()
    return CustomNamespace(**vars(args))
