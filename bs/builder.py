from .node import Node


class Builder:
    def get_command(self, targets: List[Node], sources: List[Node]):
        raise NotImplementedError


class Command(Builder):
    def __init__(self, targets: List[Node], sources, cmdstr):
        self.cmdstr = cmdstr
        self.targets = targets
        self.sources = sources
