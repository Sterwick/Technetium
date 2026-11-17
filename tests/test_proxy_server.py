import ipaddress
import socket
import socketserver
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from servers import proxy_server


class HTTPOriginHandler(socketserver.StreamRequestHandler):
    def handle(self):
        request_line = self.rfile.readline()
        while self.rfile.readline() not in (b'\r\n', b''):
            pass
        self.server.request_line = request_line
        self.wfile.write(
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/plain\r\n'
            b'Content-Length: 2\r\n'
            b'Connection: close\r\n\r\nOK'
        )


class EchoOriginHandler(socketserver.StreamRequestHandler):
    def handle(self):
        payload = self.rfile.read(4)
        self.wfile.write(payload)


class ProxyIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.origins = []
        self.origin_threads = []
        self.proxy_threads = []

    def tearDown(self):
        for server in self.origins:
            server.shutdown()
            server.server_close()
        for thread in self.origin_threads + self.proxy_threads:
            thread.join(timeout=2)

    def _start_origin(self, handler):
        server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.origins.append(server)
        self.origin_threads.append(thread)
        return server

    def _open_proxy_connection(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        client = socket.create_connection(listener.getsockname(), timeout=3)
        server_socket, address = listener.accept()
        listener.close()
        handler = proxy_server.ConnectionHandlerThread((server_socket, address))
        handler.start()
        self.proxy_threads.append(handler)
        return client, handler

    def _public_dns_for_local_fixture(self, host, port, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '',
             ('127.0.0.1', port))
        ]

    def test_forwards_http_request_and_response(self):
        origin = self._start_origin(HTTPOriginHandler)
        client, handler = self._open_proxy_connection()
        client.settimeout(4)

        with patch.object(socket, 'getaddrinfo', side_effect=self._public_dns_for_local_fixture), \
                patch.object(ipaddress, 'ip_address',
                             return_value=SimpleNamespace(is_global=True)):
            client.sendall(
                ('GET http://example.test:%d/path HTTP/1.1\r\n' % origin.server_address[1]
                 + 'Host: example.test\r\nConnection: close\r\n\r\n').encode('ascii')
            )
            response = bytearray()
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response.extend(data)

        client.close()
        handler.join(timeout=4)
        self.assertIn(b'HTTP/1.1 200 OK', response)
        self.assertTrue(response.endswith(b'OK'))
        self.assertEqual(origin.request_line, b'GET /path HTTP/1.1\r\n')

    def test_establishes_connect_tunnel_and_relays_bytes(self):
        origin = self._start_origin(EchoOriginHandler)
        client, handler = self._open_proxy_connection()
        client.settimeout(4)

        with patch.object(socket, 'getaddrinfo', side_effect=self._public_dns_for_local_fixture), \
                patch.object(ipaddress, 'ip_address',
                             return_value=SimpleNamespace(is_global=True)):
            client.sendall(
                ('CONNECT example.test:%d HTTP/1.1\r\n\r\n'
                 % origin.server_address[1]).encode('ascii')
            )
            handshake = bytearray()
            while b'\r\n\r\n' not in handshake:
                handshake.extend(client.recv(1024))
            self.assertIn(b'200 Connection established', handshake)
            client.sendall(b'ping')
            relayed = bytearray()
            while len(relayed) < 4:
                relayed.extend(client.recv(4 - len(relayed)))

        client.close()
        handler.join(timeout=4)
        self.assertEqual(bytes(relayed), b'ping')


if __name__ == '__main__':
    unittest.main()
