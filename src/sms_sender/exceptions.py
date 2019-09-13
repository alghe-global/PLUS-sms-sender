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


class SMSException(Exception):
    """Generică"""
    pass


class SMSApiException(SMSException):
    """Generică la nivel de API pentru SMS"""
    pass


class SMSApiClientException(SMSException):
    """Generică la nivel de insanțiere a clientului API pentru SMS"""
    pass


class SMSApiMessageLengthExceeded(SMSException):
    """Dacă mesajul pentru SMS a depăsit o anumită mărime"""
    pass
