import pypixelbuf

callback_called = False


def callback():  # pylint: disable=global-statement
    global callback_called
    callback_called = True


buffer = pypixelbuf.PixelBuf(20, bytearray(20 * 3), pypixelbuf.RGB, 1.0, auto_write=True,
                             write_function=callback)

buffer[0] = (1, 2, 3)

print(callback_called)
