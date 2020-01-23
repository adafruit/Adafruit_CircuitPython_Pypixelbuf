# The MIT License (MIT)
#
# Based on the Adafruit NeoPixel and Adafruit Dotstar CircuitPython drivers.
# Copyright (c) 2019-2020 Roy Hooper
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
`adafruit_pypixelbuf` - A pure python implementation of _pixelbuf
=================================================================
This class is used when _pixelbuf is not available in CircuitPython.  It is based on the work
in neopixel.py and adafruit_dotstar.py.

* Author(s): Damien P. George &  Limor Fried & Scott Shawcroft & Roy Hooper
"""

DOTSTAR_LED_START_FULL_BRIGHT = 0xFF
DOTSTAR_LED_START = 0b11100000  # Three "1" bits, followed by 5 brightness bits
DOTSTAR_LED_BRIGHTNESS = 0b00011111


class PixelBuf:  # pylint: disable=too-many-instance-attributes
    """
    A sequence of RGB/RGBW pixels.

    This is the pure python implementation of CircuitPython's _pixelbuf.

    :param int n: Number of pixels
    :param str byteorder: Byte order string constant (also sets bpp)
    :param float brightness: Brightness (0 to 1.0, default 1.0)
    :param bool auto_write: Whether to automatically write pixels (Default False)
    :param bytes header: Sequence of bytes to always send before pixel values.
    :param bytes trailer: Sequence of bytes to always send after pixel values.
    """
    def __init__(self, n, buf=None, *, byteorder="BGR", brightness=1.0, auto_write=False,
                 rawbuf=None, header=b"", trailer=b""):

        # Ignore buf and rawbuf. They are there for backwards compatibility with NeoPixel 4.1.0.
        buf = None
        rawbuf = None

        bpp, byteorder_tuple, has_white, dotstar_mode = self.parse_byteorder(byteorder)

        effective_bpp = 4 if dotstar_mode else bpp
        _bytes = effective_bpp * n

        self._pre_brightness_buffer = None
        self._transmit_buffer = bytearray(_bytes + len(header) + len(trailer))
        start = 0
        end = len(self._transmit_buffer)
        if header:
            self._transmit_buffer[0:len(header)] = header
            start = len(header)
        if trailer:
            self._transmit_buffer[-len(trailer):] = trailer
            end = -len(trailer)
        # Use a memoryview to only manipulate the color bits in the overall buffer.
        self._post_brightness_buffer = memoryview(self._transmit_buffer)[start:end]

        self._pixels = n
        self._bytes = _bytes
        self._byteorder = byteorder_tuple
        self._byteorder_string = byteorder
        self._has_white = has_white
        self._bpp = bpp
        self._dotstar_mode = dotstar_mode
        self._pixel_step = effective_bpp


        if dotstar_mode:
            self._byteorder_tuple = (byteorder_tuple[0] + 1, byteorder_tuple[1] + 1,
                                     byteorder_tuple[2] + 1, 0)

        # Set auto_write to False so that we don't try to update pixels with the brightness
        # assignment.
        self.auto_write = False
        self._brightness = 1.0
        # Set brightness through the property so that it can allocate _pre_brightness_buffer
        self.brightness = brightness
        self.auto_write = auto_write

        if dotstar_mode:
            for i in range(0, self._pixels * 4, 4):
                self._post_brightness_buffer[i] = DOTSTAR_LED_START_FULL_BRIGHT

    @property
    def buf(self):
        """The brightness adjusted pixel buffer data including the header and trailer."""

        # TODO: Remove this property once subclasses implement _transmit instead.
        return self._transmit_buffer

    @staticmethod
    def parse_byteorder(byteorder):
        """
        Parse a Byteorder string for validity and determine bpp, byte order, and
        dostar brightness bits.

        Byteorder strings may contain the following characters:
            R - Red
            G - Green
            B - Blue
            W - White
            P - PWM (PWM Duty cycle for pixel - dotstars 0 - 1.0)

        :param: ~str bpp: bpp string.
        :return: ~tuple: bpp, byteorder, has_white, dotstar_mode
        """
        bpp = len(byteorder)
        dotstar_mode = False
        has_white = False

        if byteorder.strip("RGBWP") != "":
            raise ValueError("Invalid Byteorder string")

        try:
            r = byteorder.index("R")
            g = byteorder.index("G")
            b = byteorder.index("B")
        except ValueError:
            raise ValueError("Invalid Byteorder string")
        if 'W' in byteorder:
            w = byteorder.index("W")
            byteorder = (r, g, b, w)
        elif 'P' in byteorder:
            lum = byteorder.index("P")
            byteorder = (r, g, b, lum)
            dotstar_mode = True
        else:
            byteorder = (r, g, b)

        return bpp, byteorder, has_white, dotstar_mode

    @property
    def bpp(self):
        """
        The number of bytes per pixel in the buffer (read-only).
        """
        return self._bpp

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
    def brightness(self, new_brightness):
        self._brightness = min(max(new_brightness, 0.0), 1.0)

        # Allocate a second buffer for unadjusted pixel values if needed.
        if self._pre_brightness_buffer is None and new_brightness < 1.0:
            self._pre_brightness_buffer = bytearray(self._post_brightness_buffer)

        # We don't deallocate if brightness is set back to 1.0 because it is likely we'll need it
        # again for a brightness < 1.0.

        for i in range(0, self._bytes):
            if self._dotstar_mode:
                self._post_brightness_buffer[i] = int(self._pre_brightness_buffer[i] * new_brightness)

        if self.auto_write:
            self.show()

    @property
    def byteorder(self):
        """
        ByteOrder string for the buffer (read-only)
        """
        return self._byteorder_string

    def __len__(self):
        """
        Number of pixels.
        """
        return self._pixels

    def _transmit(self, buffer):
        """
        Transmits the full buffer out to the pixels.
        """
        raise NotImplementedError("Must be subclassed")

    def show(self):
        """
        Transmit the color values out to the pixels so that they are shown.
        """
        self._transmit(self._transmit_buffer)

    def _set_item(self, index, value):  # pylint: disable=too-many-locals,too-many-branches
        if index < 0:
            index += len(self)
        if index >= self._pixels or index < 0:
            raise IndexError
        offset = (index * self.bpp)
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
            if self.bpp == 4 and self._has_white and r == g and g == b:
                w = r
                r = 0
                g = 0
                b = 0
            elif self._dotstar_mode:
                w = 1.0
        elif len(value) == self.bpp:
            if self.bpp == 3:
                r, g, b = value
            else:
                r, g, b, w = value
                has_w = True
        elif len(value) == 3 and self._dotstar_mode:
            r, g, b = value

        if self._pre_brightness_buffer is not None:
            self._pre_brightness_buffer[offset + self._byteorder[0]] = r
            self._pre_brightness_buffer[offset + self._byteorder[1]] = g
            self._pre_brightness_buffer[offset + self._byteorder[2]] = b
            self._post_brightness_buffer[offset + self._byteorder[0]] = int(r * self._brightness)
            self._post_brightness_buffer[offset + self._byteorder[1]] = int(g * self._brightness)
            self._post_brightness_buffer[offset + self._byteorder[2]] = int(b * self._brightness)
        else:
            self._post_brightness_buffer[offset + self._byteorder[0]] = r
            self._post_brightness_buffer[offset + self._byteorder[1]] = g
            self._post_brightness_buffer[offset + self._byteorder[2]] = b


        if has_w:
            white_offset = offset + self._byteorder[3]
            if self._dotstar_mode:
                # LED startframe is three "1" bits, followed by 5 brightness bits
                # then 8 bits for each of R, G, and B. The order of those 3 are configurable and
                # vary based on hardware
                # same as math.ceil(brightness * 31) & 0b00011111
                # Idea from https://www.codeproject.com/Tips/700780/Fast-floor-ceiling-functions
                self._post_brightness_buffer[offset + self._byteorder[3]] = (
                    32 - int(32 - w * 31) & 0b00011111) | DOTSTAR_LED_START
            else:
                if self._pre_brightness_buffer is not None:
                    self._pre_brightness_buffer[white_offset] = w
                    self._post_brightness_buffer[white_offset] = int(w * self._brightness)
                else:
                    self._post_brightness_buffer[white_offset] = w
        elif self._dotstar_mode:
            self._post_brightness_buffer[offset + self._byteorder[3]] = DOTSTAR_LED_START_FULL_BRIGHT

    def __setitem__(self, index, val):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._pixels)
            for val_i, in_i in enumerate(range(start, stop, step)):
                self._set_item(in_i, val[val_i])
        else:
            self._set_item(index, val)

        if self.auto_write:
            self.show()

    def _getitem(self, index):
        start = index * self.bpp
        color_data = self._post_brightness_buffer
        if self._pre_brightness_buffer is not None:
            color_data = self._pre_brightness_buffer
        value = [
            color_data[start + self._byteorder[0]],
            color_data[start + self._byteorder[1]],
            color_data[start + self._byteorder[2]],
        ]
        if self._has_white:
            value.append(color_data[start + self._byteorder[2]])
        elif self._dotstar_mode:
            value.append((color_data[start + self._byteorder[3]] & DOTSTAR_LED_BRIGHTNESS) /
                         31.0)
        return value

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

    def fill(self, color):
        """
        Fill the PixelBuf with a single color.
        :param color: Color to set.
        """
        auto_write = self.auto_write
        self.auto_write = False
        for i, _ in enumerate(self):
            self[i] = color
        if auto_write:
            self.show()
        self.auto_write = auto_write


def wheel(pos):
    """
    Helper to create a colorwheel.

    :param pos: int 0-255 of color value to return
    :return: tuple of RGB values
    """
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return 0, 0, 0
    if pos < 85:
        return 255 - pos * 3, pos * 3, 0
    if pos < 170:
        pos -= 85
        return 0, 255 - pos * 3, pos * 3
    pos -= 170
    return pos * 3, 0, 255 - pos * 3

# TODO: Remove this once all libraries use the instance `fill` method.
def fill(pixelbuf, color):
    """
    Helper to fill the strip a specific color.
    :param pixelbuf: A pixel object.
    :param color: Color to set.
    """
    auto_write = pixelbuf.auto_write
    pixelbuf.auto_write = False
    for i, _ in enumerate(pixelbuf):
        pixelbuf[i] = color
    if auto_write:
        pixelbuf.show()
    pixelbuf.auto_write = auto_write
