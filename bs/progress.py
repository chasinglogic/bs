"""Classes for displaying various kinds of progress."""

from sys import stdout
from itertools import cycle


class Spinner:
    def __init__(self, stream=stdout):
        self.spinner = cycle(["-", "/", "|", "\\"])
        self.stream = stream

    def spin(self):
        self.stream.write(next(self.spinner))  # write the next character
        self.stream.flush()  # flush stdout buffer (actual character display)
        self.stream.write("\b")  # erase the last written char
