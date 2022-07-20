# client.py - HTTP client module to post data to server


def post_weather_data(url: str, data):
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
