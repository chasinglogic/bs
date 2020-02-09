from bs.util import get_suffix


class Node:
    """Node is a target or source file in the graph."""

    def __init__(self, filename, children=None):
        if children is None:
            children = []

        self.filename = filename
        self.children = children

    def get_suffix(self):
        return get_suffix(self.filename)
