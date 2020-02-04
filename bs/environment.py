from copy import deepcopy

from bs.subst import subst


class Environment(dict):
    """A dict-like object that represents a build environment."""

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
