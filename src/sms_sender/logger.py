# -*- encoding: utf-8 -*-
#
# GNU GENERAL PUBLIC LICENSE
#
# Version 2, June 1991
#
# Copyright (C) 1989, 1991 Free Software Foundation, Inc.
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# Pentru informatii, contactati: contact@ro.plus
# https://www.ro.plus/contact
#

import sys
import time

import logging

from datetime import datetime

LOG_FORMATTER = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt=datetime.isoformat(datetime.utcnow())+"Z")


def get_logger(name=None, level=logging.DEBUG):
    """
    Returnează un logger formatat. Standardizează logarea pe mai multe domenii.

    :param name: numele cu care logger-ul să fie configurat
    :type name: str
    :param level: nivelul pentru logging (logging.[INFO,DEBUG ...])
    :type level: logging.LEVEL
    :returns: logging.getLogger instance
    :rtype: obj
    """
    if not name:
        name = __name__
    root_logger = logging.getLogger(name)
    root_logger.setLevel(level)

    fileHandler = logging.FileHandler("app.log_{}".format(
        time.strftime("%Y-%m-%d_%H-%M")), mode="ab")
    fileHandler.setFormatter(LOG_FORMATTER)
    root_logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(LOG_FORMATTER)
    root_logger.addHandler(consoleHandler)

    return root_logger
