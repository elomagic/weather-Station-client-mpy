# client.py - HTTP client module to post data to server

import configuration as c


def _publish_property(mqtt, topic_prefix: str, sensor_uid: str, key: str, data: dict) -> None:
    if data.get(key) is None:
        return

    value = str(data[key])

    mqtt.publish("{}/{}/{}".format(topic_prefix, sensor_uid, key), value)


def _send_via_mqtt(url: str, data: dict) -> None:
    from umqttsimple import MQTTClient
    from gc import collect
    import logging as log
    from exceptions import UnableToPostError

    log.info("Sending data to '{}'".format(url))

    # Client-Instanz erzeugen
    proto, dummy, host, topic_prefix = url.split('/', 3)
    if ':' in host:
        host, port = host.split(':', 1)
    elif proto == 'mqtts:':
        port = '8883'
    else:
        port = '1883'

    collect()
    sensor_uid = c.get_value(c.SENSOR_UID)
    client = MQTTClient(client_id=sensor_uid, server=host, port=int(port), keepalive=10)
    try:
        log.debug("Connecting to '{}' on port {} with ID '{}'".format(host, port, sensor_uid))
        client.connect()
        try:
            log.debug("Connected to {}".format(host))

            _publish_property(client, topic_prefix, sensor_uid, 'temperature', data)
            _publish_property(client, topic_prefix, sensor_uid, 'pressure', data)
            _publish_property(client, topic_prefix, sensor_uid, 'humidity', data)
            _publish_property(client, topic_prefix, sensor_uid, 'batteryVoltage', data)

            log.debug('Value published. Disconnecting')
        finally:
            client.disconnect()
    except BaseException as e:
        log.error(e)
        raise UnableToPostError


def _post_via_rest(url: str, data: dict) -> None:
    import ujson
    import erequests as requests
    from exceptions import UnableToPostError
    import logging as log

    payload = ujson.dumps(data)

    log.info("Posting to '{}' with payload: {}".format(url, payload))

    response = requests.post(url, json=payload)
    http_code = response.status_code
    response.close()

    if (http_code >= 400) & (http_code < 600):
        log.warn("Posted payload: {}".format(payload))
        # log.warn("Responses payload {}".format(text))

        raise UnableToPostError


def post_weather_data(data: dict) -> None:
    from wifi import wlan
    from exceptions import WlanNotConnectedError

    if not wlan.isconnected():
        raise WlanNotConnectedError

    url = c.get_value(c.SERVER_URL)

    if url.startswith('http:'):
        _post_via_rest("{}/measure".format(url), data)
    elif url.startswith('mqtt:'):
        _send_via_mqtt(c.get_value(c.SERVER_URL), data)
    else:
        raise ValueError("Unsupported scheme in URL '%s'" % url)
