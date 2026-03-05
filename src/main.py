from cli import parse_args
from comms import send_message
from low.create import make_question
from low.parse import DNSMessage

ERR = "\x1b[1;32merror:\x1b[0m"


def main() -> int:
    args = parse_args()

    message = make_question(
        domains=args.domains,
        qtype=args.qtype,
        qclass=args.qclass,
        recursive=args.recursive,
    )

    resp = send_message(
        message=message,
        server=args.server,
    )

    parsed = DNSMessage.from_raw_bytes(resp)

    __import__("pprint").pprint(parsed)

    return 0


if __name__ == "__main__":
    exit(main())
