
from micropython import const

LEVEL_TRACE = const(b'trace')
LEVEL_DEBUG = const(b'debug')
LEVEL_INFO = const(b'info')
LEVEL_WARN = const(b'warn')
LEVEL_ERROR = const(b'error')
LEVEL_ALL = const(b'-')

_FILENAME: str = "logs/weather-{}.log"
_MAX_ROLLOVER_FILES: int = const(2)
_MAX_LOG_FILE_SIZE = const(1024 * 16)

_logging_level: bytes = LEVEL_DEBUG
_logging_console_enabled: bool = True
_logging_file_enabled: bool = False


def _print_text(text) -> None:
    print(text)


def _write_text(text) -> None:
    import os

    filename_0 = get_logfile(0)

    with open(filename_0, 'a') as f:
        f.write(text)
        f.write('\n')

    stat_info = os.stat(get_logfile(0))
    file_size = stat_info[6]

    if file_size > _MAX_LOG_FILE_SIZE:
        filename_1 = get_logfile(1)
        try:
            os.remove(filename_1)
        except BaseException as e:
            # noop
            pass

        os.rename(filename_0, filename_1)


def _can_log(level: bytes) -> bool:
    _DEBUG_PRIORITY = {
        LEVEL_TRACE: 1500,
        LEVEL_DEBUG: 1000,
        LEVEL_INFO: 500,
        LEVEL_WARN: 250,
        LEVEL_ERROR: 100,
        LEVEL_ALL: 0
    }
    vclevel = _DEBUG_PRIORITY[_logging_level]
    vlevel = _DEBUG_PRIORITY[level]

    return vlevel <= vclevel


def _log(level: bytes, text: str) -> None:
    global _logging_file_enabled
    global _logging_console_enabled

    if _can_log(level):
        if _logging_console_enabled:
            _print_text(text)
        if _logging_file_enabled:
            _write_text(text)


def setup(console_logging: bool, file_logging: bool, min_log_level: bytes) -> None:
    global _logging_level
    global _logging_file_enabled
    global _logging_console_enabled

    info("Setup logging (min_log_level={}, console_logging={}, file_logging={})".format(min_log_level, console_logging, file_logging))

    _logging_level = min_log_level
    _logging_console_enabled = console_logging
    _logging_file_enabled = file_logging


def get_logfile(index: int) -> str:
    return _FILENAME.format(index)


def debug(text) -> None:
    _log(LEVEL_DEBUG, "DEBUG {}".format(text))


def info(text) -> None:
    _log(LEVEL_INFO, "INFO  {}".format(text))


def warn(text) -> None:
    _log(LEVEL_WARN, "WARN  {}".format(text))


def error(text) -> None:
    _log(LEVEL_ERROR, "ERROR {}".format(text))


def all_event(text) -> None:
    _log(LEVEL_ALL, "-     {}".format(text))
