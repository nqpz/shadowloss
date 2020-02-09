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

##[ Name        ]## shadowloss.cairogame
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Adds a Cairo backend for drawing shapes that
                  # PyGame has difficulties drawing
##[ Start date  ]## 2010 September 15

import cairo
import math

SURFACE = None

def set_screen(pygame_surf):
    global SURFACE
    SURFACE = pygame_surf

def get_cairo_ctx(surf):
    width, height = surf.get_size()
    surf = cairo.ImageSurface.create_for_data(
        surf.get_buffer(), cairo.FORMAT_ARGB32,
        width, height, width * 4)
    return cairo.Context(surf)

def draw_line(color, start_pos, end_pos, line_width, surf=None):
    ctx = get_cairo_ctx(surf or SURFACE)
    ctx.set_source_rgb(*color)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(*start_pos)
    ctx.line_to(*end_pos)
    ctx.stroke()
    del ctx

def draw_circle(color, pos, radius, line_width=0, surf=None):
    ctx = get_cairo_ctx(surf or SURFACE)
    if line_width > 0:
        ctx.set_line_width(line_width)

    ctx.set_source_rgb(*color)
    ctx.arc(pos[0], pos[1], radius, 0, 2 * math.pi)
    if line_width > 0:
        ctx.stroke()
    else:
        ctx.fill()
    del ctx

def finish_draw(surf=None):
    pass
