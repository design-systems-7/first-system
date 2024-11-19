# import logging
# import sys
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO) # set logger level
# logFormatter = logging.Formatter\
# ("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
# consoleHandler = logging.StreamHandler(sys.stdout) #set streamhandler to stdout
# consoleHandler.setFormatter(logFormatter)
# logger.addHandler(consoleHandler)

import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss} | <level>{message}</level> </green>",
           colorize=True, enqueue=True)
