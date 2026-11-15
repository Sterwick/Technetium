import ipaddress
import socket
import select
import threading
from urllib.parse import urlsplit

# Server configuration
########################################################################################################################

config_IPv6    = False
config_host    = '127.0.0.1'
config_port    = 8080
config_timeout = 60

BUFLEN  = 10000
HTTPVER = 'HTTP/1.1'


# Connections handling
########################################################################################################################

class ConnectionHandlerThread(threading.Thread):
    supportedHttpMethods = ('OPTIONS',
                            'GET',
                            'HEAD',
                            'POST',
                            'PUT',
                            'DELETE',
                            'TRACE',
                            'CONNECT')

    def __init__(self, accepted_connection):
        super().__init__(daemon=True)

        self.accepted_connection = accepted_connection
        self.client = None
        self.client_buffer = bytes()
        self.timeout = config_timeout


    def _process_CONNECT(self, path):
        self._target = self._connect_target(path)
        self.client.sendall(bytes((HTTPVER + ' 200 Connection established\r\n'
                                   + 'Proxy-agent: Technetium\r\n\r\n'), encoding="latin-1"))

        self._target_client_exchange()


    def _substitute_CDN(self, host, path):

        return False


    def _process_method(self, method, path, protocol):
        parsed_url = urlsplit(path)
        if parsed_url.scheme.lower() != 'http' or not parsed_url.hostname:
            raise ValueError('Expected an absolute HTTP URL')
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query

        if self._substitute_CDN(host, path) == True:
            return

        self._target = self._connect_target(host, 80)    # send the HTTP response
        self._target.sendall(bytes('%s %s %s\r\n' % (method, path, protocol), encoding='latin-1'))

        if self.client_buffer:
            self._target.sendall(self.client_buffer)  # send the remaining from _parse_request
        self.client_buffer = bytes()                 # and reset the buffer

        self._target_client_exchange()               # start copying from target


    def _connect_target(self, path, default_port=443):
        parsed = urlsplit('//' + path)
        host = parsed.hostname
        port = parsed.port or default_port
        if not host:
            raise ValueError('Invalid proxy destination')

        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        if not addresses:
            raise OSError('Proxy destination did not resolve')
        if any(not ipaddress.ip_address(address[4][0].split('%')[0]).is_global
               for address in addresses):
            raise PermissionError('Proxy destination resolves to a non-public address')

        last_error = None
        for family, socktype, proto, _, address in addresses:
            target = socket.socket(family, socktype, proto)
            target.settimeout(self.timeout)
            try:
                target.connect(address)
                return target
            except OSError as error:
                last_error = error
                target.close()
        raise last_error or OSError('Unable to connect to proxy destination')


    def _target_client_exchange(self):
        socs = [self.client, self._target]
        finished = False
        while not finished:
            (recv, _, error) = select.select(socs, [], socs, self.timeout)
            if error:
                break
            if len(recv) == 0:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if len(data) == 0:
                        finished = True
                        break
                    if in_ is self.client:
                        out = self._target
                    else:
                        out = self.client
                    if data:
                        out.sendall(data)
        print('Active connection threads:', len(threading.enumerate()) - 1)


    def _parse_request(self):
        request = bytearray()
        while b'\n' not in request:
            chunk = self.client.recv((BUFLEN // 8) * 2)
            if not chunk:
                raise ConnectionError('Client closed before sending a request')
            request.extend(chunk)
            if len(request) > BUFLEN * 4:
                raise ValueError('Proxy request line is too large')

        end = request.index(b'\n')
        request_line = request[:end].decode('latin-1').strip()
        print(request_line)
        parsed_request = request_line.split()
        if len(parsed_request) != 3:
            raise ValueError('Malformed proxy request line')
        self.client_buffer = bytes(request[end + 1:])
        return parsed_request


    def run(self):
        self.client, _ = self.accepted_connection
        self.client.settimeout(self.timeout)
        self._target = None
        try:
            method, path, protocol = self._parse_request()
            if method not in self.supportedHttpMethods:
                raise ValueError('Unsupported HTTP method')
            if method == 'CONNECT':
                self._process_CONNECT(path)
            else:
                self._process_method(method, path, protocol)
        except (OSError, ValueError, PermissionError, ConnectionError) as error:
            print('Error processing proxy request:', error)
            if self.client:
                try:
                    self.client.sendall(
                        b'HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n')
                except OSError:
                    pass
        finally:
            if self.client:
                self.client.close()
            if self._target:
                self._target.close()


def serve_forever():
    soc_type = socket.AF_INET6 if config_IPv6 else socket.AF_INET
    host_port = (config_host, config_port)
    with socket.socket(soc_type) as soc:
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(host_port)
        soc.listen(64)
        print("Proxy is up and listening %s:%d" % host_port)
        while True:
            try:
                connection = soc.accept()
            except OSError as error:
                print('Proxy listener stopped:', error)
                break
            ConnectionHandlerThread(connection).start()


if __name__ == '__main__':
    serve_forever()
