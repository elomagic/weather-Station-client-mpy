# client.py - HTTP client module to post data to server

def publish_property(client, topic_prefix: str, key: str, data: dict):
    if data.get(key) is None:
        return

    value = data[key]

    client.publish("{}/{}".format(topic_prefix, "temperature"), value)


def send_via_mqtt(url: str, data: dict):
    from umqttsimple import MQTTClient
    import configuration as c
    import logging as log

    # Client-Instanz erzeugen
    proto, dummy, host, topic_prefix = url.split("/", 3)
    log.debug("Connecting to " + host)
    client = MQTTClient(c.get_value(c.SERVER_APP_KEY), host)
    client.connect()
    log.debug("Connected to " + host)

    publish_property(client, topic_prefix, "temperature", data)
    publish_property(client, topic_prefix, "pressure", data)
    publish_property(client, topic_prefix, "humidity", data)
    publish_property(client, topic_prefix, "batteryVoltage", data)


def post_via_rest(url: str, data: dict):
    import ujson
    from wifi import wlan
    import erequests as requests
    from exceptions import UnableToPostError, WlanNotConnectedError
    import logging as log

    if not wlan.isconnected():
        raise WlanNotConnectedError

    payload = ujson.dumps(data)

    log.info("Posting to \"{}\" with payload: {}".format(url, payload))

    response = requests.post(url, json=payload)
    http_code = response.status_code
    response.close()

    if (http_code >= 400) & (http_code < 600):
        log.warn("Posted payload: {}".format(payload))
        # log.warn("Responses payload {}".format(text))

        raise UnableToPostError


def post_weather_data(url: str, data: dict):
    if url.startswith('http:'):
        post_via_rest(url, data)
    elif url.startswith('mqtt:'):
        send_via_mqtt(url, data)
    else:
        raise ValueError("Unsupported scheme in URL '%s'" % url)
