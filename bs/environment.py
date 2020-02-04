from copy import deepcopy

from bs.subst import subst
from bs.defaults import DEFAULT_COMMAND_MAP


class Environment:
    """A dict-like object that represents a build environment."""

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            self.variables = args
        else:
            self.variables = kwargs

        if self.get("COMMAND_MAP") is None:
            self["COMMAND_MAP"] = DEFAULT_COMMAND_MAP

    def __setitem__(self, key, item):
        self.variables[key] = item

    def __getitem__(self, key):
        return self.variables[key]

    def __repr__(self):
        return repr(self.variables)

    def __len__(self):
        return len(self.variables)

    def __delitem__(self, key):
        del self.variables[key]

    def clear(self):
        return self.variables.clear()

    def copy(self):
        return Environment(self.variables.copy())

    @property
    def command_map(self):
        return self["COMMAND_MAP"]

    def clone(self):
        return deepcopy(self)

    def append_unique(self, **kwargs):
        """
        For key=value in kwargs append / combine the values as appropriate if
        the value is not already present in self[key]
        """
        for key, value in kwargs.items():
            result = self.get(key)
            if result is None:
                self[key] = value
                continue

            if isinstance(result, list):
                if isinstance(value, list):
                    result.extend([v for v in value if v not in result])
                elif value not in result:
                    result.append(value)
            elif value not in result:
                result += value

            self[key] = result

    def subst_command(self, s):
        return subst(self, s, for_command=True)

    def subst(self, s):
        return subst(self, s, for_command=False)
