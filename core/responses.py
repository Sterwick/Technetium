
import re

from dataclasses import dataclass
from typing import Tuple

from core.config import (
    MAX_HEADER_SIZE,
    SUPPORTED_HTTP_VERSIONS,
    HEADER_ENCODING,
)


HEADER_NAME_PATTERN = re.compile(
    rb"[!#$%&'*+\-.^_`|~0-9A-Za-z]+"
)


from core.errors import ResponseParseError


@dataclass(frozen=True)
class HTTPResponse:
    version: str
    status_code: int
    reason: str
    headers: Tuple[Tuple[str, str], ...]

    def get_header(self, name: str):
        name = name.lower()

        for key, value in self.headers:
            if key.lower() == name:
                return value

        return None

    def get_all_headers(self, name: str):
        name = name.lower()

        return tuple(
            value for key, value in self.headers
            if key.lower() == name
        )

    @property
    def content_type(self):
        value = self.get_header("Content-Type")

        if value is None:
            return None

        return value.split(";", 1)[0].strip()

    @property
    def is_redirect(self):
        return 300 <= self.status_code < 400

    @property
    def redirect_location(self):
        if not self.is_redirect:
            return None

        return self.get_header("Location")

    @property
    def is_success(self):
        return 200 <= self.status_code < 300

    @property
    def is_error(self):
        return self.status_code >= 400


def parse_response(raw_data: bytes):
    if not isinstance(raw_data, bytes):
        raise ResponseParseError("Response must be bytes")

    if len(raw_data) > MAX_HEADER_SIZE and b"\r\n\r\n" not in raw_data:
        raise ResponseParseError("Response headers too large")

    separator = raw_data.find(b"\r\n\r\n")

    if separator == -1:
        if len(raw_data) >= MAX_HEADER_SIZE:
            raise ResponseParseError("Response headers too large")

        raise ResponseParseError("Incomplete response headers")

    if separator > MAX_HEADER_SIZE:
        raise ResponseParseError("Response headers too large")

    header_data = raw_data[:separator]
    remaining_data = raw_data[separator + 4:]

    try:
        lines = header_data.split(b"\r\n")
        status_line = lines[0].decode(HEADER_ENCODING)

        parts = status_line.split(" ", 2)

        if len(parts) < 2:
            raise ResponseParseError("Invalid status line")

        version = parts[0]
        status_code_text = parts[1]
        reason = parts[2] if len(parts) == 3 else ""

        if version not in SUPPORTED_HTTP_VERSIONS:
            raise ResponseParseError("Unsupported HTTP version")

        if not re.fullmatch(r"[0-9]{3}", status_code_text):
            raise ResponseParseError("Invalid status code")

        status_code = int(status_code_text)

        if status_code < 100 or status_code > 599:
            raise ResponseParseError("Invalid status code")

        headers = []

        for line in lines[1:]:
            if not line:
                continue

            if line.startswith((b" ", b"\t")):
                raise ResponseParseError(
                    "Obsolete folded headers are not supported"
                )

            if b":" not in line:
                raise ResponseParseError("Invalid header")

            name, value = line.split(b":", 1)

            if not HEADER_NAME_PATTERN.fullmatch(name):
                raise ResponseParseError("Invalid header name")

            headers.append((
                name.decode(HEADER_ENCODING),
                value.strip(b" \t").decode(HEADER_ENCODING)
            ))

        response = HTTPResponse(
            version=version,
            status_code=status_code,
            reason=reason,
            headers=tuple(headers),
        )

        return response, remaining_data

    except UnicodeDecodeError as error:
        raise ResponseParseError(
            "Invalid response encoding"
        ) from error
