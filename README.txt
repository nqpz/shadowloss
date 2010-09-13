
==========
shadowloss
==========

There's no release out yet.

You have no shadow, your limbs are all sticks, and your movements look
funny. You have been transformed into a stickman.

You have the ability to run very fast --- **extremely** fast. You can
run so fast that you are in a constant risk of hurting yourself. If
you don't slow down, you're going to run straight into a wall and die.

But how to slow down, you ask?

When you were a stickboy you had trouble learning the alphabet. To
this day your stickfriends still tease you. However, you have just
realized that letters are everywhere, and that whenever you pass a
letter while running, you just have to press that letter on your inner
keyboard. This will both make you learn the alphabet and slow down
(because you have to concentrate about the letter).

There is a catch: if you press a letter on your inner keyboard when
you're not passing it on your running path, your mind gets chaotic,
which makes you run even faster. You are forced to concentrate so that
you can come to a complete stop before you reach the wall.


License
=======

shadowloss is free software under the terms of the GNU General Public
License version 3 (or any later version). The author of shadowloss is
Niels Serup, contactable at ns@metanohi.org. This is version 0.1.0 of
the program.

The libraries used by shadowloss are GPL-compatible.

All data (music, sounds, etc.) is available under free licenses. See
the details in the file LICENSING.txt.

Installing
==========

Way #1
------
Just run this (requires that you have python-setuptools installed)::

  $ sudo easy_install shadowloss

Way #2
------
Get the newest version of shadowloss at
http://metanohi.org/projects/shadowloss/ or at
http://pypi.python.org/pypi/shadowloss

Extract the downloaded file and run this in a terminal::

  # python setup.py install

Dependencies
============

Python 2.5+ is probably a requirement.

``qvikconfig``
 + Web address: http://pypi.python.org/pypi/qvikconfig/
 + License: GPLv3+
 + Installing: ``$ sudo easy_install qvikconfig``
 + Author: Niels Serup

Note that ``qvikconfig`` is included with shadowloss, so you don't really
have to install it.

Optional extras
---------------
If present, shadowloss will also use these Python modules:

``termcolor``
 + Web address: http://pypi.python.org/pypi/termcolor/
 + License: GPLv3+
 + Installing: ``$ sudo easy_install termcolor``
 + Author: Konstantin Lepa <konstantin lepa at gmail com>

Note that ``termcolor`` is included with shadowloss, so you don't
really have to install it.
 
``setproctitle``
 + Web address: http://pypi.python.org/pypi/setproctitle/
 + License: New BSD License
 + Installing: ``$ sudo easy_install setproctitle``
 + Author: Daniele Varrazzo <daniele varrazzo at gmail com>


Using
=====

Simply running ``shadowloss`` will start the game with its default
options. Running ``shadowloss --help`` will show a list of available
command-line options. These options can also be specified in config
files, but they cannot be changed in-game (that would clutter the
interface). Config files use a ``property = value`` syntax
(e.g. ``fullscreen = true`` or ``resolution = 640x480``) separated by
newlines.


Developing
==========

shadowloss is written in Python and uses Git for branches. To get the
latest branch, get it from gitorious.org like this::

  $ git clone git://gitorious.org/shadowloss/shadowloss.git

A number of shadowloss mods can be fetched using git as well::

  $ git clone git://gitorious.org/shadowloss/shadowloss-mods.git


This document
=============
Copyright (C) 2010  Niels Serup

Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
