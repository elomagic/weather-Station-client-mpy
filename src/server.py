
import logging as log
from micropython import const

_CONST_HTTP_OK = const(b'HTTP/1.1 200 OK\r\n')
_CONST_CONN_CLOSE = const(b'Connection: close\r\n\r\n')
_FIX_PASSWORD = const(b'DoYaThinkIAmAnIdiot?')

_ssids = []


#def send_response_log(connection):
#    filename = log.get_logfile('0')
#    log.debug("Request log file '{}'".format(filename))
#    with open(log.get_logfile('0'), 'r') as f:
#        connection.send(__CONST_HTTP_OK)
#        connection.send('Cache-Control: no-cache\r\n')
#        connection.send('Content-Type: text/plain\r\n')
#        connection.send(__CONST_CONN_CLOSE)
#        for line in f:
#            connection.sendall(line)
#
#    log.debug('Log file responded')


def send_response_not_found(connection):
    log.debug('Send response: 404 Not Found')
    connection.send(const(b'HTTP/1.1 404 Not found\r\n'))
    connection.send(const(b'Content-Type: text/html\r\n'))
    connection.sendall(_CONST_CONN_CLOSE)


def send_redirect(connection):
    connection.send('HTTP/1.1 303 See Other\r\n')
    connection.send(const(b'Location: /\r\n'))
    connection.sendall(_CONST_CONN_CLOSE)


def send_response_resource(connection, resource, text=''):
    import configuration as c
    global _ssids
    filename = "/html/{}".format(resource)

    if resource.endswith('.html'):
        log.debug("Loading resource '{}'...".format(filename))

        access_points = ''
        for ssid in _ssids:
            access_points += "<option value=\"{}\">".format(ssid)

        with open(filename, 'r') as f:
            connection.send(_CONST_HTTP_OK)
            connection.send('Content-Type: text/html;charset=utf-8\r\n')
            connection.send('Server: WeatherBot/1.0\r\n')
            connection.send(_CONST_CONN_CLOSE)

            for line in f:
                line = line\
                    .replace('{uid}', c.get_value(c.SENSOR_UID))\
                    .replace('{measure-interval}', c.get_value(c.SENSOR_MEASURE_INTERVAL))\
                    .replace('{geo}', c.get_value(c.SENSOR_MEASURE_INTERVAL))

                line = line\
                    .replace('{ssid}', c.get_value(c.WIFI_SSID))\
                    .replace('{password}', str(_FIX_PASSWORD))\
                    .replace('{address}', c.get_value(c.WIFI_ADDRESS))\
                    .replace('{netmask}', c.get_value(c.WIFI_NETMASK))\
                    .replace('{gateway}', c.get_value(c.WIFI_GATEWAY))\
                    .replace('{dns}', c.get_value(c.WIFI_DNS))\
                    .replace('{wcn}', c.get_value(c.WIFI_CLIENT_NAME))

                line = line\
                    .replace('{server-url}', c.get_value(c.SERVER_URL))\
                    .replace('{api-key}', c.get_value(c.SERVER_APP_KEY))

                line = line.replace('{level-debug}', 'selected' if 'debug' == c.get_value(c.LOGGING_LEVEL) else '')
                line = line.replace('{level-info}', 'selected' if 'info' == c.get_value(c.LOGGING_LEVEL) else '')
                line = line.replace('{level-warn}', 'selected' if 'warn' == c.get_value(c.LOGGING_LEVEL) else '')
                line = line.replace('{level-error}', 'selected' if 'error' == c.get_value(c.LOGGING_LEVEL) else '')

                line = line.replace('{submit-result-text}', text)

                line = line.replace('{local-ip-address}', '')

                line = line.replace('{access-points}', access_points)

                line = line.replace('{app-ver}', c.APP_VER)

                connection.send(line)

        connection.sendall('')
    else:
        log.debug("Stream resource '{}'...".format(filename))

        mimetypes = 'application/octet-stream'
        if resource.endswith('.png'):
            mimetypes = 'image/pmg'
        elif resource.endswith('.css'):
            mimetypes = 'text/css'

        chunk_size = 1024
        with open(filename, 'rb') as f:
            connection.send(_CONST_HTTP_OK)
            connection.send('Cache-Control: max-age=86400, public\r\n')
            connection.send("Content-Type: {}\r\n".format(mimetypes))
            connection.send(_CONST_CONN_CLOSE)

            data = f.read(chunk_size)
            while data:
                # print("Sending bulk: {}".format(data))
                connection.sendall(data)
                data = f.read(chunk_size)

    log.debug("Resource '{}' responded".format(resource))


def url_decode(data: bytearray) -> str:
    bits = data.split(b'%')
    arr = [bits[0]]
    for item in bits[1:]:
        code = item[:2]
        char = bytes([int(code, 16)])
        arr.append(char)
        arr.append(item[2:].replace(b'+', b' '))

    res = b''.join(arr)
    return res.decode('utf-8')


