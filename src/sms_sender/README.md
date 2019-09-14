### SMS Sender

#### Instalare

##### Windows

Executabilul `.exe` se deschide pentru ca instalarea să aibă loc.

##### Linux

Instalarea se face prin executarea comenzii următoare:

    sudo setup.py install

#### Cum se folosește?

Se execută din linia de comandă.

Pentru a afla opțiunile:

    sms_sender_nb.py -h

Opțiunile importante ar fi:

* -c -- este țara care ar trebui să fie luată în considerare pentru parsarea numerelor (de ex., „GB” ar fi pentru Marea Britanie - toate numerele din fișier vor fi asumate ca fiind GB)

* -f -- este fișierul CSV exportat din NB

* -e -- este numărul care va fi afișat la destinatar ca fiind emițătorul (acolo va da reply)

#### Logare

Programul produce două log-uri separate:

1. Este log-ul ce ține de programul în sine (app.log*)

2. Este log-ul ce ține de trimiterea SMS-urilor (sms.log*)

Conținutul log-urilor vor fi printate oricum pe ecran.


