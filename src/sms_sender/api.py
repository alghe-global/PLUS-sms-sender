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
# Implementeaza:
# http://api.i-digital-m.com/v1/documentation
#

import sys
import json

import requests
from requests.auth import HTTPBasicAuth

from sms_sender.parser import parse_number

from sms_sender.util import get_user, get_password

from sms_sender.exceptions import (SMSApiException, SMSApiClientException,
                                   SMSApiMessageLengthExceeded)

from sms_sender.logger import get_logger

_log = get_logger(__name__)


class SMSApiClient(object):
    """
    Clasă ce implementează client-ul API pentru SMS.
    Mai multe informații `aici <_http://api.i-digital-m.com/v1/documentation>`_.

    * trimitere SMS
    * trimitere SMS Bulk
    """
    def __init__(self, user=None, passwd=None):
        """
        :param user: utilizatorul pentru autentificare
        :type user: str
        :param passwd: parola pentru autentificare
        :type passwd: str
        """
        self.user = user
        self.passwd = passwd

        if not self.user:
            _log.info("N-am găsit user-ul. Îl preiau de la utilizator. <3")
            _log.info("Utilizator: ")
            self.user = get_user()
            _log.debug("Am primit un utilizator: {}".format(self.user))
        if not self.passwd:
            _log.info("N-am găsit parola. O preiau de la utilizator. <3")
            self.passwd = get_password()
            _log.debug("Am primit parola. Nu ți-o zic. (╯°□°)╯︵ ┻━┻")

    def _make_request(self, request, data={}):
        """
        Dat un **request**, apelează API-ul și returnează rezultatul.

        :param request: request-ul cerut
        :type request: str
        :param data: date extra de pasat
        :type data: dict
        :returns: răspunsul cererii
        :rtype: json
        """
        response = {}

        try:
            _log.debug("API path: /{}".format(request))
            response = self._request(request=request, data=data,
                                     user=self.user, passwd=self.passwd)
            _log.debug("Request completat cu succes.")
            _log.debug(response)
        except SMSApiClientException as e:
            _log.critical("O eroare a avut loc atunci când am încercat să "
                          "fac cererea: {} ({})".format(request, e))
            raise
        return response

    def _request(self, request, data, user, passwd,
                 url="http://api.i-digital-m.com/v1/", method="POST"):
        """
        Returnează o instanțiere a `requests` ca fiind drept client-ul API.
        Dacă **method** nu este `POST`, atunci face default la o operație `GET`.

        :param request: cererea către API
        :type request: str
        :param data: de pasat API-ului pentru POST
        :type data: dict
        :param user: utilizatorul cu care să ne autentificăm față de API
        :type user: str
        :param passwd: parola cu care să ne autentificăm
        :type passwrd: str
        :param url: adresa URL de la API
        :type url: str
        :returns: requests
        :rtype: obj
        :raises: SMSApiException
        """
        self.url = url.lstrip("/")
        self.user = user
        self.passwd = passwd
        self.method = method

        self.data = data
        self.request = request
        self._request_path = "/".join([self.url, self.request])

        try:
            # XXX: un client care poate fi cache-uit ar fi ideal aici cu
            #      HTTPBasicAuth - planul acesta era, inițial, însă am renunțat
            #      la el datorită lipsei de timp (acest comment la 01:25 AM IST)
            #      P.S. asta ne-ar permite să implementăm și retry cu backoff
            #           exponențial pe următoarele (mereu setate pe request-uri
            #                                       limitate [throttle]):
            #
            #           Header
            #             Descriere
            #
            #           X-RateLimit-Reset
            #             Unix timestamp (UTC) when the request count gets reset
            #
            #           X-RateLimit-Remaining
            #             Amount of requests remaining in current timeframe
            #
            #           X-RateLimit-Limit
            #             Max amount of requests that can be made in current
            #             timeframe
            #
            if self.method == "POST":
                return requests.put(self._request_path, data=self.data,
                                    auth=HTTPBasicAuth(self.user, self.passwd))
            else:
                return requests.get(self._request_path, data=self.data,
                                    auth=HTTPBasicAuth(self.user, self.passwd))
        except Exception as e:
            _log.error("Cererea făcută la API a eșuat (URL: \"{}\"): {} "
                       "- user: {} (metodă: {})".format(self.url, e, self.user,
                                                         self.method),
                       exc_info=True)
            raise SMSApiException(e)

    def send_sms(self, sender, recipient, message, dlr=0, max_len=250):
        """
        Trimite un SMS de la numărul **sender**, către recipientul **recipient**
        cu mesajul **message**.

        :param sender: numărul de telefon de la care să vină SMS-ul
        :type sender: int
        :param recipient: numărul către care să se ducă SMS-ul
        :type recipient: int
        :param message: mesajul care să fie trimis ca fiind parte din SMS
        :type message: str
        :param dlr: dacă este 1 atunci un delivery receipt va fi primit,
                    altfel dacă 0 (implicit) un delivery receipt nu va fi primit
        :type dlr: int
        :param max_len: mărimea maximă a mesajului care poate fi folosită
        :type max_len: int (default 250)
        :returns: ID al SMS-ului care poate fi folosit pentru a îl identifica
                  în alte cereri către API (request-uri)
        :rtype: messageId
        :raises: SMSApiMessageLengthExceeded dacă mesajul e > 200 crct.
        :raises: SMSApiException dacă o problemă generică a fost întâmpinată
        """
        self.dlr = dlr

        self.sender = sender
        self.recipient = recipient

        self.message = message
        self.max_len = max_len

        if len(self.message) > self.max_len:
            _log.error("Mărimea mesajului este mai mare decât cea permisă "
                       "(mesaj {} > {} lungime permisă)."
                       "".format(len(self.message), self.max_len),
                       exc_info=True)
            raise SMSApiMessageLengthExceeded("Mărimea mesajului este mai mare "
                                              "decât cea permisă.")

        # compute request
        d = {
            "sender": self.sender,
            "recipient": self.recipient,
            "message": self.message,
            "dlr": self.dlr
        }

        # compute path
        path = "sms"

        response = {}
        try:
            req = self._make_request(request=path, data=d)
            if not isinstance(req, dict):
                _log.warn("REQ. EȘUAT: {}".format(req))
            else:
                response.update(json.loads(req))
        except Exception as e:
            _log.error("Cererea făcută la API a eșuat "
                       "(path: \"{}\")".format(path), exc_info=True)
            raise SMSApiException(e)

        if response.get("status", -1) == 0:
            _log.debug("Am primit răspuns valid pentru request: {}".format(d))
            return response
        else:
            _log.warn("Nu am primit răspuns valid pentru request: "
                      "{} (status code: {})".format(d, response.get("status")))
            return response

    def bulk_send_sms(self, sender, recipients, message, country_code, dlr=0):
        """
        Ca și :func:`send_sms`, numai că ia argumentul **recipient** drept listă
        și în caz că nu e o listă (ci e `str`, de exemplu), face conversie.

        :param country_code: codul de țară pentru număr (format IATA)
        :type country_code: str
        :returns: numerele care au fost procesate corect cărora li s-au trimis
                  mesajul sub formă de SMS
        :rtype: list
        """

        self.sender = sender
        self.recipients = recipients
        self.message = message
        self.dlr = dlr

        if not isinstance(self.recipients, (list, tuple)) or \
           not hasattr(self.recipients, "__iter__"):
            # singurul element din listă va fi self.recipients
            self.recipients = [self.recipients]

        answers = []
        for recipient in self.recipients:
            if isinstance(recipient, list) and len(recipient) == 1:
                recipient = recipient[0]
            else:
                _log.warn("Recipientul este o listă: {}".format(recipient))
                assert False, \
                    RuntimeError("O extorsiune a burlanului s-a produs.")
            _log.debug("Verific dacă numărul destinatar "
                       "este valid: {}".format(recipient))
            num = parse_number(recipient, country_code)
            if num:
                _log.debug("Numărul este valid: {}. Continui.".format(num))
            else:
                _log.warn("Numărul destinatar: \"{}\" este invalid pentru "
                          "country code-ul: \"{}\". SKIP!".format(recipient,
                                                                  country_code))
                continue
            _log.debug("Trimit mesajul către destinatar: {}".format(num))
            answers.append(self.send_sms(sender=self.sender,
                           recipient=num,
                           message=self.message,
                           dlr=self.dlr))
        if not answers:
            _log.info("Toate cererile au eșuat. :(")
        else:
            _log.info("Am trimis cererile.\nStatistică:\n\tDestinatari: {}  | "
                      "trimise cu succes: {}".format(len(self.recipients),
                                                     len(answers))
                      )
            _log.debug("Răspunsurile sunt: {}".format(answers))

        return answers
