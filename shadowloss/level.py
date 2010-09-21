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
            spl = x.split('\\')
            try:
                default_decrease = float(spl[1])
            except IndexError:
                default_decrease = None
            try:
                default_letter_speed = int(float(spl[2]) * 1000)
            except IndexError:
                default_letter_speed = None
            spl = spl[0].split(':')
            pos = float(spl[0])
            parts = []
            for y in spl[1:]:
                bspl = y.split('/')
                letter = bspl[0]
                try:
                    decrease = float(bspl[1])
                except Exception:
                    decrease = default_decrease
                try:
                    letter_speed = int(float(bspl[2]) * 1000)
                except Exception:
                    letter_speed = default_letter_speed
                surf = self.parent.create_text(letter, 75)
                parts.append([letter, surf, surf.get_size()[0],
                              decrease, letter_speed, ''])
            nletters.append([pos, parts, 0, 0])
        nnumbers = []
        for x in data['numbers']:
            spl = x.split(':')
            pos = float(spl[0])
            number = spl[1]
            surf = self.parent.create_text(number, 40)
            nnumbers.append([pos, int(number), surf, surf.get_size()[0]])

        self.letters = nletters
        self.numbers = nnumbers
        self.start_speed = float(data.get('start speed') or 1.0)
        self.end_speed = float(data.get('end speed') or 0.0)
        self.start_pos = float(data.get('start position') or 0.0)
        if self.start_pos is None:
            self.start_pos = 0
        self.length = data['length']
        self.speed_increase = float(data.get('default speed increase') or 0.5)
        self.temp_speed_increase = float(data.get('default temporary speed increase') or 1.0)
        self.speed_increase_per_second = float(data.get('speed increase per second') or 0)
        self.speed_decrease = float(data.get('default speed decrease') or 0.5)
        self.letter_speed = int(float(data.get('default letter changing speed') or 0.5) * 1000)
        self.stickfigure = builtinstickfigures[data.get('stickfigure')
                                               or 'bob'].create(self.parent)
        self.start()

    def start(self):
        self.speed = self.start_speed
        self.pos = self.start_pos
        self.time = 0
        self.temp_speed_still = 0
        self.orig_time = datetime.datetime.now()
        self.prev_time = self.orig_time
        for x in self.letters:
            x[3] = 0
        self.body_color = (255, 255, 255)
        self.parent.fill_borders(self.body_color)
        self.status = PLAYING

    def color_foreground(self):
        self.parent.fill_borders(self.body_color)
        for x in self.letters:
            for y in x[1]:
                y[1] = self.parent.create_text(y[0], 75, self.body_color)
        for x in self.numbers:
            x[2] = self.parent.create_text(str(x[1]), 40, self.body_color)

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
            self.speed += self.speed_increase_per_second
            if self.temp_speed_still > 0:
                self.temp_speed_still -= 1
                if self.temp_speed_still == 0:
                    self.speed -= self.temp_speed_increase

        self.pos += self.speed * (increase / 10.0)
        if self.pos >= self.length:
            self.lose()

        ok = False
        for x in self.letters:
            part = x[1][x[2]]
            if x[0] - part[2] / 2 <= self.pos <= x[0] + part[2] / 2:
                test = part[0].lower()
                for y in letters:
                    if test.startswith(part[5] + y):
                        part[5] += y
                        if part[5] == test:
                            self.letters.remove(x)
                            self.speed -= part[3] or self.speed_decrease
                    else:
                        self.speed += self.speed_increase
                        part[5] = ''
                ok = True
                break

            x[3] += increase
            if x[3] >= (part[4] or self.letter_speed):
                x[3] = x[3] % (part[4] or self.letter_speed)
                part[5] = ''
                x[2] = (x[2] + 1) % len(x[1])
                
        if not ok:
            for x in letters:
                self.speed += self.speed_increase

        for x in self.numbers:
            if x[0] - x[3] / 2 <= self.pos <= x[0] + x[3] / 2:
                self.numbers.remove(x)
                self.temp_speed_still = x[1]
                self.speed += self.temp_speed_increase

        if self.speed <= self.end_speed:
            self.win()

    def draw(self):
        for x in self.letters:
            self.parent.blit(x[1][x[2]][1], (x[0] - self.pos +
                                    self.parent.virtual_size[0] / 2, 0))
        for x in self.numbers:
            self.parent.blit(x[2], (x[0] - self.pos +
                                   self.parent.virtual_size[0] / 2, 0))
        self.stickfigure.draw(self.time, self.speed, self.body_color)
        self.parent.draw_wall(-1, self.parent.virtual_size[0] / 2 -
                               self.pos, self.body_color)
        self.parent.draw_wall(self.length - self.pos + self.parent.virtual_size[0] /
                              2, self.parent.virtual_size[0] + 1, self.body_color)
