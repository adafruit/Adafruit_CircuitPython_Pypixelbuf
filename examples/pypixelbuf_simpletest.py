import adafruit_pypixelbuf


class TestBuf(adafruit_pypixelbuf.PixelBuf):
    called = False

    @property
    def n(self):
        return len(self)

    def _transmit(self, buffer):  # pylint: disable=unused-argument
        self.called = True


buf = TestBuf(20, "RGB", 1.0, auto_write=True)
buf[0] = (1, 2, 3)

print(buf[0])
print(buf[0:2])
print(buf[0:2:2])
print(buf.called)
