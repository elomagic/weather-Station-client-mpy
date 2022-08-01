import usocket as socket
import ustruct as struct


class MQTTException(Exception):
    pass


class MQTTClient:

    def __init__(self, client_id: str, server: str, port: int = 0, user: str = None, password: str = None, keepalive=0):
        if port == 0:
            port = 8883

        self.client_id = client_id
        self.sock = None
        self.addr = socket.getaddrinfo(server, port)[0][-1]
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False

    def _send_str(self, s: str):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic: str, msg: str, retain=False, qos: int = 0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session: bool = True):
        self.sock = socket.socket()
        self.sock.connect(self.addr)

        msg = bytearray(b"\x10\0\0\x04MQTT\x04\x02\0\0")
        msg[1] = 10 + 2 + len(self.client_id)
        msg[9] = clean_session << 1

        if self.user is not None:
            msg[1] += 2 + len(self.user) + 2 + len(self.pswd)
            msg[9] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[10] |= self.keepalive >> 8
            msg[11] |= self.keepalive & 0x00FF
        if self.lw_topic:
            msg[1] += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[9] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[9] |= self.lw_retain << 5

        self.sock.write(msg)
        self._send_str(self.client_id)

        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)

        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)

        resp = self.sock.read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self.sock.write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self.sock.write(b"\xc0\0")

    def publish(self, topic: str, msg: str, retain: bool = False, qos: int = 0):
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)

        if qos > 0:
            sz += 2

        assert sz < 2097152

        i = 1
        while sz > 0x7f:
            pkt[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz

        self.sock.write(pkt, i + 1)
        self._send_str(topic)

        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.write(pkt, 2)

        self.sock.write(msg)

        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self.sock.read(1)
                    assert sz == b"\x02"
                    rcv_pid = self.sock.read(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        return
        elif qos == 2:
            assert 0

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        res = self.sock.read(1)
        self.sock.setblocking(True)

        if res is None:
            return None

        if res == b"":
            raise OSError(-1)

        if res == b"\xd0":  # PING RESP
            sz = self.sock.read(1)[0]
            assert sz == 0
            return None

        op = res[0]
        if op & 0xf0 != 0x30:
            return op

        sz = self._recv_len()
        topic_len = self.sock.read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self.sock.read(topic_len)
        sz -= topic_len + 2

        if op & 6:
            pid = self.sock.read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2

        msg = self.sock.read(sz)
        self.cb(topic, msg)

        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self.sock.write(pkt)
        elif op & 6 == 4:
            assert 0

    # Checks whether a pending message from server is available.
    # If not, returns immediately with None. Otherwise, does
    # the same processing as wait_msg.
    def check_msg(self):
        self.sock.setblocking(False)
        return self.wait_msg()

    def publish_property(self, topic_prefix: str, key: str, data: dict):
        if data.get(key) is None:
            return

        value = data[key]

        self.publish("{}/{}".format(topic_prefix, key), value)
