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
from shadowloss.builtinstickfigures import stickfigures as builtinstickfigures
try:
    from qvikconfig import parse as config_parse
except ImportError:
    from shadowloss.external.qvikconfig import parse as config_parse

PLAYING = 0
WON = 1
LOST = 2

class Level(object):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        data = config_parse(path)
        nletters = []
        for x in data['letters']:
            spl = x.split(':')
            pos = float(spl[0])
            try:
                dec = float(spl[2])
            except Exception:
                dec = None
            surf = self.parent.create_text(spl[1], 75)
            nletters.append((pos, spl[1], surf, pos +
                             surf.get_size()[0], dec))
        self.letters = nletters
        self.start_speed = float(data.get('start speed') or 1.0)
        self.end_speed = float(data.get('end speed') or 0.0)
        self.start_pos = float(data.get('start position') or 0.0)
        if self.start_pos is None:
            self.start_pos = 0
        self.length = data['length']
        self.speed_increase = float(data.get('default speed increase') or 0.5)
        self.speed_decrease = float(data.get('default speed decrease') or 0.5)

        self.stickfigure = builtinstickfigures[data.get('stickfigure')
                                               or 'bob'].create(self.parent)
        self.start()

    def start(self):
        self.speed = self.start_speed
        self.pos = self.start_speed
        self.time = 0
        self.orig_time = datetime.datetime.now()
        self.prev_time = self.orig_time
        self.body_color = (255, 255, 255)
        self.parent.fill_borders(self.body_color)
        self.status = PLAYING

    def color_foreground(self):
        self.parent.fill_borders(self.body_color)
        self.letters = list([list(x) for x in self.letters])
        for x in self.letters:
            x[2] = self.parent.create_text(x[1], 75, self.body_color)

    def lose(self):
        self.status = LOST
        self.body_color = (255, 0, 0)
        self.color_foreground()

    def win(self):
        self.status = WON
        self.body_color = (0, 255, 0)
        self.color_foreground()

    def update(self, letters=[]):
        if self.status != PLAYING:
            return

        now = datetime.datetime.now()
        increase = ((now - self.orig_time) - (self.prev_time - self.orig_time)).microseconds / 1000
        self.time += increase * self.speed
        self.prev_time = now
        if self.time >= 999:
            self.time = self.time % 1000

        self.pos += self.speed * (increase / 10.0)
        if self.pos >= self.length:
            self.lose()

        ok = False
        for x in self.letters:
            if x[0] <= self.pos <= x[3]:
                test = x[1].lower()
                for y in letters:
                    if y == test:
                        self.letters.remove(x)
                        self.speed -= x[4] or self.speed_decrease
                    else:
                        self.speed += self.speed_increase
                ok = True
                break
        if not ok:
            for x in letters:
                self.speed += 0.5

        if self.speed <= self.end_speed:
            self.win()

    def draw(self):
        for x in self.letters:
            self.parent.blit(x[2], (x[0] - self.pos +
                                    self.parent.virtual_size[0] / 2, 0))
        self.stickfigure.draw(self.time, self.speed, self.body_color)
        self.parent.draw_wall(-1, self.parent.virtual_size[0] / 2 -
                               self.pos, self.body_color)
        self.parent.draw_wall(self.length - self.pos + self.parent.virtual_size[0] /
                              2, self.parent.virtual_size[0] + 1, self.body_color)
