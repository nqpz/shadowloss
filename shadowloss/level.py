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
import re
import shadowloss.various as various
from shadowloss.builtinstickfigures import stickfigures as builtinstickfigures
try:
    from qvikconfig import parse as config_parse
except ImportError:
    from shadowloss.external.qvikconfig import parse as config_parse

PLAYING = 1
WON = 2
LOST = 3

class ObjectContainer(various.Container):
    def get_current_part(self):
        return self.parts[self.current_part]

    def has_pos(self, test_pos):
        part = self.get_current_part()
        return self.pos - part.width / 2 <= test_pos <= self.pos + part.width / 2

class PartContainer(various.Container):
    pass

class SettingsContainer(various.Container):
    pass

class Level(object):
    def _extract_text_settings(self, sets):
        """
        Extracts settings from text settings in the shadowloss
        syntax
        """
        info = {}
        sets = [x.split('=') for x in sets.rstrip(']').split(';')]
        for x in sets:
            info[x[0]] = float(info[x[1]])

        return info

    def create_objects(self, lst, typ=None):
        """
        Create usable objects from a list of letters or numbers in
        shadowloss syntax.
        """
        objects = []
        for x in lst:
            contents = x.split('[')
            if len(contents) > 1:
                global_settings = self._extract_text_settings(contents[1])
            else:
                global_settings = {}

            subcontents = contents[0].split(':')
            parts = []
            for y in subcontents[1:]:
                contents = y.split('(')
                if len(contents) > 1:
                    local_settings = self._extract_text_settings(contents[1])
                else:
                    local_settings = {}

                t_get = lambda name, default: \
                    return local_settings[name] or \
                    global_settings[name] or default

                settings = SettingsContainer()
                settings.duration = t_get('dur', typ == 'letter' and
                                          self.defaults.letter_duration
                                          or self.defaults.number_duration)
                if typ == 'letter':
                    settings.speed_decrease = t_get(
                        'dec', self.defaults.speed_decrease)
                elif typ == 'number':
                    settings.speed_increase = t_get(
                        'inc', self.defaults.temp_speed_increase)

                string = contents[0]
                obj_height = typ == 'letter' and self.letter_height or self.number_height
                surf = self.parent.create_text(string, obj_height)

                info = PartContainer()
                if typ == 'letter':
                    info.letter = string
                    info.temp_text = ''
                elif typ == 'number':
                    info.number = int(string)
                info.settings = settings
                info.surface = surf
                info.width = surf.get_size()[0]
                info.font_height = obj_height

                parts.append(info)

            pos = subcontents[0]

            info = ObjectContainer()
            info.type = typ
            info.pos = pos
            info.parts = parts
            info.current_part = 0
            info.current_time = 0

            objects.append(info)

        return objects

    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

        data = config_parse(path)

        # Starting speed of stickfigure
        self.start_speed = float(data.get('start speed') or 1.0)

        # When the stickman reaches the stop speed without hitting the
        # wall, he (or, alternatively, the human player controlling
        # him/her), has won.
        self.stop_speed = float(data.get('stop speed') or 0.0)

        # Starting position of stickfigure
        self.start_pos = float(data.get('start position') or 0.0)

        # Length of level
        self.length = data['length']

        # Speed increase when pressing a wrong letter
        self.speed_increase = float(
            data.get('speed increase') or 0.5)

        # Speed increase per second
        self.speed_increase_per_second = float(
            data.get('speed increase per second') or 0.0)

        # Stickfigure to be used
        self.stickfigure = builtinstickfigures[
            data.get('stickfigure') or 'bob'].create(self.parent)

        # Font heights
        self.font_height = int(data.get('font height') or 75)
        self.letter_height = int(data.get('letter height') or font_height)
        self.number_height = int(data.get('number height') or font_height)
        
        # Default values
        self.defaults = various.Container()

        ## Temporary speed increase during number penalties
        self.defaults.temp_speed_increase = float(
            data.get('default temporary speed increase') or 1.0)

        ## Speed decrease when pressing a correct letter
        self.default_speed_decrease = float(
            data.get('default speed decrease') or 0.5)

        ## The speed at which subobjects change
        default_obj_dur = float(
            data.get('default object duration') or 0.5)
        self.defaults.letter_duration = int(
            float(data.get('default letter duration')
                  or default_obj_dur) * 1000)
        self.defaults.number_duration = int(
            float(data.get('default number duration')
                  or default_obj_dur) * 1000)

        # Objects
        self.base_letters = self.create_objects(data.get('letters'), 'letter')
        self.base_numbers = self.create_objects(data.get('numbers'), 'number')

        # Prepare
        self.start()

    def start(self):
        self.speed = self.start_speed
        self.pos = self.start_pos
        self.time = 0
        self.temp_speed_still = 0
        self.current_temp_speed_increase = 0
        self.orig_time = datetime.datetime.now()
        self.prev_time = self.orig_time
        
        for x in (self.base_letters, self.base_numbers):
            for y in x:
                y.current_time = 0
                for z in y.parts:
                    if z.type = 'letter':
                        z.temp_text = ''
        self.letters, self.numbers = self.base_letters[:], self.base_numbers[:]

        self.body_color = (255, 255, 255)
        self.parent.fill_borders(self.body_color)

        self.status = PLAYING

    def color_foreground(self):
        self.parent.fill_borders(self.body_color)
        for x in (self.letters, self.numbers):
            for y in x:
                for z in y.parts:
                    z.surface = self.parent.create_text(z.text, y.font_height, self.body_color)

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
        time_increase = ((now - self.orig_time) - (self.prev_time - self.orig_time)).microseconds / 1000
        self.time += time_increase * self.speed
        self.prev_time = now
        if self.time > 999:
            self.time %= 1000

        if self.current_temp_speed_wait > 0:
            self.current_temp_speed_wait -= time_increase / 1000.0
            if self.current_temp_speed_wait <= 0:
                self.speed -= self.current_temp_speed_increase
                self.current_temp_speed_increase = 0

        self.speed += self.speed_increase_per_second * time_increase / 1000.0
        self.pos += self.speed * (increase / 10.0)
        for x in self.letters:
            part = x.get_current_part()
            if x.has_pos(self.pos)
                test = part.string.lower()
                for y in letters:
                    if test.startswith(part.temp_text + y):
                        part.temp_text += y
                        if part.temp_text == test:
                            part.temp_text = ''
                            self.letters.remove(x)
                            self.speed -= part.settings.speed_decrease
                    else:
                        self.speed += self.speed_increase
                        part.temp_text = ''
                ok = True
                break

            x.current_time += time_increase
            if x.current_time >= part.settings.duration:
                x.current_time %= part.settings.duration
                part.temp_text = ''
                x.current_part = (x.current_part + 1) % len(x.parts)

        if not ok:
            for x in letters:
                self.speed += self.speed_increase

        for x in self.numbers:
            part = x.get_current_part()
            if x.has_pos(self.pos):
                self.numbers.remove(x)
                self.current_temp_speed_wait += part.number
                this_speed_increase = part.settings.speed_increase
                self.current_temp_speed_increase += this_speed_increase
                self.speed += this_speed_increase

        if self.speed <= self.stop_speed:
            self.win()

    def draw(self):
        # Draw objects
        for x in (self.letters, self.numbers):
            for y in x:
                self.parent.blit(y.get_current_part().surface,
                                 (x.pos - self.pos +
                                  self.parent.virtual_size[0] / 2, 0))

        # Draw stickfigure
        self.stickfigure.draw(self.time, self.speed, self.body_color)

        # Draw start and end wall
        self.parent.draw_wall(-1, self.parent.virtual_size[0] / 2 -
                               self.pos, self.body_color)
        self.parent.draw_wall(self.length - self.pos + self.parent.virtual_size[0] /
                              2, self.parent.virtual_size[0] + 1, self.body_color)
