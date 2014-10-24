#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""color module

This is a junion color module.

"""

SYSTEM_COLORS = {
    0:  (  0,   0,   0),
    1:  (128,   0,   0),
    2:  (  0, 128,   0),
    3:  (128, 128,   0),
    4:  (  0,   0, 128),
    5:  (128,   0, 128),
    6:  (  0, 128, 128),
    7:  (192, 192, 192),
    8:  (128, 128, 128),
    9:  (255,   0,   0),
    10: (  0, 255,   0),
    11: (255, 255,   0),
    12: (  0,   0, 255),
    13: (255,   0, 255),
    14: (  0, 255, 255),
    15: (255, 255, 255),
    }

EXTENDED_COLORS = [
    0, 95, 135, 175, 215, 255
    ]

def ansi2rgb(ansi):
    """Convert ANSI escape code to RGB code.

    Parameters
    ----------
    ansi: int
        ANSI escape code

    Returns
    -------
    int
        Red color code
    int
        Green color code
    int
        Blue color code

    """
    if 0 <= ansi < 16:
        return SYSTEM_COLORS[ansi]
    elif 232 <= ansi < 256:
        v = 10*(ansi - 232) + 8
        return v, v, v
    else:
        v = ansi - 16
        r = EXTENDED_COLORS[v / 36]
        g = EXTENDED_COLORS[(v/6) % 6]
        b = EXTENDED_COLORS[v % 6]
        return r, g, b

def rgb2hex(r, g, b):
    """Convert RGB code to HEX code

    Parameters
    ----------
    r: int
        Red color code
    g: int
        Green color code
    b: int
        Blue color code

    Returns
    -------
    str
        HEX code (#xxxxxx)

    """
    hr = hex(r)[2]*2 if r < 16 else hex(r)[2:]
    hg = hex(g)[2]*2 if g < 16 else hex(g)[2:]
    hb = hex(b)[2]*2 if b < 16 else hex(b)[2:]
    return '#%s%s%s' % (hr, hg, hb)

def gray_scale(r, g, b):
    """Convert RGB code to gray scale code

    Parameters
    ----------
    r: int
        Red color code
    g: int
        Green color code
    b: int
        Blue color code

    Returns
    -------
    int
        gray scale code

    """
    return (2*r + 4*g + b) / 7

