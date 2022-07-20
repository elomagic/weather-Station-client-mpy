# Upload this file only when you want to run app automatically. In this case, no console is available
import esp
import wifi
from board import MEASURE_MODE_PIN
import configuration
import logging as log

esp.osdebug(None)

config_exists = configuration.load()
log.debug("config_exists={}".format(config_exists))

log.debug("measure_mode_pin={}".format(MEASURE_MODE_PIN.value()))
measure_mode = MEASURE_MODE_PIN.value() == 1 and config_exists

wifi.init(config_exists)

if measure_mode:
    import myapp
    myapp.start()
else:
    import server
    server.start_web_server()
