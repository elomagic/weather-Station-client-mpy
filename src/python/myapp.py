# myapp.py - tbd.

import machine
import logging as log
import configuration as c

def deep_sleep(deep_sleep_time_ms: int):
    log.info("Going into deep sleep for {} seconds.".format(c.get_value(c.SENSOR_MEASURE_INTERVAL)))

    # Configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
    rtc.alarm(rtc.ALARM0, deep_sleep_time_ms)
    # Put the device to sleep
    machine.deepsleep()


def start():
    import gc
    from exceptions import BaseError
    from board import flash_led, BATTERY_MONITOR_PIN
    from sensor import read_sensor
    from client import post_weather_data
    import etime
    import version as v

    try:
        # check if the device woke from a deep sleep
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            log.info('Woke up from a deep sleep')

        etime.init_time_from_ntp()

        current_sensor_data: dict = read_sensor()

        # Enrich payload
        current_sensor_data['api_version'] = v.APP_API_VER
        current_sensor_data['fw_version'] = v.APP_VER
        current_sensor_data['sensorUid'] = c.get_value(c.SENSOR_UID)
        current_sensor_data['unixEpochTimestamp'] = etime.get_local_time()
        log.debug('Getting battery voltage')
        # 1024 = 1.3 Volt ( 220k / 100k Resistor )
        current_sensor_data['batteryVoltage'] = "{}".format(BATTERY_MONITOR_PIN.read() / 1023 * 1.3)

        # Release unused memory
        log.debug("Collected data: {}".format(current_sensor_data))

        gc.collect()

        post_weather_data(current_sensor_data)
        flash_led(1)
    except BaseException as e:
        log.error(e)
        flash_led(6, 2)
    except BaseError as e:
        log.error(e.message)
        flash_led(e.flashCount, 2)
    finally:
        deep_sleep_time = int(c.get_value(c.SENSOR_MEASURE_INTERVAL)) * 1000
        deep_sleep(deep_sleep_time)