def get_form_fields(body) -> {}:
    result = {}
    fields = body.replace(b'+', b'%20').split(b'&')
    for field in fields:
        items = field.split(b'=')
        result[items[0].decode('utf-8')] = url_decode(items[1]) if len(items) > 1 else ''

    return result


def get_form_field(form_data, key, default_value):
    if key in form_data:
        value = form_data[key]
        log.debug("Return value '{}' for key '{}'".format(value, key))
        return value

    log.debug("Return default value '{}' for key '{}'".format(default_value, key))
    return default_value


def handle_post_configuration(data):
    import configuration as c
    form_fields = get_form_fields(data)

    log.debug("ssid={}".format(c.get_value(c.WIFI_SSID)))

    # TODO Add validation

    c.set_value(c.SENSOR_UID, get_form_field(form_fields, 'uid', c.get_value(c.SENSOR_UID)))
    c.set_value(c.SENSOR_MEASURE_INTERVAL, get_form_field(form_fields, 'measure-interval', c.get_value(c.SENSOR_MEASURE_INTERVAL)))

    c.set_value(c.WIFI_SSID, get_form_field(form_fields, 'ssid', c.get_value(c.WIFI_SSID)))
    p = get_form_field(form_fields, 'password', c.get_value(c.WIFI_PASSWORD))
    if p != _FIX_PASSWORD:
        c.set_value(c.WIFI_PASSWORD, p)
    c.set_value(c.WIFI_ADDRESS, get_form_field(form_fields, 'address', c.get_value(c.WIFI_ADDRESS)))
    c.set_value(c.WIFI_NETMASK, get_form_field(form_fields, 'netmask', c.get_value(c.WIFI_NETMASK)))
    c.set_value(c.WIFI_GATEWAY, get_form_field(form_fields, 'gateway', c.get_value(c.WIFI_GATEWAY)))
    c.set_value(c.WIFI_DNS, get_form_field(form_fields, 'dns', c.get_value(c.WIFI_DNS)))
    c.set_value(c.WIFI_CLIENT_NAME, get_form_field(form_fields, 'wcn', c.get_value(c.WIFI_CLIENT_NAME)))

    c.set_value(c.SERVER_URL, get_form_field(form_fields, 'server-url', c.get_value(c.SERVER_URL)))
    c.set_value(c.SERVER_APP_KEY, get_form_field(form_fields, 'api-key', c.get_value(c.SERVER_APP_KEY)))

    c.set_value(c.LOGGING_LEVEL, get_form_field(form_fields, 'debug-level', c.get_value(c.LOGGING_LEVEL)))

    log.info('Writing new configuration')
    c.write()


def start_web_server():
    import usocket as socket
    import gc
    import wifi
    from board import WIFI_CLIENT_MODE_PIN

    global _ssids

    if WIFI_CLIENT_MODE_PIN.value() == 0:
        _ssids = wifi.scan_wlan()

    port = 80
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen(1)

    while True:
        gc.collect()

        method = None

        log.info("Webserver listening on port {}".format(port))
        conn, addr = server.accept()
        try:
            log.debug('Got a connection from %s' % str(addr))
            conn.settimeout(10)

            headers = []
            body = []
            # Looks a little ugly but otherwise no chance to read the whole request content
            try:
                while True:
                    line = conn.readline().decode('utf-8').strip()
                    if line == '':
                        break
                    else:
                        headers.append(line)

                method = headers[0].split(' ')[0]
                log.debug("Req-Method={}".format(method))

                if method == 'POST':
                    body = conn.recv(1024)
            except Exception as ex:
                log.debug("End of request reached? {}".format(ex))

            log.debug("Req-Headers={}".format(headers))
            requested_path = headers[0].split()[1]
            log.info("Req Path={}".format(requested_path))
            log.debug("Req-Body={}".format(body))

            if '..' in requested_path:
                # Prevent path traversal vulnerabilities by checking of ".."
                log.warn('Invalid path requested by %s' % str(addr))
                send_response_not_found(conn)
 #           elif requested_path == '/get-log-file.do' and method == 'GET':
 #               try:
 #                   send_response_log(conn)
 #               except Exception as err:
 #                   log.error("Trouble with requested logging file '{}': {}".format(requested_path, err))
 #                   send_response_not_found(conn)
            elif requested_path == '/submit-configuration.do' and method == 'POST':
                # Must be HTTP POST
                handle_post_configuration(body)
                send_redirect(conn)
            elif requested_path == '/' and method == 'GET':
                # Must be HTTP GET
                send_response_resource(conn, 'index.html')
            elif method == 'GET':
                try:
                    resource = requested_path.split("/")[-1]
                    send_response_resource(conn, resource)
                except Exception as err:
                    log.warn("Trouble with requested path '{}': {}".format(requested_path, err))
                    send_response_not_found(conn)
            else:
                send_response_not_found(conn)
        except Exception as ex:
            log.error("An unexpected error occur: {}".format(ex))
        finally:
            log.debug('Closing socket')
            conn.close()
