import usocket
import logging as log


class Response:

    def __init__(self, f):
        self.status_code = None
        self.raw = f
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None

        self._cached = None

    @property
    def content(self) -> bytes:
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None

        return self._cached

    @property
    def text(self) -> str:
        return str(self.content, "utf-8")

    def json(self):
        import ujson
        return ujson.loads(self.content)


def __request(method: str, url: str, json=None) -> Response:
    import ussl
    import configuration as c
    from exceptions import AuthenticationFailed

    redir_cnt = 1

    while True:
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""

        if proto == "http:":
            port = 80
        elif proto == "https:":
            import ussl
            port = 443
        else:
            raise ValueError("Unsupported protocol: {}".format(proto))

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        log.debug("Host={}, Port={}, Protocol={}".format(host, port, proto))

        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]

        log.debug("addrinfo={}".format(ai))

        s: usocket.Socket = usocket.socket(ai[0], ai[1], ai[2])
        try:
            s.settimeout(9.0)
            s.connect(ai[-1])
            if proto == "https:":
                ctx = ussl.SSLContext()
                s = ctx.wrap_socket(s, server_hostname=host)

            # log.debug('Sending data on socket')
            s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
            s.write(b"Host: %s\r\n" % host)
            s.write(b"Weather-Client-API-Key: %s\r\n" % c.get_value(c.SERVER_APP_KEY))

            if json:
                s.write(b'Content-Type: application/json; charset=UTF-8\r\n')
                s.write(b"Content-Length: %d\r\n" % len(json))

            s.write(b"Connection: close\r\n\r\n")

            if json:
                s.write(json)

            line = s.readline()
            # print(line)
            line = line.split(None, 2)
            status = int(line[1])
            reason = ""
            if len(line) > 2:
                reason = line[2].rstrip()

            while True:
                line = s.readline()
                if not line or line == b"\r\n":
                    break
                # print(line)

                if line.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in line:
                        raise ValueError("Unsupported " + line.decode())
                elif line.startswith(b"Location:") and 300 <= status <= 399:
                    if not redir_cnt:
                        raise ValueError("Too many redirects")

                    redir_cnt -= 1
                    url = line[9:].decode().strip()
                    log.debug("Redirect to url {}".format(url))
                    status = 300
                    break
        except OSError:
            s.close()
            raise

        if status != 300:
            break

    log.debug("Responses HTTP code {}, reason={}".format(status, reason))

    if status == 401:
        raise AuthenticationFailed()

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    return resp


def get(url: str, **kw) -> Response:
    return __request("GET", url, **kw)


def post(url: str, **kw) -> Response:
    return __request("POST", url, **kw)
