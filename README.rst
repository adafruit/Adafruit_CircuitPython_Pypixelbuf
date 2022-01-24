Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-pypixelbuf/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/pypixelbuf/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_Pypixelbuf/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_Pypixelbuf/actions
    :alt: Build Status

Pure python implementation of _pixelbuf for smaller boards.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-pypixelbuf/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-pypixelbuf

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-pypixelbuf

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-pypixelbuf

Usage Example
=============

This example tests that pypixelbuf works.

.. code-block:: python

    class TestBuf(adafruit_pypixelbuf.PixelBuf):
        called = False

        def show(self):
            self.called = True


    buffer = TestBuf(20, bytearray(20 * 3), "RGB", 1.0, auto_write=True)
    buffer[0] = (1, 2, 3)


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/pypixelbuf/en/latest/>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_Pypixelbuf/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
