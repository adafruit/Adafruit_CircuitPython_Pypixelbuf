# The MIT License (MIT)
#
# Based on the Adafruit NeoPixel and Adafruit Dotstar Circuitpython drivers.
# Copyright (c) 2019 Roy Hooper
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`pypixelbuf` - A pure python implementation of pixelbuf
=======================================================
This class is used when `pixelbuf` is not available in a build.

This is a work in progress.

* Author(s): Damien P. George &  Limor Fried & Scott Shawcroft & Roy Hooper
"""
import math

class ByteOrder(object):
    has_white = False
    has_luminosity = False
    bpp = 3
    byteorder = (0, 1, 2)


class RGB(ByteOrder):
    byteorder = (0, 1, 2)


class RBG(ByteOrder):
    byteorder = (0, 2, 1)


class GRB(ByteOrder):
    byteorder = (1, 0, 2)


class GBR(ByteOrder):
    byteorder = (1, 2, 0)


class BRG(ByteOrder):
    byteorder = (2, 0, 1)


class BGR(ByteOrder):
    byteorder = (2, 1, 0)


class RGBW(ByteOrder):
    byteorder = (0, 1, 2, 3)
    bpp = 4
    has_white = True


class RBGW(ByteOrder):
    byteorder = (0, 2, 1, 3)
    bpp = 4
    has_white = True


class GRBW(ByteOrder):
    byteorder = (1, 0, 2, 3)
    bpp = 4
    has_white = True


class GBRW(ByteOrder):
    byteorder = (1, 2, 0, 3)
    bpp = 4
    has_white = True


class BRGW(ByteOrder):
    byteorder = (2, 0, 1, 3)
    bpp = 4
    has_white = True


class BGRW(ByteOrder):
    byteorder = (2, 1, 0, 3)
    bpp = 4
    has_white = True


class LRGB(ByteOrder):
    byteorder = (1, 2, 3, 0)
    bpp = 4
    has_luminosity = True


class LRBG(ByteOrder):
    byteorder = (1, 3, 2, 0)
    bpp = 4
    has_luminosity = True


class LGRB(ByteOrder):
    byteorder = (2, 1, 3, 0)
    bpp = 4
    has_luminosity = True


class LGBR(ByteOrder):
    byteorder = (2, 3, 1, 0)
    bpp = 4
    has_luminosity = True


class LBRG(ByteOrder):
    byteorder = (3, 1, 2, 0)
    bpp = 4
    has_luminosity = True


class LBGR(ByteOrder):
    byteorder = (3, 2, 1, 0)
    bpp = 4
    has_luminosity = True


DOTSTAR_LED_START_FULL_BRIGHT = 0xFF
DOTSTAR_LED_START = 0b11100000  # Three "1" bits, followed by 5 brightness bits
DOTSTAR_LED_BRIGHTNESS = 0b00011111

IS_PURE_PYTHON = True


class PixelBuf(object):
    """
    A sequence of RGB/RGBW/LRGB pixels.

    This is the purepython implementation of PixelBuf. 

    :param ~int size: Number of pixels
    :param ~bytearray buf: Bytearray to store pixel data in
    :param ~pixelbuf.ByteOrder byteorder: Byte order constant from `pixelbuf` (also sets the bpp)
    :param ~float brightness: Brightness (0 to 1.0, default 1.0)
    :param ~bytearray rawbuf: Bytearray to store raw pixel colors in
    :param ~int offset: Offset from start of buffer (default 0)
    :param ~bool dotstar: Dotstar mode (default False)
    :param ~bool auto_write: Whether to automatically write pixels (Default False)
    :param ~callable write_function: (optional) Callable to use to send pixels
    :param ~list write_args: (optional) Tuple or list of args to pass to ``write_function``.  The 
           PixelBuf instance is appended after these args.
    """
    def __init__(self, n, buf, byteorder=BGR, brightness=1.0, rawbuf=None, offset=0, dotstar=False,
                 auto_write=False, write_function=None, write_args=None):
        if not issubclass(byteorder, ByteOrder):
            raise TypeError("byteorder must be a subclass of ByteOrder, got %s" % (byteorder.__class__.__name__, ), )
        if not isinstance(buf, bytearray):
            raise TypeError("buf must be a bytearray")
        if rawbuf is not None and not isinstance(rawbuf, bytearray):
            raise TypeError("rawbuf must be a bytearray")
        if dotstar and not byteorder.has_luminosity:
            raise ValueError("Can not use dotstar with %s" % byteorder)

        effective_bpp = 4 if dotstar else byteorder.bpp
        _bytes = effective_bpp * n
        two_buffers = rawbuf is not None and buf is not None
        if two_buffers and len(buf) != len(rawbuf):
            raise ValueError("rawbuf is not the same size as buf")

        if (len(buf) + offset) < _bytes:
            raise TypeError("buf is too small")
        if two_buffers and (len(rawbuf) + offset) < _bytes:
            raise TypeError("buf is too small. need %d bytes" % (_bytes, ))

        self._pixels = n
        self._bytes = _bytes
        self._byteorder = byteorder
        self._bytearray = buf
        self._two_buffers = two_buffers
        self._rawbytearray = rawbuf
        self._offset = offset
        self._dotstar_mode = dotstar
        self._pixel_step = effective_bpp

        self.auto_write = auto_write

        if dotstar and not self._byteorder.has_luminosity:
            self._byteorder = byteorder.__class__()  # Make a copy
            self._byteorder.has_luminosity = True
            self._byteorder.byteorder = (
                self._byteorder.byteorder[0] + 1,
                self._byteorder.byteorder[1] + 1,
                self._byteorder.byteorder[2] + 1,
                0
            )
        
        self._write_function = write_function
        self._write_args = ()
        if write_args:
            self._write_args = tuple(self._write_args) + (self, )

        self._brightness = min(1.0, max(0, brightness))

        if dotstar:
            for i in range(0, self._pixels * 4, 4):
                self._bytearray[i + self._offset] = DOTSTAR_LED_START_FULL_BRIGHT

    @property
    def bpp(self):
        """
        The number of bytes per pixel in the buffer (read-only).
        """
        return self._byteorder.bpp

    @property
    def brightness(self):
        """
        Float value between 0 and 1.  Output brightness.
        If the PixelBuf was allocated with two both a buf and a rawbuf,
        setting this value causes a recomputation of the values in buf.
        If only a buf was provided, then the brightness only applies to
        future pixel changes.
        In DotStar mode 
        """      
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = min(max(value, 0.0), 1.0)

        # Adjust brightness when two buffers are available
        if self._two_buffers:
            offset_check = self._offset % self._pixel_step
            for i in range(self._offset, self._bytes + self._offset):
                if self._dotstar_mode and (i % 4 != offset_check):
                    self._bytearray[i] = int(self._rawbytearray[i] * self._brightness)

        if self.auto_write:
            self.show()

    @property
    def byteorder(self):
        """
        `ByteOrder` class for the buffer (read-only)
        """
        return self._byteorder


    def __len__(self):
        """
        Number of pixels.
        """
        return self._pixels


    def show(self):
        """
        Call the associated write function to display the pixels
        """
        if self._write_function:
            self._write_function(*self._write_args)

    def _set_item(self, index, value):
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError
        offset = self._offset + (index * self.bpp)
        r = 0
        g = 0
        b = 0
        w = 0
        has_w = False
        if isinstance(value, int):
            r = value >> 16
            g = (value >> 8) & 0xff
            b = value & 0xff
            w = 0
            # If all components are the same and we have a white pixel then use it
            # instead of the individual components.
            if self.bpp == 4 and self.byteorder.has_white and r == g and g == b:
                w = r
                r = 0
                g = 0
                b = 0
            elif self._byteorder.has_luminosity:
                w = 1.0
        elif len(value) == self.bpp:
            if self.bpp == 3:
                r, g, b = value
            else:
                r, g, b, w = value
                has_w = True
        elif len(value) == 3 and self._byteorder.has_luminosity:
            r, g, b = value
        
        if self._two_buffers:
            self._rawbytearray[offset + self.byteorder.byteorder[0]] = r
            self._rawbytearray[offset + self.byteorder.byteorder[1]] = g
            self._rawbytearray[offset + self.byteorder.byteorder[2]] = b

        self._bytearray[offset + self.byteorder.byteorder[0]] = int(r * self._brightness)
        self._bytearray[offset + self.byteorder.byteorder[1]] = int(g * self._brightness)
        self._bytearray[offset + self.byteorder.byteorder[2]] = int(b * self._brightness)
        if has_w:
            if self._dotstar_mode:
                # LED startframe is three "1" bits, followed by 5 brightness bits
                # then 8 bits for each of R, G, and B. The order of those 3 are configurable and
                # vary based on hardware
                # same as math.ceil(brightness * 31) & 0b00011111
                # Idea from https://www.codeproject.com/Tips/700780/Fast-floor-ceiling-functions
                self._bytearray[offset + self.byteorder.byteorder[3]] = (32 - int(32 - w * 31) & 0b00011111) | DOTSTAR_LED_START
            else:
                self._bytearray[offset + self.byteorder.byteorder[3]] = int(w * self._brightness)
            if self._two_buffers:
                self._rawbytearray[offset + self.byteorder.byteorder[3]] = self._bytearray[offset + self.byteorder.byteorder[3]]
        elif self._dotstar_mode:
            self._bytearray[offset + self.byteorder.byteorder[3]] = DOTSTAR_LED_START_FULL_BRIGHT
            
    def __setitem__(self, index, val):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._pixels)
            length = stop - start
            if step != 0:
                length = math.ceil(length / step)
            if len(val) != length:
                raise ValueError("Slice and input sequence size do not match.")
            for val_i, in_i in enumerate(range(start, stop, step)):
                self._set_item(in_i, val[val_i])
        else:
            self._set_item(index, val)

        if self.auto_write:
            self.show()

    def _getitem(self, index):
        if self.byteorder.has_white:
            return tuple(self._bytearray[self._offset + (index * self.bpp) + self._byteorder.byteorder[i]] for i in range(self.bpp))
        else:
            return tuple(
                [self._bytearray[self._offset + (index * self.bpp) + self._byteorder.byteorder[i]] for i in range(3)] + [
                (self._bytearray[self._offset + (index * self.bpp) + self._byteorder.byteorder[3]] & DOTSTAR_LED_BRIGHTNESS) / 31.0
            ])

    def __getitem__(self, index):
        if isinstance(index, slice):
            out = []
            for in_i in range(*index.indices(len(self._bytearray) // self.bpp)):
                out.append(self._getitem(in_i))
            return out
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError
        return self._getitem(index)

    def fill_wheel(self, n, step):
        """
        fill the buffer with a colorwheel starting at offset n, and stepping by step
        """
        self[0:len(self)] = [wheel((n + (step * i)) % 255) for i in range(len(self))]
        if self.auto_write:
            self.show()


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 