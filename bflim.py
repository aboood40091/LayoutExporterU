# I made this when I was fed up with
# converting BFLIM to TGA manually
# and I wanted to get something working asap
# so, yeah, not the cleanest code ever

import os
from PIL import Image
import struct

import addrlib
import bcn

try:
    import pyximport
    pyximport.install()

    import gx2FormConv_cy as formConv

except ImportError:
    import gx2FormConv as formConv


BCn_formats = [0x31, 0x431, 0x32, 0x432, 0x33, 0x433, 0x34, 0x35]


class FLIMData:
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


def computeSwizzleTileMode(z):
    if isinstance(z, int):
        z = bin(z)[2:].zfill(8)

        tileMode = int(z[3:], 2)

        if tileMode in [1, 2, 3, 16]:
            s = 0

        else:
            s = 0xd0000

        s |= int(z[:3], 2) << 8

        return s, tileMode

    if isinstance(z, tuple):
        z = bin(z[0])[2:].zfill(3) + bin(z[1])[2:].zfill(5)
        return int(z, 2)


def readFLIM(f):
    flim = FLIMData()

    pos = len(f) - 0x28

    if f[pos + 4:pos + 6] == b'\xFF\xFE':
        bom = '<'

    elif f[pos + 4:pos + 6] == b'\xFE\xFF':
        bom = '>'

    header = FLIMHeader(bom)
    header.data(f, pos)

    if header.magic != b'FLIM':
        raise ValueError("Invalid file header!")

    pos += header.size

    info = imagHeader(bom)
    info.data(f, pos)

    if info.magic != b'imag':
        raise ValueError("Invalid imag header!")

    flim.width = info.width
    flim.height = info.height

    if info.format_ == 0x00:
        flim.format = 0x01
        flim.compSel = [0, 0, 0, 5]

    elif info.format_ == 0x01:
        flim.format = 0x01
        flim.compSel = [5, 5, 5, 0]

    elif info.format_ == 0x02:
        flim.format = 0x02
        flim.compSel = [0, 0, 0, 1]

    elif info.format_ == 0x03:
        flim.format = 0x07
        flim.compSel = [0, 0, 0, 1]

    elif info.format_ in [0x05, 0x19]:
        flim.format = 0x08
        flim.compSel = [2, 1, 0, 5]

    elif info.format_ == 0x06:
        flim.format = 0x1a
        flim.compSel = [0, 1, 2, 5]

    elif info.format_ == 0x07:
        flim.format = 0x0a
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x08:
        flim.format = 0x0b
        flim.compSel = [2, 1, 0, 3]

    elif info.format_ == 0x09:
        flim.format = 0x1a
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0C:
        flim.format = 0x31
        flim.format_ = "BC1"
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0D:
        flim.format = 0x32
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0E:
        flim.format = 0x33
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x0F:
        flim.format = 0x34
        flim.compSel = [0, 0, 0, 5]

    elif info.format_ == 0x10:
        flim.format = 0x34
        flim.compSel = [5, 5, 5, 0]

    elif info.format_ == 0x11:
        flim.format = 0x35
        flim.compSel = [0, 0, 0, 1]

    elif info.format_ == 0x14:
        flim.format = 0x41a
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x15:
        flim.format = 0x431
        flim.format_ = "BC1"
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x16:
        flim.format = 0x432
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x17:
        flim.format = 0x433
        flim.compSel = [0, 1, 2, 3]

    elif info.format_ == 0x18:
        flim.format = 0x19
        flim.compSel = [0, 1, 2, 3]

    else:
        raise NotImplementedError("Unsupported texture format: " + hex(info.format_))

    flim.imageSize = info.imageSize

    # Calculate swizzle and tileMode
    flim.swizzle, flim.tileMode = computeSwizzleTileMode(info.swizzle_tileMode)

    flim.alignment = info.alignment

    surfOut = addrlib.getSurfaceInfo(flim.format, flim.width, flim.height, 1, 1, flim.tileMode, 0, 0)

    if surfOut.depth != 1:
        raise NotImplementedError("Unsupported depth!")

    flim.pitch = surfOut.pitch

    flim.data = f[:info.imageSize]

    flim.surfOut = surfOut

    return flim


def get_deswizzled_data(flim):
    result = addrlib.deswizzle(flim.width, flim.height, flim.surfOut.height, flim.format, flim.surfOut.tileMode,
                               flim.swizzle, flim.pitch, flim.surfOut.bpp, flim.data)

    if flim.format in BCn_formats:
        size = ((flim.width + 3) >> 2) * ((flim.height + 3) >> 2) * (addrlib.surfaceGetBitsPerPixel(flim.format) >> 3)

    else:
        size = flim.width * flim.height * (addrlib.surfaceGetBitsPerPixel(flim.format) >> 3)

    return result[:size]


def toTGA(inb, name, texPath):
    tex = readFLIM(inb)
    result = [get_deswizzled_data(tex)]

    if tex.format == 0x1:
        data = result[0]

        format_ = 'l8'
        bpp = 1

    elif tex.format == 0x2:
        data = result[0]

        format_ = 'la4'
        bpp = 1

    elif tex.format == 0x7:
        data = result[0]

        format_ = 'la8'
        bpp = 2

    elif tex.format == 0x8:
        data = result[0]

        format_ = 'rgb565'
        bpp = 2

    elif tex.format == 0xa:
        data = result[0]

        format_ = 'rgb5a1'
        bpp = 2

    elif tex.format == 0xb:
        data = result[0]

        format_ = 'rgba4'
        bpp = 2

    elif tex.format == 0x19:
        data = result[0]

        format_ = 'bgr10a2'
        bpp = 4

    elif (tex.format & 0x3F) == 0x1a:
        data = result[0]

        format_ = 'rgba8'
        bpp = 4

    elif (tex.format & 0x3F) == 0x31:
        data = bcn.decompressDXT1(result[0], tex.width, tex.height)

        format_ = 'rgba8'
        bpp = 4

    elif (tex.format & 0x3F) == 0x32:
        data = bcn.decompressDXT3(result[0], tex.width, tex.height)

        format_ = 'rgba8'
        bpp = 4

    elif (tex.format & 0x3F) == 0x33:
        data = bcn.decompressDXT5(result[0], tex.width, tex.height)

        format_ = 'rgba8'
        bpp = 4

    elif (tex.format & 0x3F) == 0x34:
        data = bcn.decompressBC4(result[0], tex.width, tex.height, tex.format >> 8)

        format_ = 'rgba8'
        bpp = 4

    else:
        data = bcn.decompressBC5(result[0], tex.width, tex.height, tex.format >> 8)

        format_ = 'rgba8'
        bpp = 4

    data = formConv.torgba8(tex.width, tex.height, bytearray(data), format_, bpp, tex.compSel)
    img = Image.frombuffer("RGBA", (tex.width, tex.height), data, 'raw', "RGBA", 0, 1)
    img.save(os.path.join(texPath, "%s.tga" % name))
