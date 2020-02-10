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
# http://api.i-digital-m.com/v2/documentation
#

import getpass
import errno

from csv import DictReader


def _return_csv_as_dict(csv_file):
    return DictReader(open(csv_file, "rb"))


def build_list_of_numbers(data):
    """
    Dată fie o listă de dicționare (list[hash]), returnează o listă de numere
    mobile.

    :param data: listă cu dicționare
    :type data: list
    :returns: listă cu numere (în ordinea aceasta:
      mobile_number > phone_number > work_phone_number)
    :rtype: list
    """

    nums = []
    for d in data:
        nums.append([
            d.get("mobile_number") if d.get("mobile_number") else
            d.get("phone_number") if d.get("phone_number") else
            d.get("work_phone_number") if d.get("work_phoe_number") else
            None
        ])

    return nums


def get_password(password=None):
    """
    Apelează la stdin pentru a obține parola de la utilizator.

    :param password: parola deja specificată
    :type password: str
    :returns: getpass.getpass
    :rtype: str
    """
    if not password:
        return getpass.getpass()
    return password


def get_user(user=None):
    """
    Apelează la stdin pentru a obține user-ul de la utilizator.

    :param user: utilizator deja specificat
    :type user: str
    :returns: getpass.getuser
    :rtype: str
    """
    if not user:
        user = getpass._raw_input()
    return user


def get_message(file, fix_path=False):
    """
    Dat fiind obiectul **file**, încearcă să returneze conținutul.
    Dacă fișierul nu există, returnează None.

    :param file: fișierul cu pricina
    :type file: str
    :returns: conținutul fișierului \n splitted
    :rtype: str sau None (dacă fișierul nu există)
    """
    if fix_path:
        fpath = "/".join(["/".join(__file__.split("/")[:-1]),
                         file])
    else:
        fpath = file

    try:
        return "".join(open(fpath, "rb").readlines())
    except IOError as e:
        if e.errno == errno.ENOENT:
            return None
        elif len(e.args) > 1 and isinstance(e.args[1], str):
            if "no such file" in e.args[1].lower():
                return None
        else:
            raise
