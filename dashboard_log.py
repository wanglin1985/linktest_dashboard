"""
This module is used to:
 1. create the framework_logger instance
 2. if not set framework_logger level in settings then set log level to "INFO" as default

Note:
    can add below code in settings to change the framework_logger's level:
    import logging
    FRAMEWORK_LOGGER_LEVEL = logging.DEBUG

@author: Lin.Wang
"""
import logging
import os

output_folder = os.path.dirname(os.path.realpath(__file__)) + os.sep + "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

execution_log_file = output_folder + os.sep + "dashboard.log"

logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] %(levelname)s %(filename)s %(lineno)d: %(message)s")
framework_logger = logging.getLogger("EF_COMMON_FRAMEWORK")
fileHandler = logging.FileHandler(execution_log_file)
fileHandler.setFormatter(logFormatter)
framework_logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
framework_logger.addHandler(consoleHandler)
framework_logger.setLevel(logging.DEBUG)
