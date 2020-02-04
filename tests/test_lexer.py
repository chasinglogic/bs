from bs.subst import Lexer, Token


def test_lexer_all_literals():
    s = "build systems are bs"
    lexer = Lexer(s)
    tokens = [token for token in lexer]
    assert tokens == [
        (Token.literal, "build"),
        (Token.literal, "systems"),
        (Token.literal, "are"),
        (Token.literal, "bs"),
    ]


def test_lexer_simple():
    s = "$CC $CCFLAGS -Werror"
    lexer = Lexer(s)
    tokens = [token for token in lexer]
    assert tokens == [
        (Token.variable, "CC"),
        (Token.variable, "CCFLAGS"),
        (Token.literal, "-Werror"),
    ]
