===================
 Bricklayer project
===================

Bricklayer builds packages to help you automate builds and upload them to
repositories.


Requirements
============

Bricklayer uses twisted to serve a restful interface as well as the scheduler
interface, it also needs Redis 2.0 or higher to store projects. Depending on
the linux/unix flavor, you have to install Redis by yourself since not all the
distros include redis-2.0 yet.


Installation
============

Bricklayer has a debian directory ready to be built. To do so under a
debian-based system just run (after install Redis):

        export PYTHONPATH="."
        apt-get -y install build-essential devscripts cdbs python-twisted python-setuptools python-simplejson redis-server
        apt-get -y install python2.5-dev && easy_install multiprocessing ## if using Python 2.5 ##
        dpkg-buildpackage -rfakeroot # (inside the project directory)
        dpkg -i ../bricklayer*.deb # were * is your architecture and version



HTTP API
========

* :doc:`Bricklayer has a restful interface that accepts a JSON payload <http_api>`

.. toctree::
  :hidden:

  http_api


Development
===========

Some tools are needed in order to run bricklayer on your development environment.

Firstly install redis-server

::

  apt-get -y install redis-server


If you already have python installed, you can use pip for twisted:

::

  pip install twisted

Use python path on the current directory, so the namespace will be acessible:

::

  export PYTHONPATH="."

Point the bricklayer config file to the local one:

::

  export BRICKLAYERCONFIG=etc/bricklayer/bricklayer.ini

Run twisted to get the bricklayer interface available at http://localhost

::

  twistd -ny bricklayer/bricklayer.tac

Run the bricklayer consumers

::

  python bricklayer/build_consumer.py


Building ruby applications ?
============================

Bricklayer uses RVM to handle multiple ruby projects to be built in the same
machine. To use rvm you must provide a .rvmrc or .rvmrc.example (if you don't
want a .rvmrc hanging on your project repository) using the rvmrc syntax as
usual. It is highly recommended that you use this if you are building multiples
projects using different ruby versions.


What else ?
===========

It is important to note that bricklayer itself does nothing (beside watch your
repository for tags and changes) but do what you told him to do, that means, if
your project doesn't has enough automation to be able to pack itself by using
scripts or make-like tasks the very best bricklayer can do is to provide
templates that will copy everything in your project directory to a specific
installation directory, still a package will be generated but no customizations
will be made so BE AWARE and automate your project right way :D


Changelog
=========

* https://raw.github.com/locaweb/bricklayer/master/CHANGELOG


License
=======

APACHE 2.0


Help
====

Having problems, questions or suggestions? Don't hesitate to reach us!

* IRC(freenode): #bricklayer;
* bricklayer@listadev.email.locaweb.com.br;
