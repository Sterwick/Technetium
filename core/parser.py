import re

from core.config import (
    MAX_HEADER_SIZE,
    SUPPORTED_HTTP_VERSIONS,
    HEADER_ENCODING,
)

from core.requests import HTTPRequest


HEADER_NAME_PATTERN = re.compile(
    rb"[!#$%&'*+\-.^_`|~0-9A-Za-z]+"
)


class RequestParseError(Exception):
    pass


def parse_request(raw_data: bytes):
    if not isinstance(raw_data, bytes):
        raise RequestParseError("Request must be bytes")

    if len(raw_data) > MAX_HEADER_SIZE and b"\r\n\r\n" not in raw_data:
        raise RequestParseError("Request headers too large")

    separator = raw_data.find(b"\r\n\r\n")

    if separator == -1:
        if len(raw_data) >= MAX_HEADER_SIZE:
            raise RequestParseError("Request headers too large")

        raise RequestParseError("Incomplete request headers")

    if separator > MAX_HEADER_SIZE:
        raise RequestParseError("Request headers too large")

    header_data = raw_data[:separator]
    remaining_data = raw_data[separator + 4:]

    try:
        lines = header_data.split(b"\r\n")

        request_line = lines[0].decode(HEADER_ENCODING)
        parts = request_line.split()

        if len(parts) != 3:
            raise RequestParseError("Invalid request line")

        method, target, version = parts

        if not method.isascii() or not method.isalpha():
            raise RequestParseError("Invalid HTTP method")

        if version not in SUPPORTED_HTTP_VERSIONS:
            raise RequestParseError("Unsupported HTTP version")

        headers = []

        for line in lines[1:]:
            if not line:
                continue

            if line.startswith((b" ", b"\t")):
                raise RequestParseError(
                    "Obsolete folded headers are not supported"
                )

            if b":" not in line:
                raise RequestParseError("Invalid header")

            name, value = line.split(b":", 1)

            if not HEADER_NAME_PATTERN.fullmatch(name):
                raise RequestParseError("Invalid header name")

            headers.append((
                name.decode(HEADER_ENCODING),
                value.strip(b" \t").decode(HEADER_ENCODING)
            ))

        request = HTTPRequest(
            method=method,
            target=target,
            version=version,
            headers=tuple(headers),
        )

        return request, remaining_data

    except UnicodeDecodeError as error:
        raise RequestParseError(
            "Invalid request encoding"
        ) from error
