#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Addrlib
# Copyright © 2018 AboodXD

# Addrlib
# A Python/Cython Address Library for Wii U textures.

try:
    import pyximport
    pyximport.install(language_level=3)

    from . import addrlib_cy as addrlib  # type: ignore

except:
    from . import addrlib

# Define the functions that can be used
getDefaultGX2TileMode = addrlib.getDefaultGX2TileMode
deswizzle = addrlib.deswizzle
swizzle = addrlib.swizzle
surfaceGetBitsPerPixel = addrlib.surfaceGetBitsPerPixel
getSurfaceInfo = addrlib.getSurfaceInfo
