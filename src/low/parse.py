from dataclasses import dataclass
from typing import Callable


type Ptr = int


@dataclass
class DNSHeader:
    ID: int  # 2 byte
    QR: int  # 1 bit
    OPCODE: int  # 4 bit
    AA: int  # 1 bit
    TC: int  # 1 bit
    RD: int  # 1 bit
    RA: int  # 1 bit
    Z: int  # 3 bit
    RCODE: int  # 4 bit
    QDCOUNT: int  # 2 bytes
    ANCOUNT: int  # 2 bytes
    NSCOUNT: int  # 2 bytes
    ARCOUNT: int  # 2 bytes

    def to_bytes(self) -> bytes:
        return (
            self.ID.to_bytes(2)
            + (
                self.QR << 15
                | self.OPCODE << 11
                | self.AA << 10
                | self.TC << 9
                | self.RD << 8
                | self.RA << 7
                | self.Z << 4
                | self.RCODE
            ).to_bytes(2)
            + self.QDCOUNT.to_bytes(2)
            + self.ANCOUNT.to_bytes(2)
            + self.NSCOUNT.to_bytes(2)
            + self.ARCOUNT.to_bytes(2)
        )


@dataclass
class DNSQuestion:
    QNAME: bytes  # variable bytes
    QTYPE: bytes  # 2 bytes
    QCLASS: bytes  # 2 bytes

    def to_bytes(self) -> bytes:
        return self.QNAME + self.QTYPE + self.QCLASS


@dataclass
class DNSResourceRecord:
    NAME: bytes  # variable bytes
    TYPE: bytes  # 2 bytes
    CLASS: bytes  # 2 bytes
    TTL: bytes  # 4 bytes
    RDLENGTH: bytes  # 2 bytes
    RDATA: bytes  # variable bytes

    def to_bytes(self) -> bytes:
        return (
            self.NAME + self.TYPE + self.CLASS + self.TTL + self.RDLENGTH + self.RDATA
        )


@dataclass
class DNSMessage:
    Header: DNSHeader
    Question: list[DNSQuestion]
    Answer: list[DNSResourceRecord]
    Authority: list[DNSResourceRecord]
    Additional: list[DNSResourceRecord]

    @classmethod
    def from_raw_bytes(cls, data: bytes) -> "DNSMessage":
        parsed = ResponseParser(data)
        return DNSMessage(
            Header=parsed.header,
            Question=parsed.question_section,
            Answer=parsed.answer_section,
            Authority=parsed.authority_section,
            Additional=parsed.additional_section,
        )

    def to_bytes(self) -> bytes:
        return (
            self.Header.to_bytes()
            + b"".join([r.to_bytes() for r in self.Question])
            + b"".join([r.to_bytes() for r in self.Answer])
            + b"".join([r.to_bytes() for r in self.Authority])
            + b"".join([r.to_bytes() for r in self.Additional])
        )


class ResponseParser:
    def __init__(self, data: bytes):
        self.response = data

        self._raw_headers = self.response[:12]
        self.header: DNSHeader = self._parse_headers(self._raw_headers)

        self._ptr = 12

        self._raw_question_section, self.question_section = (
            self._parse_question_section()
        )

        self._raw_answer_section, self.answer_section = self._parse_answer_section()

        self._raw_authority_section, self.authority_section = (
            self._parse_authority_section()
        )

        self._raw_additional_section, self.additional_section = (
            self._parse_additional_section()
        )

    def _parse_headers(self, data: bytes) -> DNSHeader:
        return DNSHeader(
            ID=int.from_bytes(data[:2]),
            QR=data[2] & 0x10000000 >> 7,
            OPCODE=data[2] & 0x01111000 >> 3,
            AA=data[2] & 0x00000100 >> 2,
            TC=data[2] & 0x00000010 >> 1,
            RD=data[2] & 0x00000001,
            RA=data[3] & 0x10000000 >> 7,
            Z=data[3] & 0x01110000 >> 4,
            RCODE=data[3] & 0x00001111,
            QDCOUNT=int.from_bytes(data[4:6]),
            ANCOUNT=int.from_bytes(data[6:8]),
            NSCOUNT=int.from_bytes(data[8:10]),
            ARCOUNT=int.from_bytes(data[10:12]),
        )

    def _parse_question_section(self) -> tuple[bytes, list[DNSQuestion]]:
        return self._parse_helper(
            _extract_questions,
            self.header.QDCOUNT,
        )

    def _parse_answer_section(self) -> tuple[bytes, list[DNSResourceRecord]]:
        return self._parse_helper(
            _extract_resource_records,
            self.header.ANCOUNT,
        )

    def _parse_authority_section(self) -> tuple[bytes, list[DNSResourceRecord]]:
        return self._parse_helper(
            _extract_resource_records,
            self.header.NSCOUNT,
        )

    def _parse_additional_section(self) -> tuple[bytes, list[DNSResourceRecord]]:
        return self._parse_helper(
            _extract_resource_records,
            self.header.ARCOUNT,
        )

    def _parse_helper[T: DNSQuestion | DNSResourceRecord](
        self,
        f: Callable[[bytes, Ptr, int], tuple[Ptr, list[T]]],
        count: int,
    ) -> tuple[bytes, list[T]]:
        end_ptr, records = f(
            self.response,
            self._ptr,
            count,
        )

        raw_section = self.response[self._ptr : end_ptr]

        self._ptr = end_ptr

        return raw_section, records


def _extract_questions(
    data: bytes,
    ptr: Ptr,
    qdcount: int,
) -> tuple[Ptr, list[DNSQuestion]]:
    records: list[DNSQuestion] = []
    for _ in range(0, qdcount):
        ptr, qname = _extract_qname(data, ptr)
        records.append(
            DNSQuestion(
                QNAME=qname,
                QTYPE=data[ptr : ptr + 2],
                QCLASS=data[ptr + 2 : ptr + 4],
            )
        )
        ptr += 4

    return ptr, records


def _extract_resource_records(
    data: bytes,
    ptr: Ptr,
    xxcount: int,
) -> tuple[Ptr, list[DNSResourceRecord]]:
    resource_records: list[DNSResourceRecord] = []
    for _ in range(0, xxcount):
        ptr, question = _extract_questions(data, ptr, 1)

        name = question[0].QNAME
        type_ = question[0].QTYPE
        class_ = question[0].QCLASS

        ttl = data[ptr : ptr + 4]
        ptr += 4

        rdlength = data[ptr : ptr + 2]
        rdlength_int = int.from_bytes(rdlength)
        ptr += 2

        rdata = data[ptr : ptr + rdlength_int]
        ptr += rdlength_int

        resource_records.append(
            DNSResourceRecord(
                NAME=name,
                TYPE=type_,
                CLASS=class_,
                TTL=ttl,
                RDLENGTH=rdlength,
                RDATA=rdata,
            )
        )

    return ptr, resource_records


def _extract_qname(data: bytes, ptr: Ptr) -> tuple[Ptr, bytes]:
    qname_parts: list[bytes] = []
    base_ptr = ptr
    while True:
        part_len = data[ptr]
        if part_len == 0:
            return base_ptr + 1, b".".join(qname_parts)
        elif part_len & 0b11000000 == 0b11000000:
            ptr = (part_len & 0x00111111) << 8 | data[ptr + 1]
            base_ptr += 1
            continue
        else:
            ptr += 1
            part = data[ptr : ptr + part_len]
            ptr += part_len
            qname_parts.append(part)
            if ptr > base_ptr:
                base_ptr = ptr
