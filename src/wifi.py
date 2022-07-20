
import logging as log

wlan = None


def start_client():
    import configuration as c
    import network
    import ubinascii
    
    global wlan

    wifi_ssid = c.get_value(c.WIFI_SSID)
    wifi_password = c.get_value(c.WIFI_PASSWORD)

    client_hostname = c.get_value(c.WIFI_CLIENT_NAME)

    log.info("Initiating Wifi client '{}'...".format(client_hostname))
    wlan = network.WLAN(network.STA_IF)
    mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()
    log.info("MAC-address: {}".format(mac))
    log.info("Connecting to access point with SSID '{}'...".format(wifi_ssid))
    if not wlan.isconnected():
        wlan.active(True)
        wlan.config(dhcp_hostname=client_hostname)
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass

    log.info("Network settings: {}".format(wlan.ifconfig()))


def start_ap():
    import configuration as c
    import network
    import gc

    global wlan

    # Read configuration

    ssid = c.get_value(c.WIFI_CLIENT_NAME)
    password = 'weather-bot'

    log.info("Starting Wifi for configuration mode with SSID '{}'".format(ssid))

    # Why?
    gc.collect()

    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    # Hint: Password currently not work. See https://forum.micropython.org/viewtopic.php?t=9247
    wlan.config(essid=ssid, password=password)

    # Wait till hotspot is active
    while not wlan.active():
        pass

    log.info('Access point successful configured.')
    log.debug("Ifconfig={}".format(wlan.ifconfig()))


def init(config_exists: bool = False):
    from board import WIFI_CLIENT_MODE_PIN

    log.debug("wifi_client_mode_pin={}".format(WIFI_CLIENT_MODE_PIN.value()))

    wifi_client_mode = WIFI_CLIENT_MODE_PIN.value() == 1 and config_exists
    if wifi_client_mode:
        start_client()
    else:
        start_ap()


def scan_wlan():
    import network

    log.info('Scanning WLAN...')
    wl = network.WLAN(network.STA_IF)
    wl.active(True)

    __ssids = []
    try:
        aps = wl.scan()
        for ssid, bssid, channel, rssi, authmode, hidden in sorted(aps, key=lambda x: x[0], reverse=False):
            ssid = ssid.decode('utf-8')
            if ssid not in __ssids:
                __ssids.append(ssid)
    except Exception as ex:
        log.error("WLAN scan failed: {}".format(ex))

    # wl.active(False)
    log.debug("ssids={}".format(__ssids))

    return __ssids
