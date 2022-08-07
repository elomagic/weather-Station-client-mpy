# etime.py - Tooling around NTP and time

import logging as log


def init_time_from_ntp():
    """Sync internal RTC with public NTP server"""
    import ntptime
    import exceptions

    log.info('Getting time from NTP server')
    count = 5
    while count > 0:

        try:
            ntptime.settime()
            break
        except Exception as ex:
            count -= 1
            log.error("Getting time failed: {}".format(ex))

    if count == 0:
        raise exceptions.ReadNtpError

def get_local_time():
    """Returns local time in seconds including timezone offset starting from UNIX epoch (1.1.1970)"""
    import time

    # Get epoch in seconds related to year 2000
    log.debug('Getting local time')
    t = time.time()
    log.debug("Epoch in seconds related to year 2000 is {}".format(t))

    # Convert to unix epoch
    t += 946684800
    return t
