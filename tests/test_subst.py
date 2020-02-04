from bs.environment import Environment
from bs.subst import subst


def test_subst_returns_unmodified():
    env = Environment(some="value")
    fixture = "this string needs no subst"
    result = subst(env, fixture, for_command=True)
    assert result == fixture.split()

    result = subst(env, "this string needs no subst")
    assert result == fixture


def test_subst_only_string_variables():
    env = Environment(foo="FOO", bar="BAR", baz="BAZ")
    result = subst(env, "$foo $baz $bar", for_command=True)
    assert result == ["FOO", "BAZ", "BAR"]


def test_subst_mixed_string_and_list_variables():
    env = Environment(CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"])

    result = subst(env, "$CC $CCFLAGS", for_command=True)
    assert result == ["gcc", "-gsplit-dwarf", "-Werror", "-Wall"]


def test_subst_self_referential():
    env = Environment(
        CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"], LINKFLAGS="$CCFLAGS"
    )

    result = subst(env, "$CC $CCFLAGS $LINKFLAGS", for_command=True)
    assert result == [
        "gcc",
        "-gsplit-dwarf",
        "-Werror",
        "-Wall",
        "-gsplit-dwarf",
        "-Werror",
        "-Wall",
    ]


def test_subst_generate_real_command():
    env = Environment(CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"],)

    s = "$CC -o $target $CCFLAGS $LINKFLAGS $sources"
    result = subst(env, s, targets=["foo"], sources=["foo.c"], for_command=True)
    assert result == [
        "gcc",
        "-o",
        "foo",
        "-gsplit-dwarf",
        "-Werror",
        "-Wall",
        "foo.c",
    ]
