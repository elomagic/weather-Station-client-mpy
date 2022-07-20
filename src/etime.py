# etime.py - Tooling around NTP and time

import configuration as c
import logging as log


class Time:

    # Sync internal RTC with public NTP server
    @staticmethod
    def init_time_from_ntp():
        import ntptime
        import exceptions

        log.info('Getting time from NTP server...')
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

    # Returns local time in seconds including timezone offset starting from UNIX epoch (1.1.1970)
    def get_local_time(self):
        import time

        # Get epoch in seconds related to year 2000
        t = time.time()
        log.debug("Epoch in seconds related to year 2000 is {}".format(t))

        # Convert to unix epoch
        t += 946684800
        return t
