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

##[ Name        ]## shadowloss.world
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Controls the major aspects of the game
##[ Start date  ]## 2010 September 13

import pygame
from pygame.locals import *
from shadowloss.settingsparser import SettingsParser
import shadowloss.various as various
import shadowloss.generalinformation as ginfo

config_file_translations = {
    'verbose': 'term_verbose',
    'color errors': 'term_color_errors',
    'fullscreen': 'use_fullscreen',
    'zoom': 'disp_zoom',
    'fakefullscreen': 'use_fakefullscreen',
    'size': 'disp_size',
    'border': 'use_border',
    'hwaccel': 'use_hwaccel',
    'doublebuf': 'use_doublebuf',
    'mute': 'mute'
}

class World(SettingsParser):
    virtual_size=(640, 480)

    def __init__(self, **options):
        SettingsParser.__init__(self, config_file_translations, **options)
        self.set_if_nil('error_function', various.usable_error)
        self.set_if_nil('term_verbose', True)
        self.set_if_nil('term_color_errors', True)
        self.set_if_nil('use_fullscreen', False)
        self.set_if_nil('disp_zoom', 1)
        self.set_if_nil('use_fakefullscreen', False)
        self.set_if_nil('disp_size', None)
        self.set_if_nil('use_border', True)
        self.set_if_nil('use_hwaccel', True)
        self.set_if_nil('use_doublebuf', True)
        self.set_if_nil('mute', False)

        self.levels = options.get('levels') or []
        if self.levels:
            self.set_current_level(0)
        else:
            self.set_current_level(None)

        if self.disp_size is not None:
            try:
                spl = self.disp_size.split('x')
                self.disp_size = []
                for i in range(2):
                    if spl[i] == '':
                        self.disp_size.append(None)
                    else:
                        self.disp_size.append(int(spl[i]))
                if len(self.disp_size) < 2:
                    raise Exception()
            except Exception:
                self.error('size syntax is wrong, use [WIDTH]x[HEIGHT], quitting', True)

    def error(self, msg, done=None):
        if self.term_verbose:
            self.error_function(msg, done, color=self.term_color_errors)

    def status(self, msg):
        print ginfo.program_name + ': ' + msg

    def set_current_level(self, num):
        if num is None:
            self.current_level = None
        else:
            self.current_level = self.levels[num]
        self.current_level_index = num

    def start(self):
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.pre_init(44100) # Sound files must be resampled
        pygame.mixer.init()          # to 44.1 kHz

        self.create_screen()

        pygame.display.set_caption(ginfo.program_name)

        self.clock = pygame.time.Clock()
        self.run()

    def end(self):
        pass

    def normalize_point(self, p, rect):
        x = ((self.virtual_size[0] - rect[0]) / 2 + p[0]) * self.disp_zoom
        y = (self.virtual_size[1] - p[1]) * self.disp_zoom
        return int(x), int(y)
 
    def draw_line(self, p1, p2, body_rect):
        p1 = self.normalize_point(p1, body_rect)
        p2 = self.normalize_point(p2, body_rect)
        pygame.draw.line(self.screen, (255, 255, 255), p1, p2, 3)

    def draw_circle(self, pos, radius, body_rect):
        pos = self.normalize_point(pos, body_rect)
        pygame.draw.circle(self.screen, (255, 255, 255), pos,
                           int(radius * self.disp_zoom))

    def create_screen(self):
        # The screen is by default just a window of the same
        # dimensions as the virtual screen. This can be changed to
        # fullscreen (still with the same dimensions) or to different
        # dimensions, eventually with bars if the height ratio differs
        # from the width ratio.
        flags = 0
        barsize = None
        self.screen_bars = [None, None]
        self.screen_offset = [0, 0] # Might get changed if bars need
                                    # to be added
        if self.use_fullscreen:
            flags = FULLSCREEN
            if self.use_hwaccel:
                flags = flags | HWSURFACE
            if self.use_doublebuf:
                flags = flags | DOUBLEBUF
            self.real_size = self.virtual_size
        elif self.use_fakefullscreen or self.disp_size is not None:
            # Get dimensions (screen size if use_fakefullscreen,
            # user-specified size otherwise)
            if self.use_fakefullscreen or (self.disp_size is not None and
                                           self.disp_size[0] is None and
                                           self.disp_size[1] is None):
                try:
                    info = pygame.display.Info()
                    screen_size = info.current_w, info.current_h
                    if screen_size[0] == -1: # in this case, size[1] will also be -1
                        self.error('your SDL is too old for width and height detection', True)
                except Exception:
                    self.error('your PyGame is too old for width and height detection', True)
            else:
                screen_size = list(self.disp_size)
            if screen_size[0] is None:
                self.disp_zoom = screen_size[1] / float(self.virtual_size[1])
                screen_size[0] = int(self.virtual_size[0] * self.disp_zoom)
            elif screen_size[1] is None:
                self.disp_zoom = screen_size[0] / float(self.virtual_size[0])
                screen_size[1] = int(self.virtual_size[1] * self.disp_zoom)
            else:
                # The given width and height might not match the ratio
                # of the virtual width and height. Fix this by adding
                # bars. Sometimes bars should be on the x axis,
                # sometimes on the y axis. This is what a and b stands
                # for.
                scales = [screen_size[i] / float(self.virtual_size[i]) for i in range(2)]
                if scales[0] < scales[1]: a = 0; b = 1
                else:                     a = 1; b = 0

                self.disp_zoom = scales[a]
                self.screen_offset[b] = int((screen_size[b] - self.virtual_size[b] * self.disp_zoom) / 2)
                barsize = [0, 0]
                barsize[a] = screen_size[a]
                barsize[b] = self.screen_offset[b]
            self.real_size = screen_size
            self.status('Modified size of game is: %dx%d' % tuple(self.real_size))
            if not self.use_border or self.use_fakefullscreen:
                flags = NOFRAME
            if self.use_doublebuf:
                if flags is not 0:
                    flags = flags | DOUBLEBUF
                else:
                    flags = DOUBLEBUF
        else:
            # Check if a zoom level has been given
            if self.disp_zoom != 1:
                self.real_size = [int(x * self.disp_zoom) for x in self.virtual_size]
                self.status('Scaled size of game is: %dx%d' % tuple(self.real_size))
            else:
                self.real_size = self.virtual_size
            if not self.use_border or self.use_fakefullscreen:
                flags = NOFRAME
            if self.use_doublebuf:
                if flags is not 0:
                    flags = flags | DOUBLEBUF
                else:
                    flags = DOUBLEBUF

        # Finally create the screen
        self.screen = pygame.display.set_mode(self.real_size, flags)
        if barsize is not None:
            self.screen_bars[b] = pygame.Surface(barsize).convert()

        # Create the background surface
        self.bgsurface = pygame.Surface(self.real_size).convert()
        self.bgsurface.fill((0, 255, 0))

    def run(self):
        while True:
            self.draw()
            self.clock.tick(30)
            
    def draw(self):
        self.screen.blit(self.bgsurface, (0, 0))

        if self.screen_bars[0] is not None:
            self.screen.blit(self.screen_bars[0], (0, 0))
            self.screen.blit(self.screen_bars[0],
                             (self.real_size[0] -
                              self.screen_bars[0].get_size()[0], 0))
        if self.screen_bars[1] is not None:
            self.screen.blit(self.screen_bars[1], (0, 0))
            self.screen.blit(self.screen_bars[1],
                             (0, self.real_size[1] -
                              self.screen_bars[1].get_size()[1]))

        pygame.display.flip()
