import enum
from typing import Union


class InvalidCallableValue(Exception):
    pass


class Result:
    def __init__(self, pre_subst, post_subst, variables):
        self.pre_subst = pre_subst
        self.post_subst = post_subst
        self.variables = variables

    def __repr__(self):
        return "Result('{}', '{}')".format(self.pre_subst, self.post_subst)

    def __str__(self):
        return str(self.post_subst)

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


def to_expansion_list(bs, expanded, variables, targets, sources):
    expansion_list = []
    for item in expanded:
        if needs_further_subst(item):
            sub_results, sub_variables = subst(bs, item, recursive=True)
            variables.update(sub_variables)
            expansion_list.extend(reversed(sub_results))
        else:
            expansion_list.append(str(item))

    return expansion_list


def subst(bs, s, for_command=False, recursive=False, targets=None, sources=None):
    if not recursive and bs.is_mutable():
        bs["targets"] = targets
        if targets:
            bs["target"] = targets[0]
        bs["sources"] = sources

    if isinstance(s, Result):
        variables = {key: bs.get(key) for key in s.vars()}

        if not s.needs_rebuild(variables):
            print("CACHED!")
            return s.post_subst

        s = s.pre_subst

    variables = {}
    lexer = Lexer(s)
    result = []

    for token, value in lexer:
        if token == Token.literal:
            print("LITERAL", token, value)
            result.append(value)
            continue

        expanded = bs.get(value, None)
        if expanded is None:
            continue

        if needs_further_subst(expanded):
            sub_results, sub_variables = subst(bs, expanded, recursive=True)
            variables.update(sub_variables)
            print("EXPANDED", expanded, "TO", sub_results)
            result.extend(sub_results)
        elif isinstance(expanded, list):
            expansion_list = to_expansion_list(
                bs, expanded, variables, targets, sources
            )
            variables[value] = expansion_list
            result.extend(expansion_list)
        elif callable(expanded):
            called_value = expanded(bs.immutable())
            if not called_value:
                continue

            if needs_further_subst(called_value):
                sub_results, sub_variables = subst(bs, called_value, recursive=True)
                variables.update(sub_variables)
                result.extend(sub_results)
            elif isinstance(called_value, str):
                result.append(str(called_value))
            elif isinstance(called_value, list):
                expansion_list = to_expansion_list(
                    bs, called_value, variables, targets, sources
                )
                variables[value] = expansion_list
                result.extend(expansion_list)
            else:
                raise InvalidCallableValue(
                    "Expansion function {} returned an invalid value: {}".format(
                        str(expanded), str(called_value)
                    )
                )

        else:
            variables[value] = expanded
            result.append(str(expanded))

    if s not in ["targets", "target", "sources"] and bs.is_mutable():
        bs[s] = Result(pre_subst=s, post_subst=result, variables=variables)

    if recursive:
        return result, variables

    if bs.is_mutable():
        bs.delete("targets")
        bs.delete("target")
        bs.delete("sources")

    if not for_command:
        return " ".join(result)

    return result
