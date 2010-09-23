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
        """Get current part of this object"""
        return self.parts[self.current_part]

    def has_pos(self, test_pos):
        """Check if a position is inside this object"""
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
        sets = [x.split('=') for x in sets.rstrip(')]').split(';')]
        for x in sets:
            info[x[0]] = float(x[1])

        return info

    def create_objects(self, lst, typ=None):
        """
        Create usable objects from a list of letters or numbers in
        shadowloss syntax.
        """
        objects = []

        obj_height = typ == 'letter' and self.letter_height \
                or self.number_height
        
        for x in lst:
            # Split the entry into its parts and its global settings
            contents = x.split('[')
            if len(contents) > 1:
                global_settings = self._extract_text_settings(contents[1])
            else:
                global_settings = {}

            # Parse the parts
            subcontents = contents[0].split(':')
            parts = []
            for y in subcontents[1:]:
                contents = y.split('(')
                if len(contents) > 1:
                    local_settings = self._extract_text_settings(contents[1])
                else:
                    local_settings = {}

                # Use a hierarchy for settings:
                # Local settings OR global settings OR default settings
                t_get = lambda name, default: \
                    local_settings.get(name) or \
                    global_settings.get(name) or default

                settings = SettingsContainer()
                settings.duration = int(
                    t_get('dur', typ == 'letter' and
                          self.defaults.letter_duration
                          or self.defaults.number_duration) * 1000)

                if typ == 'letter':
                    settings.speed_decrease = t_get(
                        'dec', self.defaults.speed_decrease)
                elif typ == 'number':
                    settings.speed_increase = t_get(
                        'inc', self.defaults.temp_speed_increase)

                string = contents[0]
                surf = self.parent.create_text(string, obj_height)

                # Save the information
                info = PartContainer()
                info.string = string
                if typ == 'letter':
                    info.letter = string
                    info.temp_text = ''
                elif typ == 'number':
                    info.number = float(string)
                info.settings = settings
                info.surface = surf
                info.width = surf.get_size()[0]

                parts.append(info)

            # Basic info
            pos = float(subcontents[0])

            info = ObjectContainer()
            info.type = typ
            info.pos = pos
            info.parts = parts
            info.current_part = 0
            info.current_time = None
            info.font_height = obj_height
            
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
        font_height = data.get('font height')
        self.letter_height = int(data.get('letter height') or
                                 font_height or 75)
        self.number_height = int(data.get('number height') or
                                 font_height or 40)
        
        # Default values
        self.defaults = various.Container()

        ## Temporary speed increase during number penalties
        self.defaults.temp_speed_increase = float(
            data.get('default temporary speed increase') or 1.0)

        ## Speed decrease when pressing a correct letter
        self.defaults.speed_decrease = float(
            data.get('default speed decrease') or 0.5)

        ## The speed at which subobjects change
        default_obj_dur = float(
            data.get('default object duration') or 0.5)
        self.defaults.letter_duration = float(
            data.get('default letter duration')
            or default_obj_dur)
        self.defaults.number_duration = float(
            data.get('default number duration')
            or default_obj_dur)

        # Objects
        self.base_letters = self.create_objects(data.get('letters'), 'letter')
        self.base_numbers = self.create_objects(data.get('numbers'), 'number')

        # Prepare
        self.start()

    def start(self):
        """(Re)start the level"""
        now = datetime.datetime.now()

        self.speed = self.start_speed
        self.pos = self.start_pos
        self.time = 0
        self.temp_speed_still = 0
        self.current_temp_speed_increase = 0
        self.current_temp_speed_duration = 0
        self.current_temp_speed_time = None

        self.orig_time = now
        self.prev_time = now

        # Reset certain values
        for x in (self.base_letters, self.base_numbers):
            for y in x:
                y.current_time = now
                for z in y.parts:
                    if y.type == 'letter':
                        z.temp_text = ''
        self.letters, self.numbers = self.base_letters[:], self.base_numbers[:]

        self.body_color = (255, 255, 255)
        self.parent.fill_borders(self.body_color)

        self.status = PLAYING

    def color_foreground(self):
        """Colors all elements in one color (self.body_color)"""
        self.parent.fill_borders(self.body_color)
        for x in (self.letters, self.numbers):
            for y in x:
                for z in y.parts:
                    z.surface = self.parent.create_text(z.string, y.font_height, self.body_color)

    def lose(self):
        self.status = LOST
        self.body_color = (255, 0, 0)
        self.color_foreground()

    def win(self):
        self.status = WON
        self.body_color = (0, 255, 0)
        self.color_foreground()

    def update(self, letters=[]):
        """Update the level"""
        if self.status != PLAYING:
            # You have either won or lost.
            return

        # Time
        now = datetime.datetime.now()
        time_increase = (now - self.prev_time).microseconds / 1000.0
        self.time += time_increase * self.speed
        self.prev_time = now
        if self.time > 999:
            self.time %= 1000

        # Movement
        self.speed += self.speed_increase_per_second * time_increase / 1000.0
        self.pos += self.speed * (time_increase / 10.0)

        # Check for end of any current continous penalty speed increase
        if self.current_temp_speed_time is not None:
            if (now - self.current_temp_speed_time).microseconds \
                    / 1000.0 > self.current_temp_speed_duration:
                self.speed -= self.current_temp_speed_increase
                self.current_temp_speed_increase = 0
                self.current_temp_speed_duration = 0
                self.current_temp_speed_time = None

        # Letter detection
        ok = False
        for x in self.letters:
            part = x.get_current_part()
            if x.has_pos(self.pos):
                test = part.letter.lower()
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

        # Speed increases when pressing keys in empty areas
        if not ok:
            for x in letters:
                self.speed += self.speed_increase

        # Number detection
        for x in self.numbers:
            part = x.get_current_part()
            if x.has_pos(self.pos):
                self.numbers.remove(x)
                self.current_temp_speed_time = now
                self.current_temp_speed_duration += part.number * 1000
                this_speed_increase = part.settings.speed_increase
                self.current_temp_speed_increase += this_speed_increase
                self.speed += this_speed_increase

        # See if objects with more than one part needs changing into
        # the next parts
        for x in (self.letters, self.numbers):
            for y in x:
                if len(y.parts) == 1:
                    continue
                current_duration = (now - y.current_time).microseconds / 1000.0
                part = y.get_current_part()
                if current_duration >= part.settings.duration:
                    y.current_time = now
                    y.current_part = (y.current_part + 1) % len(y.parts)
                    if y.type == 'letter':
                        part.temp_text = ''

        # Win if you have reached the given stop speed
        if self.speed <= self.stop_speed:
            self.win()
        # ..or lose if you have crashed into the wall.
        elif self.pos >= self.length:
            self.lose()

    def draw(self):
        # Draw objects
        for x in (self.letters, self.numbers):
            for y in x:
                self.parent.blit(y.get_current_part().surface,
                                 (y.pos - self.pos +
                                  self.parent.virtual_size[0] / 2, 0))

        # Draw stickfigure
        self.stickfigure.draw(self.time, self.speed, self.body_color)

        # Draw start and end wall
        self.parent.draw_wall(-1, self.parent.virtual_size[0] / 2 -
                               self.pos, self.body_color)
        self.parent.draw_wall(self.length - self.pos + self.parent.virtual_size[0] /
                              2, self.parent.virtual_size[0] + 1, self.body_color)
