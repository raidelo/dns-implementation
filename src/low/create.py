from random import randint

from low.parse import DNSHeader, DNSMessage, DNSQuestion

from .constants import QCLASS_MAPPING, QTYPE_MAPPING


def _create_header(domains: list[str], recursive: bool = True) -> bytes:
    id = randint(0, 2**16 - 1).to_bytes(2)  # ID
    qr_opcode_aa_tc_rd_ra_z_rcode = int(
        "".join(
            [
                "0",  # QR
                "0000",  # Opcode
                "0",  # AA
                "0",  # TC
                str(1 if recursive else 0),  # RD
                "0",  # RA
                "000",  # FUTURE USE
                "0000",  # RCODE
            ]
        ),
        2,
    ).to_bytes(2)
    qdcount = len(domains).to_bytes(2)
    ancount = int("0" * 16, 2).to_bytes(2)
    nscount = int("0" * 16, 2).to_bytes(2)
    arcount = int("0" * 16, 2).to_bytes(2)

    return b"".join(
        [id, qr_opcode_aa_tc_rd_ra_z_rcode, qdcount, ancount, nscount, arcount]
    )


def _create_query(domain: bytes, qtype: bytes, qclass: bytes) -> bytes:
    return b"".join([domain, qtype, qclass])


def _get_domain_encoded(domain: str) -> bytes:
    ret = b""
    for sub_domain in domain.split("."):
        sub_domain_len = len(sub_domain)
        if sub_domain_len > 63:
            raise OverflowError(
                f"Invalid sub-domain length of {sub_domain_len} bytes. Maximum length is 63 bytes."
            )
        ret += sub_domain_len.to_bytes() + sub_domain.encode()
    ret += b"\x00"
    domain_name_len = len(ret)
    if domain_name_len > 255:
        raise OverflowError(
            f"Invalid domain name length of {domain_name_len} bytes. Maximum length is 255 bytes."
        )
    return ret


def _get_qtype_encoded(qtype: str) -> bytes:
    try:
        return QTYPE_MAPPING[qtype].to_bytes(2)
    except KeyError:
        raise KeyError(f"Invalid QTYPE: {qtype}")


def _get_qclass_encoded(qclass: str) -> bytes:
    try:
        return QCLASS_MAPPING[qclass].to_bytes(2)
    except KeyError:
        raise KeyError(f"Invalid QCLASS: {qclass}")


def create_request(
    domains: list[str],
    qtype: str = "A",
    qclass: str = "IN",
    recursive: bool = True,
) -> bytes:
    ret = _create_header(domains, recursive)
    for domain in domains:
        query = _create_query(
            _get_domain_encoded(domain),
            _get_qtype_encoded(qtype),
            _get_qclass_encoded(qclass),
        )
        ret += query
    request_len = len(ret)
    if request_len > 512:
        raise OverflowError(
            f"Invalid request length of {request_len} bytes. Maximum length is 512 bytes."
        )
    return ret


def make_question(
    domains: list[str],
    qtype: str = "A",
    qclass: str = "IN",
    recursive: bool = True,
) -> DNSMessage:
    h = DNSHeader(
        ID=randint(0, 2**16 - 1),
        QR=0,
        OPCODE=0,
        AA=0,
        TC=0,
        RD=int(recursive),
        RA=0,
        Z=0,
        RCODE=0,
        QDCOUNT=len(domains),
        ANCOUNT=0,
        NSCOUNT=0,
        ARCOUNT=0,
    )
    q = [
        DNSQuestion(
            _get_domain_encoded(d),
            _get_qtype_encoded(qtype),
            _get_qclass_encoded(qclass),
        )
        for d in domains
    ]

    return DNSMessage(Header=h, Question=q, Answer=[], Authority=[], Additional=[])
