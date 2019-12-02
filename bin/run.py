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
from sms_sender.util import (_return_csv_as_dict, build_list_of_numbers,
                             get_message)

__version__ = "0.0.2"


_log = get_logger(__name__)

_DEFAULT_SMS_FILE = "config/mesaj_sms.txt"

MAX_LENGTH_SENDER_DIGIT = 25
MAX_LENGTH_SENDER_ALPHA = 11
MAX_LENGTH_SMS_BODY = 160


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
    parser.add_argument("-s", "--sms", dest="sms", type=str,
                        required=False,
                        help="mesajul care să fie trimis, specificat în linia "
                             "de comandă.\nNOTĂ: dacă este setat, programul NU "
                             "va citi mesajul din fișier!")
    parser.add_argument("-m", "--sms-file", dest="sms_file", type=str,
                        required=False, default=None,
                        help="fișierul care să conțină mesajul SMS. "
                             "dacă nu este specificat, atunci fișierul \"{}\" "
                             "va fi folosit".format(_DEFAULT_SMS_FILE))
    parser.add_argument("-l", "--lungime", dest="sms_length", action="store_true",
                        required=False, default=False,
                        help="când este specificată această opțiune, "
                             "SMS-ul va fi partajat în mai multe mesaje "
                             "dacă mărimea mesajului întreg depașește {} "
                             "caractere în total; implicit, nu se vor trimite "
                             "SMS-urile, dacă mesajul depășește lungimea "
                             "permisibilă".format(MAX_LENGTH_SMS_BODY))
    parser.add_argument("-e", "--emitator", dest="sender", type=str,
                        required=True,
                        help="numarul de la care să se "
                             "trimită SMS")
    parser.add_argument("-c", "--country-code", dest="country_code", type=str,
                        required=True,
                        help="țara asumată atunci când numerele de telefon "
                             "sunt citite din fișier")
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()

    if args.sms:
        message = args.sms
    else:
        if args.sms_file:
            message = get_message(args.sms_file)
        else:
            message = get_message(_DEFAULT_SMS_FILE, fix_path=True)

    if not message and not args.sms:
        _log.fatal("Nu am un mesaj SMS cu care să pornesc. "
                   "Poți crea fișierul sau să-l specifici din linia de "
                   "comandă. Apelează script-ul cu argumentul -h sau --help "
                   "pentru mai multe informații.")
        sys.exit(1)

    if not args.sms_length and len(message) > MAX_LENGTH_SMS_BODY:
        _log.fatal("Lungimea totală a mesajului SMS ({}) depășește pe cea permisibilă ({}).\n"
                   "Poți dezactiva această protecție prin a restarta aplicația introducând și "
                   "opțiunea „-l” („--lungime”) pentru a partaja mesajul în mai multe bucăți "
                   "și a forța trimiterea lui (ATENȚIE: rețelele de telefonie s-ar putea să "
                   "blocheze mesajele dacă acestea sunt multe la număr și sunt trimise către "
                   "multe numere de telefon! Folosiți cu grijă).".format(len(message),
                                                                         MAX_LENGTH_SMS_BODY)
                   )
        sys.exit(1)
    elif args.sms_length and len(message) > MAX_LENGTH_SMS_BODY:
        _log.debug("Lungimea totală a mesajului SMS ({}) depășește pe cea permisibilă ({}), "
                   "însă mi s-a comunicat să partajez mesajul. Continui!\n"
                   "ATENȚIE: mesajele separate vor costa fiecare cât un SMS individual! Prin "
                   "urmare, veți suporta consecințele costurilor!".format(len(message),
                                                                          MAX_LENGTH_SMS_BODY)
                   )

    if not args.sender:
        _log.fatal("Un emițător trebuie menționat. Nu pot continua altfel.")
        sys.exit(1)
    elif args.sender.replace(" ", "").isalpha() and \
            len(args.sender) > MAX_LENGTH_SENDER_ALPHA:
       _log.fatal("Numele folosit pentru emițător este prea lung ({}). "
                  "Lungimea maximă permisă este de: {}.\n"
                  "Folosește un nume de o mărime mai mică.".format(len(args.sender), MAX_LENGTH_SENDER_ALPHA))
       sys.exit(1)
    elif args.sender.replace("+", "").replace(" ", "").isdigit() and \
            len(args.sender) > MAX_LENGTH_SENDER_DIGIT:
       _log.fatal("Numărul folosit pentru emițător este prea lung ({}). "
                  "Lungimea maximă permisă este de: {}.\n"
                  "Folosește un număr de o mărime mai mică.".format(len(args.sender), MAX_LENGTH_SENDER_DIGIT))
       sys.exit(1)

    if not isinstance(message, str) and hasattr(message, '__iter__'):
        # este o iterabila: incarca drept un singur string
        message = "".join(message)

    message = message.lstrip("\n").rstrip("\n")
    _log.debug("Am încărcat SMS-ul ce trebuie trimis. Acesta este:\n"
               "--- ÎNCEPE TEXT SMS ---\n\n"
               "{}\n\n"
               "--- ÎNCHEIE TEXT SMS ---".format(message))

    data = _return_csv_as_dict(args.file)
    numbers = build_list_of_numbers(data)

    client = SMSApiClient()

    ans = client.bulk_send_sms(sender=args.sender, message=message,
                               recipients=numbers,
                               country_code=args.country_code,
                               dlr=1)
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

    _log.info("Am terminat procedura de trimitere. "
              "Salvez în DEBUG mode răspunsurile primite de la server.")
    _log.debug("\n----------------------------\n")
    _log.debug(json.dumps(ans, indent=4))
    _log.debug("\n----------------------------\n")

    _log.info("Salvez datele.")
    with open("sms_log_{}".format(time.strftime("%Y_%m_%d-%H_%M_%S")), "ab") \
            as fobj:
        fobj.write(json.dumps(ans, indent=4))
    _log.debug("Gata. Totul s-a terminat cu succes.")
    sys.exit(0)
