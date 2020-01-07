import adafruit_pypixelbuf


class TestBuf(adafruit_pypixelbuf.PixelBuf):
    called = False

    def show(self):
        self.called = True


buffer = TestBuf(20, bytearray(20 * 3), "RGB", 1.0, auto_write=True)
buffer[0] = (1, 2, 3)

print(buffer[0])
print(buffer[0:2])
print(buffer[0:2:2])
print(buffer.called)
