# I made this when I was fed up with
# converting BFLIM to TGA manually
# and I wanted to get something working asap
# so, yeah, not the cleanest code ever

from typing import Any
from PIL import Image
import struct
import os

import addrlib
import bcn

try:
    import pyximport
    pyximport.install()

    import gx2FormConv_cy as formConv  # type: ignore

except ImportError:
    import gx2FormConv as formConv


class FLIMData:
    width: int
    height: int
    format: int
    format_: str
    compSel: list[int]
    imageSize: int
    swizzle: int
    tileMode: int
    alignment: Any
    pitch: Any
    surfOut: object
    data: Any
    pass


class FLIMHeader(struct.Struct):
    def __init__(self, bom):
        super().__init__(bom + '4s2H2IH2x')

    def data(self, data, pos):
        (self.magic,
         self.endian,
         self.size_,
         self.version,
         self.fileSize,
         self.numBlocks) = self.unpack_from(data, pos)


class imagHeader(struct.Struct):
    def __init__(self, bom):
        super().__init__(bom + '4sI3H2BI')

    def data(self, data, pos):
        (self.magic,
         self.infoSize,
         self.width,
         self.height,
         self.alignment,
         self.format_,
         self.swizzle_tileMode,
         self.imageSize) = self.unpack_from(data, pos)


def computeSwizzleTileMode(tileModeAndSwizzlePattern):
    if isinstance(tileModeAndSwizzlePattern, int):
        tileMode = tileModeAndSwizzlePattern & 0x1F
        swizzlePattern = ((tileModeAndSwizzlePattern >> 5) & 7) << 8
        if tileMode not in [1, 2, 3, 16]:
            swizzlePattern |= 0xd0000

        return swizzlePattern, tileMode

    return tileModeAndSwizzlePattern[0] << 5 | tileModeAndSwizzlePattern[1]  # swizzlePattern << 5 | tileMode


def readFLIM(f):
    flim = FLIMData()

    pos = len(f) - 0x28

    if f[pos + 4:pos + 6] == b'\xFF\xFE':
        bom = '<'

    elif f[pos + 4:pos + 6] == b'\xFE\xFF':
        bom = '>'

    header = FLIMHeader(bom)  # type: ignore
    header.data(f, pos)

    if header.magic != b'FLIM':
        raise ValueError("Invalid file header!")

    pos += header.size

    info = imagHeader(bom)  # type: ignore
    info.data(f, pos)

    if info.magic != b'imag':
        raise ValueError("Invalid imag header!")

    flim.width = info.width
    flim.height = info.height

    if info.format_ == 0x00:  # ^c
        flim.format = 0x01
        flim.compSel = [0, 0, 0, 5]

    elif info.format_ == 0x01:  # ^d
        flim.format = 0x01
        flim.compSel = [5, 5, 5, 0]

    elif info.format_ == 0x02:  # ^e
        flim.format = 0x02
        flim.compSel = [0, 0, 0, 1]

    elif info.format_ == 0x03:  # ^f
        flim.format = 0x07
        flim.compSel = [0, 0, 0, 1]

    elif info.format_ == 0x04:  # ^g
        flim.format = 0x07
        flim.compSel = [0, 1, 4, 5]

    elif info.format_ == 0x05:  # ^h
        flim.format = 0x08
        flim.compSel = [2, 1, 0, 5]

    #elif info.format_ == 0x06:  # unsupported by NW4F, ^i
    #    flim.format = 0x1a
    #    flim.compSel = [0, 1, 2, 5]

    elif info.format_ == 0x07:  # ^j
        flim.format = 0x0a
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x08:  # ^k
        flim.format = 0x0b
        flim.compSel = [3, 2, 1, 0]

    elif info.format_ == 0x09:  # ^l
        flim.format = 0x1a
        flim.compSel = [0, 1, 2, 3]

    #elif info.format_ == 0x0a:  # unsupported by NW4F, ^m
    #    flim.format = 0x31
    #    flim.format_ = "ETC1"
    #    flim.compSel = [0, 1, 2, 5]

    #elif info.format_ == 0x0b:  # unsupported by NW4F, ^n
    #    flim.format = 0x33
    #    flim.format_ = "ETC1A4"
    #    flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0c:  # ^o
        flim.format = 0x31
        flim.format_ = "BC1"
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0d:  # ^p
        flim.format = 0x32
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0e:  # ^q
        flim.format = 0x33
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0f:  # ^r, +r
        flim.format = 0x34
        flim.compSel = [0, 0, 0, 5]

    elif info.format_ == 0x10:  # ^s
        flim.format = 0x34
        flim.compSel = [5, 5, 5, 0]

    elif info.format_ == 0x11:  # ^t
        flim.format = 0x35
        flim.compSel = [0, 0, 0, 1]

    #elif info.format_ == 0x12:  # unsupported by NW4F, ^a
    #    flim.format = 0x34
    #    flim.compSel = [0, 0, 0, 5]

    #elif info.format_ == 0x13:  # unsupported by NW4F, ^b
    #    flim.format = 0x34
    #    flim.compSel = [4, 4, 4, 0]

    elif info.format_ == 0x14:  # ^l
        flim.format = 0x41a
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x15:  # ^o
        flim.format = 0x431
        flim.format_ = "BC1"
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x16:  # ^p
        flim.format = 0x432
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x17:  # ^q
        flim.format = 0x433
        flim.compSel = [0, 1, 2, 3]

    #elif info.format_ == 0x18:  # unsupported by NW4F LayoutEditor
    #    flim.format = 0x19
    #    flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x19:  # ^u
        flim.format = 0x08
        flim.compSel = [0, 2, 5, 1]

    else:
        raise NotImplementedError("Unsupported texture format: " + hex(info.format_))

    flim.imageSize = info.imageSize

    # Calculate swizzle and tileMode
    flim.swizzle, flim.tileMode = computeSwizzleTileMode(info.swizzle_tileMode)
    if not 1 <= flim.tileMode <= 16:
        raise ValueError("Invalid tileMode!")

    flim.alignment = info.alignment

    surfOut = addrlib.getSurfaceInfo(flim.format, flim.width, flim.height, 1, 1, flim.tileMode, 0, 0)

    tilingDepth = surfOut.depth
    if surfOut.tileMode == 3:
        tilingDepth //= 4

    if tilingDepth != 1:
        raise NotImplementedError("Unsupported depth!")

    flim.pitch = surfOut.pitch

    flim.data = f[:info.imageSize]

    flim.surfOut = surfOut

    return flim


