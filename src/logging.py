
from micropython import const

__FILENAME: str = "logs/weather-{}.log"
__MAX_ROLLOVER_FILES: int = const(2)
__MAX_LOG_FILE_SIZE = const(1024 * 16)

__logging_level: str = 'debug'
__logging_console_enabled: bool = True
__logging_file_enabled: bool = False


def __print_text(text):
    print(text)


def __write_text(text):
    import os

    filename_0 = get_logfile(0)

    with open(filename_0, 'a') as f:
        f.write(text)
        f.write('\n')

    stat_info = os.stat(get_logfile(0))
    file_size = stat_info[6]

    if file_size > __MAX_LOG_FILE_SIZE:
        filename_1 = get_logfile(1)
        try:
            os.remove(filename_1)
        except Exception as e:
            # noop
            pass

        os.rename(filename_0, filename_1)


def __can_log(level) -> bool:
    __DEBUG_PRIORITY = {
        'trace': 1500,
        'debug': 1000,
        'info': 500,
        'warn': 250,
        'error': 100,
        '-': 0
    }
    vclevel = __DEBUG_PRIORITY[__logging_level]
    vlevel = __DEBUG_PRIORITY[level]

    return vlevel <= vclevel


def __log(level: str, text: str):
    global __logging_file_enabled
    global __logging_console_enabled

    if __can_log(level):
        if __logging_console_enabled:
            __print_text(text)
        if __logging_file_enabled:
            __write_text(text)


def setup(console_logging: bool, file_logging: bool, min_log_level: str):
    global __logging_level
    global __logging_file_enabled
    global __logging_console_enabled

    info("Setup logging (min_log_level={}, console_logging={}, file_logging={})".format(min_log_level, console_logging, file_logging))

    __logging_level = min_log_level
    __logging_console_enabled = console_logging
    __logging_file_enabled = file_logging


def get_logfile(index: int) -> str:
    return __FILENAME.format(index)


def debug(text):
    __log('debug', "DEBUG {}".format(text))


def info(text):
    __log('info', "INFO  {}".format(text))


def warn(text):
    __log('warn', "WARN  {}".format(text))


def error(text):
    __log('warn', "ERROR {}".format(text))


def all_event(text):
    __log('-', "-     {}".format(text))
