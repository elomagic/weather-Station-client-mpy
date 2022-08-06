# configuration.py - Configuration module

from micropython import const

LOGGING_LEVEL = const(b'logging.level')
LOGGING_CONSOLE_ENABLED = const(b'logging.console.enabled')
LOGGING_FILE_ENABLED = const(b'logging.file.enabled')
SENSOR_UID = const(b'sensor.uid')
SENSOR_MEASURE_INTERVAL = const(b'sensor.measureInterval')
SERVER_URL = const(b'server.url')
SERVER_APP_KEY = const(b'server.appKey')
WIFI_SSID = const(b'wifi.ssid')
WIFI_PASSWORD = const(b'wifi.password')
WIFI_ADDRESS = const(b'wifi.address')
WIFI_NETMASK = const(b'wifi.netmask')
WIFI_GATEWAY = const(b'wifi.gateway')
WIFI_DNS = const(b'wifi.dns')
WIFI_CLIENT_NAME = const(b'wifi.clientName')

APP_VER = const(b'1.0.2-SNAPSHOT')
APP_API_VER = const(b'1.0.0')

FILENAME = 'configuration'

_DEFAULT_VALUES = {
    LOGGING_LEVEL: const(b'debug'),
    LOGGING_CONSOLE_ENABLED: '1',
    LOGGING_FILE_ENABLED: '0',

    SENSOR_UID: '00000000-0000-0000-0000-000000000000',
    SENSOR_MEASURE_INTERVAL: '300',

    SERVER_URL: 'http://weather-api.elomagic.org/rest',
    SERVER_APP_KEY: '',

    WIFI_SSID: '',
    WIFI_PASSWORD: 'changeit',
    WIFI_ADDRESS: '',
    WIFI_NETMASK: '255.255.255.0',
    WIFI_GATEWAY: '',
    WIFI_DNS: '8.8.8.8',
    WIFI_CLIENT_NAME: 'Weather-Bot'
}

_CONFIG = {}


def reset():
    global _CONFIG
    _CONFIG = {}


def get_value(key: bytes) -> str:
    global _CONFIG

    if key in _CONFIG:
        return _CONFIG[key]

    return _DEFAULT_VALUES[key]


def set_value(key: bytes, value: str):
    global _CONFIG
    import logging as log
    log.debug("Setting '{}' with value '{}'".format(key, value))
    _CONFIG[key] = value


def load() -> bool:
    global _CONFIG
    import logging as log
    log.info("Reading configuration from '{}'...".format(FILENAME))
    try:
        with open(FILENAME, 'r') as f:
            _CONFIG = {}
            for line in f.readlines():
                index = line.find('=')
                if index != -1:
                    key = line[:index]
                    value = line[index+1:].rstrip()
                    set_value(bytes(key), value)

        log.debug("Configuration file '{}' successful loaded".format(FILENAME))

        log.setup(
            get_value(LOGGING_CONSOLE_ENABLED) == '1',
            get_value(LOGGING_FILE_ENABLED) == '1',
            bytes(get_value(LOGGING_LEVEL))
        )

        return True
    except OSError as ex:
        print("\nUnable to read configuration. Either it doesn't exist or is invalid: {}".format(ex))
        return False


def write():
    import logging as log
    global _CONFIG
    with open(FILENAME, 'w') as f:
        for key, value in _CONFIG.items():
            log.debug("Writing key '{}' with value '{}...'".format(key, value[:2]))
            f.write("{}={}\n".format(key, value))


def print_config():
    import logging as log
    global _CONFIG

    log.info('Current configuration in use:')
    for key, value in _CONFIG.items():
        log.info("{}={}".format(key, value))
