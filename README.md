Asyncode Runtime
================

What is Asyncode Runtime?
-------------------------

Asyncode Runtime (ACR) is BLSL Runtime that allows you to develop nearly any internet application using XML and ObjectPath selector language. It can connect to databases and manipulate data, send mails or interact with filesystem. It handles all low level details of HTTP protocol, makes one simple and consistent XML API giving the developer efficient way to create complex applications (e.g. business applications).

It runs on any WSGI compilant server. The standalone version is available and is default for this distribution of ACR. It is tested under:

1. Apache with mod_wsgi - resource consuming,
2. Python WSGIRef module - also resource consuming,
3. Nginx with uWSGI - fast and stable

What about Windows? It works, but it is not supported as of now.

Where is the documentation?
---------------------------

http://docs.asyncode.com/

Current state of the art
------------------------

ACR is stable piece of software, working in production but is maintained and used by very limited amount of users. It is well tested on our production server (VPS on OpenVZ, Debian, Nginx/UWSGI, PostgreSQL 8.3, MongoDB 2.0.1) and few applications. None of them is running under heavy load, but Apache Benchmark shows no serious problems when running with 100 or 1000 concurrent connections. It is due to uWSGI, but it shows that code is not resource demanding - it was implemented to be fast!

Security
--------

We place great emphasis on security and we always use the best practises we know. You can test ACR and send us bug reports. We'll fix bugs as fast as we can.

License notes
-------------

ACR is licensed under the GNU AGPL v3. Near all code is written by Adrian Kalbarczyk. There are some code taken from BSD/MIT licensed projects, but it is subject to change - you can find information about orginal authors in the files.

Please note that applications written in BLSL (the XML code) have their own licenses and they are not nessecairly free. You should look at first lines of each file to determine license. Also no license means that it is propertary and you can't do anything but read the code without asking author for permission. If you found file without license in header in this package contact us.

If you want to do something prohibited by GNU AGPL v3, you must buy commercial licence. It will cost you some money, but all funds will be used to make software better.

Contributions
-------------

If you like to donate some code, write tutorials, documentation or spread the word, feel free to do so. The prefered way to send code is e-mail right now. Please keep in mind that you would be asked in future about using your code in commercial products. This is one of ways to raise funds to develop high quality software - it's not cheap. You can be sure that your code WILL NOT be used in commercial products without your permission. Additional informations will be available at http://www.asyncode.com/contribute

Support
-------

There are two options for support. One is free community support (on http://docs.asyncore.com/ website). The other is business level support where you are sure about quick bug fix, answers to your questions etc. For the later contact me by e-mail. Support is provided only for Linux-based systems in English and Polish. Fell free to ask for other options.

Contact
-------

Website: http://www.asyncode.com/
E-mail: office@asyncode.com
