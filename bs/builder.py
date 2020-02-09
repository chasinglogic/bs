from typing import List

from bs.node import Node
from bs.errors import UserError


class Builder:
    def __init__(self, bs, targets, sources, **overrides):
        self.bs = bs
        self.targets = targets
        self.sources = sources
        self.overrides = overrides

    def __call__(self, bs, targets, sources, **overrides):
        self.__init__(bs, targets, sources, **overrides)
        return self

    def get_command(self):
        raise NotImplementedError
