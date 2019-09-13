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

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from sms_sender.logger import get_logger

_log = get_logger(__name__)


def _parse_phone_number(number, country_code):
    n = phonenumbers.parse(number, country_code)
    # verifică daca e un număr valid
    if phonenumbers.is_possible_number(n) and \
       phonenumbers.is_valid_number(n):
        # returnează numărul în format internațional
        return phonenumbers.format_number(n,
                                          phonenumbers.PhoneNumberFormat.E164)
    else:
        return None


def parse_number(number, country_code="GB"):
    """
    Parsează numărul **number** cu un cod de țară **country_code** (default: GB)

    :param number: numărul de telefon
    :type number: str
    :param country_code: țara de care aparține numărul de telefon
    :type country_code: nume țară (format în standard IATA) din două litere
                        (ex. GB stă pentru Great Britain, IE pentru Ireland)
    :returns: phonenumbers.PhoneNumberFormat.E164 sau -1 dacă numărul e invalid
              al
    :rtype: phonenumbers.PhoneNumberFormat.E164, None
    """
    try:
        return _parse_phone_number(number=number, country_code=country_code)
    except NumberParseException:
        _log.warn("Numărul: \"{}\" este invalid "
                  "(country code setat: {}).".format(number, country_code))
        return None
