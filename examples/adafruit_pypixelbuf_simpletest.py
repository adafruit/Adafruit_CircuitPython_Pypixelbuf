import adafruit_pypixelbuf


class TestBuf(adafruit_pypixelbuf.PixelBuf):
    called = False

    def _transmit(self, buffer):
        print(buffer)
        self.called = True


test_buffer = TestBuf(20, byteorder="RGB", brightness=1.0, auto_write=True)
test_buffer[0] = (1, 2, 3)

print(test_buffer[0])
print(test_buffer[0:2])
print(test_buffer[0:2:2])
print(test_buffer.called)
