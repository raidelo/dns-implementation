from cli import parse_args
from comms import send_message
from low.create import make_question
from low.parse import DNSMessage

ERR = "\x1b[1;31merror:\x1b[0m"


def main() -> int:
    args = parse_args()

    message = make_question(
        domains=args.domains,
        qtype=args.qtype,
        qclass=args.qclass,
        recursive=args.recursive,
    )

    try:
        resp = send_message(
            message=message,
            server=args.server,
        )
    except TimeoutError:
        print(f"{ERR} Timeout error")
        return 1

    parsed = DNSMessage.from_raw_bytes(resp)

    __import__("pprint").pprint(parsed)

    return 0


if __name__ == "__main__":
    exit(main())
