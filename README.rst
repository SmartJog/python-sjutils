==============
python-sjutils
==============

python-sjutils is a collection of helper classes and functions used through
various daemons at SmartJog.

License
=======

python-sjutils is released under the `GNU LGPL 2.1 <http://www.gnu.org/licenses/lgpl-2.1.html>`_.


Build and installation
=======================

Bootstrapping
-------------

python-sjutils uses the autotools for its build system.

If you checked out code from the git repository, you will need
autoconf and automake to generate the configure script and Makefiles.

To generate them, simply run::

    $ autoreconf -fvi

Building
--------

python-sjutils builds like your typical autotools-based project::

    $ ./configure && make && make install


Development
===========

We use `semantic versioning <http://semver.org/>`_ for
versioning. When working on a development release, we append ``~dev``
to the current version to distinguish released versions from
development ones. This has the advantage of working well with Debian's
version scheme, where ``~`` is considered smaller than everything (so
version 1.10.0 is more up to date than 1.10.0~dev).


Authors
=======

python-sjutils was started at SmartJog by Romain Degez.
Various employees and interns from SmartJog fixed bugs and added features since
then.

* Alexandre Bossard
* Frédéric Julian
* Gilles Dartiguelongue
* Guillaume Camera
* Jean-Philippe Garcia Ballester
* Laurent Corbes
* Laurent Defert
* Matthieu Bouron
* Nicolas Noirbent
* Philippe Bridant
* Rémi Cardona
* Romain Degez
* Stéphane Kanschine
* Thomas Meson
* Thomas Souvignet

