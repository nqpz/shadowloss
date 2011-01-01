
==========
shadowloss
==========

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

Later on, when you have realized the power of the alphabet, you must
learn to accept how numbers behave as well. The thing is, passing
through numbers make you go faster for a while. For example, if you
cross the number 3, your speed will be greater for 3 seconds, after
which it will decrease. The reason why you react this way is because
you *like* numbers. You simply don't have to concentrate to understand
them --- and because of that, you speed up, but only until you realize
that you should slow down. The higher the number, the longer it takes
for you to realize that. If you feel like it, you can always destroy
numbers with your laser beam, but sometimes it may be beneficial to
speed up temporarily.


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

shadowloss depends on cairo and cairo's Python bindings for generating
images. To install it, do one of these things:

* For DEB-based distros (Debian etc.): type ``apt-get install python-cairo``
* For RPM-based distros (Fedora etc.): type ``yum install pycairo``
* For other distros: do something similar or get it at
  http://cairographics.org/download/

shadowloss depends on PyGame 1.8.1+ (perhaps earlier versions are also
supported) for showing generated images. To install it, do one of
these things:

* For DEB-based distros (Debian etc.): type ``apt-get install python-pygame``
* For RPM-based distros (Fedora etc.): type ``yum install pygame``
* For other distros: do something similar or get it at
  http://pygame.org/download.shtml

shadowloss depends on qvikconfig for parsing config files.

 + Web address: http://pypi.python.org/pypi/qvikconfig/
 + License: GPLv3+
 + Installing: ``easy_install qvikconfig``
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
(e.g. ``fullscreen = true`` or ``size = 640x480``) separated by
newlines.

Controls
--------

::

  <letter>: letter
  <SPACE>:  when playing:           laser beam
  <SPACE>:  when level is finished: next level
  <RIGHT>:  when level is finished: next level
  <LEFT>:   when level is finished: previous level
  r:        when level is finished: restart level
  ESCAPE:   quit program


Creating levels
===============

shadowloss levels are simple config files. They consist of global and
local options. **Global options:**

* ``start speed`` (what speed to start at, default 1.0)
* ``stop speed`` (what speed to stop at, default 0.0)
* ``start position`` (where to start, default 0.0)
* ``length`` (length of level, default 500)
* ``speed increase`` (when pressing a wrong letter, default 0.5)
* ``speed increase per second`` (default 0.0)
* ``stickfigure`` (what stickfigure to use, currently only 'zorna' and
  'bob', default 'zorna')
* ``font height``
* ``letter height`` (default 75, overrides 'font height')
* ``number height`` (default 40, overrides 'font height')
* ``default temporary speed increase`` (during number penalties)
* ``default speed decrease`` (when pressing a correct letter)
* ``default object duration`` (the duration of a subobject, default 0.5)
* ``default letter duration`` (overrides 'default object duration')
* ``default number duration`` (overrides 'default object duration')
* ``default object destruction duration`` (the time it takes for a laser
  beam to destroy the object, default 0.3)
* ``default letter destruction duration`` (overrides 'default object
  duration')
* ``default number destruction duration`` (overrides 'default object
  duration')
* ``letters``
* ``numbers``

Except for ``letters`` and ``numbers``, all of these options need only
simple numbers assigned to them. ``letters`` and ``numbers`` are
lists, and they offer support for local options. **Syntax:**

::

  letters|numbers = <position>:<letter1>(opt1=val1;opt2=val2;...):\
  <letter2>:...[opt3=val3;opt4=val4]

Options enclosed in ``()`` are local options, while those in ``[]``
are global (object-wise). **Local options:**

* ``letters``

  + ``dec`` (overrides ``default speed decrease``)
  + ``dur`` (overrides ``default letter duration``)
  + ``ddur`` (overrides ``default letter destruction duration``)

* ``numbers``

  + ``inc`` (overrides ``default temporary speed increase``)
  + ``dur`` (overrides ``default number duration``)
  + ``ddur`` (overrides ``default number destruction duration``)

**Example:**

::

  letters = 230:A(dec=0.3;dur=1;ddur=0.1):Q:R[dur=0.5]
  

Developing
==========

shadowloss is written in Python and uses Git for branches. To get the
latest branch, get it from gitorious.org like this::

  $ git clone git://gitorious.org/shadowloss/shadowloss.git


This document
=============
Copyright (C) 2010  Niels Serup

Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
