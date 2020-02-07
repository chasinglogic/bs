from copy import deepcopy

from bs.subst import subst
from bs.defaults import DEFAULT_COMMAND_MAP, DEFAULT_BUILDERS


class BS:
    """A dict-like object that represents the (B)uild (S)tate."""

    def __init__(self, *args, **kwargs):
        self.variables = dict(*args, **kwargs)
        if self.get("COMMAND_MAP") is None:
            self["COMMAND_MAP"] = DEFAULT_COMMAND_MAP

        if self.get("BUILDERS") is None:
            self["BUILDERS"] = DEFAULT_BUILDERS

    def __setitem__(self, key, item):
        self.variables[key] = item

    def __getitem__(self, key):
        return self.variables[key]

    def __getattr__(self, key):
        known = getattr(self, key, None)
        if known is not None:
            return known

        builder = self["BUILDERS"].get(key, None)
        if builder is not None:
            return builder

        method = self.get(key, None)
        if method is not None and callable(method):
            return method

        raise AttributeError("'BS' has not such attribute '{}'".format(key))

    def __repr__(self):
        return repr(self.variables)

    def __len__(self):
        return len(self.variables)

    def __delitem__(self, key):
        del self.variables[key]

    def delete(self, key):
        """Delete key without throwing a keyerror for missing values."""
        try:
            del self[key]
        except KeyError:
            pass

    def clear(self):
        return self.variables.clear()

    def copy(self):
        return BS(self.variables.copy())

    def get(self, key, default=None):
        return self.variables.get(key, default)

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

    def immutable(self):
        return ImmutableBS(self)

    def is_mutable(self):
        return True


class ImmutableBS(BS):
    """Not even a shovel can change this (B)uild (S)state."""

    def __init__(self, bs):
        super().__setattr__("variables", bs.variables)

    def __setattr__(self, attr, val):
        raise TypeError("Cannot mutate ImmutableBS")

    def __delattr__(self, attr):
        raise TypeError("Cannot mutate ImmutableBS")

    def __setitem__(self, key, value):
        raise TypeError("Cannot mutate ImmutableBS")

    def __delitem__(self, key):
        raise TypeError("Cannot mutate ImmutableBS")

    def clear(self):
        raise TypeError("Cannot mutate ImmutableBS")

    def clone(self):
        return self

    def copy(self):
        return self

    def immutable(self, _targets, _sources):
        return self

    def is_mutable(self):
        return False
