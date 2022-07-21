# configuration.py - Configuration module

LOGGING_LEVEL = 'logging.level'
LOGGING_CONSOLE_ENABLED = 'logging.console.enabled'
LOGGING_FILE_ENABLED = 'logging.file.enabled'
SENSOR_UID = 'sensor.uid'
SENSOR_MEASURE_INTERVAL = 'sensor.measureInterval'
SERVER_URL = 'server.url'
SERVER_APP_KEY = 'server.appKey'
WIFI_SSID = 'wifi.ssid'
WIFI_PASSWORD = 'wifi.password'
WIFI_ADDRESS = 'wifi.address'
WIFI_NETMASK = 'wifi.netmask'
WIFI_GATEWAY = 'wifi.gateway'
WIFI_DNS = 'wifi.dns'
WIFI_CLIENT_NAME = 'wifi.clientName'

APP_VER = '1.0.1-SNAPSHOT'
APP_API_VER = '1.0.0'

FILENAME = 'configuration'

__DEFAULT_VALUES = {
    LOGGING_LEVEL: 'debug',
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

__CONFIG = {}


def reset():
    global __CONFIG
    __CONFIG = {}


def get_value(key: str) -> str:
    global __CONFIG

    if key in __CONFIG:
        return __CONFIG[key]

    return __DEFAULT_VALUES[key]


def set_value(key: str, value: str):
    global __CONFIG
    import logging as log
    log.debug("Setting '{}' with value '{}'".format(key, value))
    __CONFIG[key] = value


def load() -> bool:
    global __CONFIG
    import logging as log
    log.info("Reading configuration from '{}'...".format(FILENAME))
    try:
        with open(FILENAME, 'r') as f:
            __CONFIG = {}
            for line in f.readlines():
                index = line.find('=')
                if index != -1:
                    key = line[:index]
                    value = line[index+1:].rstrip()
                    set_value(key, value)

        log.debug("Configuration file '{}' successful loaded".format(FILENAME))

        log.setup(
            get_value(LOGGING_CONSOLE_ENABLED) == '1',
            get_value(LOGGING_FILE_ENABLED) == '1',
            get_value(LOGGING_LEVEL)
        )

        return True
    except OSError as ex:
        print("\nUnable to read configuration. Either it doesn't exist or is invalid: {}".format(ex))
        return False


def write():
    import logging as log
    global __CONFIG
    with open(FILENAME, 'w') as f:
        for key, value in __CONFIG.items():
            log.debug("Writing key '{}' with value '{}...'".format(key, value[:2]))
            f.write("{}={}\n".format(key, value))


def print_config():
    import logging as log
    global __CONFIG

    log.info('Current configuration in use:')
    for key, value in __CONFIG.items():
        log.info("{}={}".format(key, value))
