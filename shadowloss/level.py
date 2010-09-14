#!/usr/bin/env python
# -*- coding: utf-8 -*-

# shadowloss: a stickman-oriented game against time
# Copyright (C) 2010  Niels Serup

# This file is part of shadowloss.
#
# shadowloss is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# shadowloss is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with shadowloss.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## shadowloss.level
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Controls levels
##[ Start date  ]## 2010 September 13

import datetime
import shadowloss.various as various
import shadowloss.stickfigure as stick
try:
    from qvikconfig import parse as config_parse
except ImportError:
    from shadowloss.external.qvikconfig import parse as config_parse

class Level(object):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        data = config_parse(path)
        nletters = []
        for x in data['letters']:
            spl = x.split(':')
            pos = int(spl[0])
            surf = self.parent.create_text(spl[1])
            nletters.append((pos, spl[1], surf, pos + surf.get_size()[0]))
        self.letters = nletters
        self.start_speed = data.get('start speed') or 1
        self.start_pos = data.get('start position')
        if self.start_pos is None:
            self.start_pos = 0
        self.length = data['length']

        self.stickfigure = stick.StickFigure(self.parent, None, stick.LinearChange((0, 250, 0, 25), (250, 500, 25, 5), (500, 750, 5, 10), (750, 1000, 10, 0)))
        # Create its limbs
        self.stickfigure.add_line(None, 'A', stick.LinearChange((0, 500, 70, 110), (500, 1000, 110, 70)), lambda info: 40)
        self.stickfigure.add_line(None, 'A', stick.LinearChange((0, 500, 110, 70), (500, 1000, 70, 110)), lambda info: 40)
        self.stickfigure.add_line('A', 'B', lambda info: 90, lambda info: 30)
        self.stickfigure.add_line('B', None, stick.LinearChange((0, 500, -140, -40), (500, 1000, -40, -140)), lambda info: 25)
        self.stickfigure.add_line('B', None, stick.LinearChange((0, 500, -40, -140), (500, 1000, -140, -40)), lambda info: 25)
        self.stickfigure.add_line('B', 'C', lambda info: 50 * info.speed, lambda info: 20)
        self.stickfigure.add_circle('C', lambda info: 13)

        self.start()

    def start(self):
        self.speed = self.start_speed
        self.pos = self.start_speed
        self.time = 0
        self.orig_time = datetime.datetime.now()
        self.prev_time = self.orig_time
        self.status = 0

    def update(self, letters=[]):
        if self.status == 1:
            return

        now = datetime.datetime.now()
        increase = ((now - self.orig_time) - (self.prev_time - self.orig_time)).microseconds / 1000
        self.time += increase * self.speed
        self.prev_time = now
        if self.time >= 999:
            self.time = self.time % 1000

        self.pos += self.speed * (increase / 10.0)
        if self.pos >= self.length:
            self.status = 1

        ok = False
        for x in self.letters:
            if x[0] <= self.pos <= x[3]:
                test = x[1].lower()
                for x in letters:
                    if x == test:
                        self.speed -= 0.5
                    else:
                        self.speed += 0.5
                ok = True
                break
        if not ok:
            for x in letters:
                self.speed += 0.5

        if self.speed <= 0:
            self.status = 1

    def draw(self):
        for x in self.letters:
            self.parent.blit(x[2], (x[0] - self.pos +
                                    self.parent.virtual_size[0] / 2, 0))
        self.stickfigure.draw(self.time, self.speed)
        self.parent.draw_wall(-1, self.parent.virtual_size[0] / 2 - self.pos)
        self.parent.draw_wall(self.length - self.pos + self.parent.virtual_size[0] /
                              2, self.parent.virtual_size[1] * 1.5)
        
