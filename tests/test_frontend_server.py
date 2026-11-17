import json
from email.message import Message
from http.server import ThreadingHTTPServer
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from unittest.mock import patch

from servers import frontend_server


class URLValidationTests(unittest.TestCase):
    def test_accepts_public_http_and_https_urls(self):
        with patch.object(frontend_server, '_host_is_public', return_value=True):
            self.assertEqual(
                frontend_server.validate_url('https://example.test/path'),
                'https://example.test/path',
            )
            self.assertEqual(
                frontend_server.validate_url('http://example.test'),
                'http://example.test/',
            )

    def test_rejects_non_http_schemes_credentials_and_nonstandard_ports(self):
        for url in (
            'file:///etc/passwd',
            'https://user:password@example.test/',
            'http://example.test:8080/',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                frontend_server.validate_url(url)

    def test_rejects_local_and_private_destinations(self):
        for url in ('http://localhost/', 'http://127.0.0.1/', 'http://192.168.1.1/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                frontend_server.validate_url(url)


class SanitizationTests(unittest.TestCase):
    def test_sanitizes_markup_and_rewrites_relative_navigation_and_assets(self):
        source = (
            '<html><head><title>Example</title><base href="/docs/">'
            '<script>parent.document.body.innerHTML = "bad"</script>'
            '<link rel="stylesheet" href="site.css"></head><body>'
            '<a href="./guide">Read <b>the guide</b></a>'
            '<img src="../image.png" onerror="alert(1)">'
            '<script/><p>Visible</p></body></html>'
        )
        with patch.object(frontend_server, '_host_is_public', return_value=True):
            rendered, links, title = frontend_server.sanitize_html(
                source, 'https://example.test/start')

        self.assertEqual(title, 'Example')
        self.assertIn({
            'text': 'Read the guide',
            'url': 'https://example.test/docs/guide',
        }, links)
        self.assertIn('data-technetium-url="https://example.test/docs/guide"', rendered)
        self.assertIn('/api/resource?url=https%3A%2F%2Fexample.test%2Fdocs%2Fsite.css', rendered)
        self.assertIn('/api/resource?url=https%3A%2F%2Fexample.test%2Fimage.png', rendered)
        self.assertIn('<p>Visible</p>', rendered)
        self.assertNotIn('parent.document', rendered)
        self.assertNotIn('onerror', rendered)

    def test_css_rewriting_preserves_safe_properties_and_proxies_assets(self):
        stylesheet = (
            'html { scroll-behavior: smooth; }'
            'body { background-image: url("../images/bg.png"); }'
            '@import "theme.css";'
        )
        with patch.object(frontend_server, '_host_is_public', return_value=True):
            rewritten = frontend_server._rewrite_css(
                stylesheet, 'https://example.test/css/site.css')

        self.assertIn('scroll-behavior: smooth', rewritten)
        self.assertIn(
            '/api/resource?url=https%3A%2F%2Fexample.test%2Fimages%2Fbg.png',
            rewritten,
        )
        self.assertIn(
            '/api/resource?url=https%3A%2F%2Fexample.test%2Fcss%2Ftheme.css',
            rewritten,
        )


class FrontendAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ('127.0.0.1', 0), frontend_server.FrontendRequestHandler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = 'http://127.0.0.1:%d' % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_serves_frontend(self):
        with urlopen(self.base_url + '/', timeout=3) as response:
            page = response.read().decode('utf-8')
            policy = response.headers.get('Content-Security-Policy', '')
        self.assertEqual(response.status, 200)
        self.assertIn('Technetium', page)
        self.assertIn("script-src 'self'", policy)

        with urlopen(self.base_url + '/js/page-bridge.js', timeout=3) as response:
            bridge = response.read().decode('utf-8')
        self.assertIn('technetium:navigate', bridge)

        with urlopen(self.base_url + '/js/debugger.js', timeout=3) as response:
            debugger = response.read().decode('utf-8')
        self.assertIn('class DeveloperTools', debugger)

    def test_browse_endpoint_returns_metadata_and_safe_links(self):
        body = (
            b'<html><head><title>Test page</title>'
            b'<meta name="description" content="A fixture page"></head>'
            b'<body><a href="/next">Next</a></body></html>'
        )
        headers = Message()
        headers['Content-Type'] = 'text/html; charset=utf-8'
        target_url = 'https://example.test/'
        api_url = self.base_url + '/api/browse?' + urlencode({'url': target_url})

        with patch.object(frontend_server, '_host_is_public', return_value=True), \
                patch.object(frontend_server, '_read_response',
                             return_value=(target_url, 200, headers, body)):
            with urlopen(api_url, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))

        self.assertEqual(data['status'], 200)
        self.assertEqual(data['title'], 'Test page')
        self.assertEqual(data['description'], 'A fixture page')
        self.assertIn(
            {'text': 'Next', 'url': 'https://example.test/next'},
            data['links'],
        )

    def test_browse_rejects_local_destinations(self):
        api_url = self.base_url + '/api/browse?' + urlencode({'url': 'http://127.0.0.1/'})
        try:
            urlopen(api_url, timeout=3)
        except HTTPError as error:
            try:
                self.assertEqual(error.code, 400)
            finally:
                error.close()
        else:
            self.fail('The API accepted a local destination.')

    def test_debug_log_endpoint_redacts_credentials_and_query_values(self):
        frontend_server._record_debug_entry(
            'page',
            'https://user:password@example.test/page?token=secret',
            200,
            'text/html',
            12.5,
        )
        with urlopen(self.base_url + '/api/debug/logs?limit=1', timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))

        entry = data['entries'][0]
        self.assertEqual(entry['url'], 'https://example.test/page?[redacted]')
        self.assertNotIn('password', json.dumps(data))
        self.assertNotIn('secret', json.dumps(data))
        self.assertEqual(entry['kind'], 'page')
        self.assertEqual(entry['status'], 200)

    def test_resource_endpoint_rewrites_css_and_allows_opaque_iframe_assets(self):
        headers = Message()
        headers['Content-Type'] = 'text/css; charset=utf-8'
        target_url = 'https://example.test/css/site.css'
        css = b'body { background-image: url(../images/bg.png); }'
        api_url = self.base_url + '/api/resource?' + urlencode({'url': target_url})

        with patch.object(frontend_server, '_host_is_public', return_value=True), \
                patch.object(frontend_server, '_read_response',
                             return_value=(target_url, 200, headers, css)):
            with urlopen(api_url, timeout=3) as response:
                body = response.read().decode('utf-8')
                self.assertEqual(response.headers.get('Content-Type'), 'text/css; charset=utf-8')
                self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')

        self.assertIn(
            '/api/resource?url=https%3A%2F%2Fexample.test%2Fimages%2Fbg.png',
            body,
        )


if __name__ == '__main__':
    unittest.main()
