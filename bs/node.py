class Node:
    def __init__(self, name, children=None):
        if children is None:
            children = []

        self.name = name
        self.children = children
