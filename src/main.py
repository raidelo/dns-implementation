from cli import argument_parser
from comms import send_query
from low.parse import DNSMessage
from parsing import parse_server_string

ERR = "\x1b[1;32merror:\x1b[0m"


def main() -> int:
    args = argument_parser().parse_args()

    try:
        upstream_server = parse_server_string(args.server)
    except ValueError as e:
        print(f"{ERR} {e.args[0]}")
        return 1

    resp = send_query(
        server=upstream_server,
        domains=args.domains,
        qtype=args.qtype,
        qclass=args.qclass,
        recursive=args.recursive,
    )

    parsed = DNSMessage.from_raw_bytes(resp)

    __import__("pprint").pprint(parsed)

    return 0


if __name__ == "__main__":
    exit(main())
