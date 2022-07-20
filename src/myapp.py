# myapp.py - tbd.

import machine
import exceptions
import configuration as c
from sensor import Sensor
from etime import Time
from board import BATTERY_MONITOR_PIN
import logging as log


_sensor = None
_etime = None


def deep_sleep(deep_sleep_time_ms: int):
    log.info("Going into deep sleep for {} seconds.".format(c.get_value(c.SENSOR_MEASURE_INTERVAL)))

    # Configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
    rtc.alarm(rtc.ALARM0, deep_sleep_time_ms)
    # Put the device to sleep
    machine.deepsleep()


def setup():
    from  board import SCL_PIN, SDA_PIN
    global _etime
    global _sensor

    log.info("Measure interval every seconds: {}".format(c.get_value(c.SENSOR_MEASURE_INTERVAL)))

    _etime = Time()
    _etime.init_time_from_ntp()
    _sensor = Sensor()
    _sensor.init(SCL_PIN, SDA_PIN)

    log.info('System successful initialized.\n')


def measure_and_send():
    import client
    import gc
    from board import flash_led

    global _etime
    global _sensor

    try:
        current_sensor_data = _sensor.read_sensor()

        _sensor.print_data(current_sensor_data)

        # Enrich payload
        current_sensor_data['api_version'] = '1.0'
        current_sensor_data['fw_version'] = c.APP_VER
        current_sensor_data['sensorUid'] = c.get_value(c.SENSOR_UID)
        current_sensor_data['unixEpochTimestamp'] = _etime.get_local_time()
        # 1024 = 1.3 Volt ( 220k / 100k Resistor )
        current_sensor_data['batteryVoltage'] = "{}".format(BATTERY_MONITOR_PIN.read() / 1023 * 1.3)

        url = "{}/measure".format(c.get_value(c.SERVER_URL))

        # Release unused memory
        c.reset()
        gc.collect()

        client.post_weather_data(url, current_sensor_data)
        flash_led(1)
    except exceptions.BaseError as e:
        flash_led(e.flashCount, 2)
        log.error(e.message)


def start():
    try:
        # check if the device woke from a deep sleep
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            log.info('Woke up from a deep sleep')

        setup()
        measure_and_send()
    except Exception as ex:
        log.error(ex)
    finally:
        deep_sleep_time = int(c.get_value(c.SENSOR_MEASURE_INTERVAL)) * 1000
        deep_sleep(deep_sleep_time)
