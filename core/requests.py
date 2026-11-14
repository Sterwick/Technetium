from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class HTTPRequest:
    method: str
    target: str
    version: str
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