def get_deswizzled_data(flim):
    result = addrlib.deswizzle(flim.width, flim.height, 1, flim.format, 0, 1, flim.surfOut.tileMode,
                               flim.swizzle, flim.pitch, flim.surfOut.bpp, 0, 0, flim.data)

    if (flim.format & 0x3F) in (0x31, 0x32, 0x33, 0x34, 0x35):
        size = ((flim.width + 3) >> 2) * ((flim.height + 3) >> 2) * (addrlib.surfaceGetBitsPerPixel(flim.format) >> 3)

    else:
        size = flim.width * flim.height * (addrlib.surfaceGetBitsPerPixel(flim.format) >> 3)

    return result[:size]


# Supported formats
formats = {
    0x1: ('l8', 1),
    0x2: ('la4', 1),
    0x7: ('la8', 2),
    0x8: ('rgb565', 2),
    0xa: ('rgb5a1', 2),
    0xb: ('rgba4', 2),
    0x19: ('bgr10a2', 4),
    0x1a: ('rgba8', 4),
    0x31: ('rgba8', 4),
    0x32: ('rgba8', 4),
    0x33: ('rgba8', 4),
    0x34: ('rgba8', 4),
    0x35:  ('rgba8', 4),
}

def texureToRGBA8(width, height, format_, data, compSel):
    formatStr, bpp = formats[format_ & 0x3F]

    ### Decompress the data if compressed ###

    if (format_ & 0x3F) == 0x31:
        data = bcn.decompressDXT1(data, width, height)

    elif (format_ & 0x3F) == 0x32:
        data = bcn.decompressDXT3(data, width, height)

    elif (format_ & 0x3F) == 0x33:
        data = bcn.decompressDXT5(data, width, height)

    elif (format_ & 0x3F) == 0x34:
        data = bcn.decompressBC4(data, width, height, format_ >> 8)

    elif (format_ & 0x3F) == 0x35:
        data = bcn.decompressBC5(data, width, height, format_ >> 8)

    return formConv.torgba8(width, height, bytearray(data), formatStr, bpp, compSel)


def toTGA(inb: bytes, name: str, texPath: str):
    tex = readFLIM(inb)
    data = texureToRGBA8(tex.width, tex.height, tex.format, get_deswizzled_data(tex), tex.compSel)
    img = Image.frombuffer("RGBA", (tex.width, tex.height), data, 'raw', "RGBA", 0, 1)
    img.save(os.path.join(texPath, "%s.tga" % name))
