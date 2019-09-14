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

from setuptools import setup, find_packages

__version__ = "0.0.2"
__release__ = "1.0.0"
__author__ = "Alexandru Gheorghe <irlanda@ro.plus>"


NAME = "SMSSender"

setup(
    name=NAME,
    version=__version__,
    packages=['sms_sender'],
    package_dir={'': 'src'},
    scripts=['bin/run.py'],

    # Generează script-urile și pentru hârburile de Windouze.
    entry_points={
        'console_scripts': [
            "sms_sender_nb.py = run:main"
        ]
    },

    install_requires=['docutils>=0.3'],

    package_data={'sms_sender': [
        'config/mesaj_sms.txt',
        '*.md',
        'LICENSE'],
    },

    # metadata to display on PyPI
    author=__author__,
    author_email="irlanda@ro.plus",
    description="Acest program a fost conceput pentru a trimite SMS-uri unor "
                "numere de telefon exportate din Nation Builder.",
    keywords="nation builder sms sender nationbuilder plus diaspora D1",
    url="https://www.ro.plus",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
    ],
)
