
import unittest

from core import (
    parse_request,
    parse_response,
    extract_metadata,
    RequestParseError,
    ResponseParseError,
)


class RequestParserTests(unittest.TestCase):

    def test_valid_request(self):
        raw = (
            b"GET /index.html HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Accept: text/html\r\n"
            b"\r\n"
        )

        request, body = parse_request(raw)

        self.assertEqual(request.method, "GET")
        self.assertEqual(request.target, "/index.html")
        self.assertEqual(request.version, "HTTP/1.1")
        self.assertEqual(request.get_header("Host"), "example.com")
        self.assertEqual(body, b"")

    def test_request_body_preserved(self):
        raw = (
            b"POST /submit HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"\r\n"
            b"hello"
        )

        request, body = parse_request(raw)

        self.assertEqual(request.method, "POST")
        self.assertEqual(body, b"hello")

    def test_duplicate_headers(self):
        raw = (
            b"GET / HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Accept: text/html\r\n"
            b"Accept: application/json\r\n"
            b"\r\n"
        )

        request, _ = parse_request(raw)

        self.assertEqual(
            request.get_all_headers("Accept"),
            ("text/html", "application/json")
        )

    def test_invalid_request(self):
        with self.assertRaises(RequestParseError):
            parse_request(b"INVALID\r\n\r\n")

    def test_unsupported_request_version(self):
        with self.assertRaises(RequestParseError):
            parse_request(b"GET / HTTP/2.0\r\n\r\n")


class ResponseParserTests(unittest.TestCase):

    def test_valid_response(self):
        raw = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"Server: example\r\n"
            b"\r\n"
            b"<html></html>"
        )

        response, body = parse_response(raw)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")
        self.assertEqual(response.content_type, "text/html")
        self.assertTrue(response.is_success)
        self.assertEqual(body, b"<html></html>")

    def test_redirect_response(self):
        raw = (
            b"HTTP/1.1 301 Moved Permanently\r\n"
            b"Location: https://example.com/new\r\n"
            b"\r\n"
        )

        response, _ = parse_response(raw)

        self.assertTrue(response.is_redirect)
        self.assertEqual(
            response.redirect_location,
            "https://example.com/new"
        )

    def test_error_response(self):
        raw = (
            b"HTTP/1.1 404 Not Found\r\n"
            b"\r\n"
        )

        response, _ = parse_response(raw)

        self.assertTrue(response.is_error)
        self.assertFalse(response.is_success)

    def test_invalid_response(self):
        with self.assertRaises(ResponseParseError):
            parse_response(b"INVALID\r\n\r\n")


class MetadataTests(unittest.TestCase):

    def test_html_metadata(self):
        html = b"""
        <html>
            <head>
                <title>Example Page</title>
                <meta name="description" content="Example description">
                <link rel="canonical" href="/canonical">
            </head>
            <body>
                <a href="/page1">Page 1</a>
                <a href="https://other.com">Other</a>
            </body>
        </html>
        """

        metadata = extract_metadata(
            html,
            "text/html",
            "https://example.com/"
        )

        self.assertEqual(metadata.title, "Example Page")
        self.assertEqual(metadata.description, "Example description")
        self.assertEqual(
            metadata.canonical_url,
            "https://example.com/canonical"
        )
        self.assertIn(
            "https://example.com/page1",
            metadata.links
        )
        self.assertIn(
            "https://other.com",
            metadata.links
        )
        self.assertTrue(metadata.is_html)

    def test_non_html_content(self):
        metadata = extract_metadata(
            b'{"hello": "world"}',
            "application/json"
        )

        self.assertFalse(metadata.is_html)
        self.assertIsNone(metadata.title)

    def test_missing_metadata(self):
        metadata = extract_metadata(
            b"<html><body>Hello</body></html>",
            "text/html"
        )

        self.assertIsNone(metadata.title)
        self.assertIsNone(metadata.description)
        self.assertEqual(metadata.links, ())


if __name__ == "__main__":
    unittest.main()
