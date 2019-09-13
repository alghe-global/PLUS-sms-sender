#!/usr/bin/env python
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
import argparse

import json

from sms_sender.api import SMSApiClient

from sms_sender.logger import get_logger
from sms_sender.util import _return_csv_as_dict, build_list_of_numbers

__version__ = "0.0.2"

_log = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Script ce citește un CSV din NationBuilder "
                    " și trimite SMS-uri.",
        epilog="O muncă depusă de către filiala D1"
    )
    parser.add_argument("-f", "--file", dest="file", type=str,
                        required=True,
                        help="fișierul CSV exportat din NB\n"
                             "NOTĂ: trebuie să aibă una din coloanele: "
                             "mobile_number, phone_number sau "
                             "work_phone_number")
    parser.add_argument("-m", "--mesaj", dest="message", type=str,
                        required=True,
                        help="mesajul care să fie trimis")
    parser.add_argument("-e", "--emitator", dest="sender", type=str,
                        required=True,
                        help="numarul de la care sa se "
                             "trimita SMS")
    parser.add_argument("-c", "--country-code", dest="country_code", type=str,
                        required=True,
                        help="țara asumată atunci când numerele de telefon "
                             "sunt citite din fișier")
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()

    data = _return_csv_as_dict(args.file)
    numbers = build_list_of_numbers(data)

    client = SMSApiClient()
    ans = client.bulk_send_sms(sender=args.sender, message=args.message,
                               recipients=numbers,
                               country_code=args.country_code)
    if ans == [{}]:
        _log.warn("A intervenit o eroare.")
        _log.info("Salvez datele.")
        with open("sms_log_{}".format(time.strftime("%Y_%m_%d-%H_%M_%S")), "ab") \
                as fobj:
            fobj.write(json.dumps(ans, indent=4))
        sys.exit(1)
    elif len(ans) != len(numbers):
        _log.warn("Nu toate numerele au primit un SMS "
                  "(trimise: {}, numere: {}).".format(len(ans), len(numbers)))

    _log.info("Toate numerele au primit un SMS.")
    _log.debug("\n----------------------------\n")
    _log.debug(json.dumps(ans, indent=4))
    _log.debug("\n----------------------------\n")

    _log.info("Salvez datele.")
    with open("sms_log_{}".format(time.strftime("%Y_%m_%d-%H_%M_%S")), "ab") \
            as fobj:
        fobj.write(json.dumps(ans, indent=4))
    _log.debug("Gata. Totul s-a terminat cu succes.")
    sys.exit(0)
