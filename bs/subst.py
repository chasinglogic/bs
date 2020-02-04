import enum
from typing import Union


class Result:
    def __init__(self, pre_subst, post_subst, variables):
        self.pre_subst = pre_subst
        self.post_subst = post_subst
        self.variables = variables

    def needs_rebuild(self, variables):
        return not self.variables == variables

    def vars(self):
        return self.variables.keys()


class Token(enum.Enum):
    variable = 0
    literal = 1


class Lexer:
    def __init__(self, s):
        self.length = len(s)
        self.data = s
        self.pos = 0
        self.read_pos = 0
        self.char = ""
        self._read_char()

    def __iter__(self):
        """Return self, for use with for loops."""
        return self

    def __next__(self):
        self._skip_whitespace()

        if self.char == "":
            raise StopIteration

        if self.char == "$":
            self._read_char()
            if self.char == "$":
                return (Token.literal, self._read_word())
            elif self.char == "{":
                self._read_char()
                varname = self._read(lambda x: x == "}")
                self._read_char()
                return (Token.variable, varname)
            else:
                return (Token.variable, self._read_word())

        return (Token.literal, self._read_word())

    def _skip_whitespace(self):
        while self.char.isspace():
            self._read_char()

    def _read_word(self):
        return self._read(lambda x: not x.isspace())

    def _read(self, valid):
        """
        Read characters in the lexer until valid returns False.

        Returns the full string which matched the valid function.
        """
        start = self.pos
        while valid(self.char) and self.pos < self.length:
            self._read_char()

        return self.data[start : self.pos]

    def _read_char(self):
        """Read a character from input advancing the cursor."""
        if self.read_pos >= len(self.data):
            self.char = ""
        else:
            self.char = self.data[self.read_pos]

        self.pos = self.read_pos
        self.read_pos += 1

    def _peek_char(self):
        """Return the next character."""
        if self.read_pos > self.length:
            return ""

        return self.data[self.read_pos]


def needs_further_subst(value):
    if isinstance(value, str) and "$" in value:
        return True

    if isinstance(value, Result):
        return True

    return False


def subst(env, s, for_command=False, recursive=False, targets=None, sources=None):
    if targets is not None or sources is not None:
        # Do a shallow copy for performance, we're only going to modify two top
        # level keys so we do not need to do a deep copy.
        env = env.copy()
        env["targets"] = targets
        env["sources"] = sources

        # Provide a convenient way to access target[0] for builders which only
        # support one output.
        if targets is not None:
            env["target"] = targets[0]

    if isinstance(s, Result):
        variables = {key: env.get(key) for key in s.vars()}

        if not s.needs_rebuild(variables):
            return s.post_subst

        s = s.pre_subst

    variables = {}
    lexer = Lexer(s)
    result = []

    for token, value in lexer:
        if token == Token.literal:
            result.append(value)
            continue

        expanded = env.get(value)
        if not expanded:
            continue

        if needs_further_subst(expanded):
            sub_results, sub_variables = subst(env, expanded, recursive=True)
            variables.update(sub_variables)
            result.extend(sub_results)
        elif isinstance(expanded, list):
            expansion_list = []
            for item in expanded:
                if needs_further_subst(item):
                    sub_results, sub_variables = subst(env, item, recursive=True)
                    variables.update(sub_variables)
                    expansion_list.extend(reversed(sub_results))
                else:
                    expansion_list.append(item)

            variables[value] = expansion_list
            result.extend(expansion_list)
        else:
            variables[value] = expanded
            result.append(expanded)

    env[s] = Result(pre_subst=s, post_subst=result, variables=variables)

    if recursive:
        return result, variables

    if not for_command:
        return " ".join(result)

    return result
