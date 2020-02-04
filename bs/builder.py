from typing import List

from bs.node import Node
from bs.errors import UserError


class Builder:
    def __init__(self, env, targets, sources, **overrides):
        self.env = env
        self.targets = targets
        self.sources = sources
        self.overrides = overrides

    def get_command(self):
        raise NotImplementedError


class Program(Builder):
    """Builds programs based on the file extension of sources."""

    def get_command(self):
        if not self.sources:
            return []

        extension = get_file_extension(self.sources[0])
        try:
            return self.env.command_map[extension]
        except KeyError:
            raise UserError(
                "Unknown file extension for Program builder: {} for target {}".format(
                    extension, self.targets
                )
            )
