import time
from test_tobias import Logger

def initialize_logger():
    logger = Logger()
    now = time.localtime()

    logger.add_info_line(
        "Logger started at %04d-%02d-%02d %02d:%02d:%02d" %
        (now[0], now[1], now[2], now[3], now[4], now[5])
    )
    print(f"Logger initialized. Log file: {logger.log_file_path}")
    return logger
