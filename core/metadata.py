
import codecs
import re

from dataclasses import dataclass
from email.message import Message
from html.parser import HTMLParser
from typing import Optional, Tuple
from urllib.parse import urljoin


@dataclass(frozen=True)
class PageMetadata:
    title: Optional[str]
    description: Optional[str]
    canonical_url: Optional[str]
    links: Tuple[str, ...]
    content_type: Optional[str]
    charset: Optional[str]
    is_html: bool


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.title = None
        self.description = None
        self.canonical_url = None
        self.links = []
        self.base_href = None
        self.og_title = None
        self._inside_title = False
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()

        if tag == "title":
            self._inside_title = True

        elif tag == "meta":
            name = (attrs.get("name") or "").lower()
            prop = (attrs.get("property") or "").lower()
            content = attrs.get("content")

            if content:
                if name == "description" and self.description is None:
                    self.description = content.strip()

                elif prop == "og:title" and self.og_title is None:
                    self.og_title = content.strip()

        elif tag == "base":
            if self.base_href is None:
                self.base_href = attrs.get("href")

        elif tag == "a":
            href = attrs.get("href")

            if href:
                self.links.append(href)

        elif tag == "link":
            rel = (attrs.get("rel") or "").lower().split()

            if "canonical" in rel and self.canonical_url is None:
                self.canonical_url = attrs.get("href")

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._inside_title = False

            if self.title is None:
                self.title = "".join(self._title_parts).strip()

    def handle_data(self, data):
        if self._inside_title:
            self._title_parts.append(data)


def _detect_charset(body, content_type):
    message = Message()
    message["content-type"] = content_type or "text/html"

    charset = message.get_content_charset()

    if charset:
        try:
            return codecs.lookup(charset).name
        except LookupError:
            pass

    if body.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"

    if body.startswith(codecs.BOM_UTF16_LE):
        return "utf-16"

    if body.startswith(codecs.BOM_UTF16_BE):
        return "utf-16"

    match = re.search(
        rb'<meta[^>]+charset\s*=\s*["\']?([a-zA-Z0-9._-]+)',
        body[:4096],
        re.IGNORECASE,
    )

    if match:
        try:
            return codecs.lookup(
                match.group(1).decode("ascii")
            ).name
        except LookupError:
            pass

    return "utf-8"


def extract_metadata(
    body: bytes,
    content_type: Optional[str] = None,
    base_url: Optional[str] = None,
):
    if not isinstance(body, bytes):
        raise TypeError("Response body must be bytes")

    message = Message()
    message["content-type"] = content_type or "application/octet-stream"

    media_type = message.get_content_type().lower()

    is_html = media_type in (
        "text/html",
        "application/xhtml+xml",
    )

    if not content_type:
        is_html = bool(
            re.search(
                rb"<(!doctype\s+html|html|head|body)(\s|>)",
                body[:1024],
                re.IGNORECASE,
            )
        )

    if not is_html:
        return PageMetadata(
            title=None,
            description=None,
            canonical_url=None,
            links=(),
            content_type=media_type,
            charset=None,
            is_html=False,
        )

    charset = _detect_charset(body, content_type)

    html = body.decode(charset, errors="replace")

    parser = MetadataParser()
    parser.feed(html)
    parser.close()

    title = parser.title or parser.og_title

    document_base = base_url or ""

    if parser.base_href:
        document_base = urljoin(
            document_base,
            parser.base_href,
        )

    links = tuple(dict.fromkeys(
        urljoin(document_base, link)
        for link in parser.links
    ))

    canonical_url = parser.canonical_url

    if canonical_url:
        canonical_url = urljoin(
            document_base,
            canonical_url,
        )

    return PageMetadata(
        title=title,
        description=parser.description,
        canonical_url=canonical_url,
        links=links,
        content_type=media_type,
        charset=charset,
        is_html=True,
    )
