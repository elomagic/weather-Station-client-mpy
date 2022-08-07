# myapp.py - tbd.

import machine
import logging as log


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
    import sensor
    import configuration as c
    from exceptions import BaseError
    from client import post_weather_data
    from gc import collect
    from board import flash_led, BATTERY_MONITOR_PIN
    from etime import Time
    import version as v

    try:
        # check if the device woke from a deep sleep
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            log.info('Woke up from a deep sleep')

        time = Time()
        time.init_time_from_ntp()

        current_sensor_data = sensor.read_sensor()

        sensor.print_data(current_sensor_data)

        # Enrich payload
        current_sensor_data['api_version'] = v.APP_API_VER
        current_sensor_data['fw_version'] = v.APP_VER
        current_sensor_data['sensorUid'] = c.get_value(c.SENSOR_UID)
        current_sensor_data['unixEpochTimestamp'] = time.get_local_time()
        # 1024 = 1.3 Volt ( 220k / 100k Resistor )
        current_sensor_data['batteryVoltage'] = "{}".format(BATTERY_MONITOR_PIN.read() / 1023 * 1.3)

        url = "{}/measure".format(c.get_value(c.SERVER_URL))

        # Release unused memory
        collect()

        post_weather_data(url, current_sensor_data)
        flash_led(1)
    except exceptions.BaseError as e:
        flash_led(e.flashCount, 2)
        log.error(e.message)
    finally:
        deep_sleep_time = int(c.get_value(c.SENSOR_MEASURE_INTERVAL)) * 1000
        deep_sleep(deep_sleep_time)
