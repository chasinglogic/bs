from bs.BS import BS
from bs.subst import subst


def test_subst_returns_unmodified():
    bs = BS(some="value")
    fixture = "this string needs no subst"
    result = subst(bs, fixture, for_command=True)
    assert result == fixture.split()

    result = subst(bs, "this string needs no subst")
    assert result == fixture


def test_subst_only_string_variables():
    bs = BS(foo="FOO", bar="BAR", baz="BAZ")
    result = subst(bs, "$foo $baz $bar", for_command=True)
    assert result == ["FOO", "BAZ", "BAR"]


def test_subst_mixed_string_and_list_variables():
    bs = BS(CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"])

    result = subst(bs, "$CC $CCFLAGS", for_command=True)
    assert result == ["gcc", "-gsplit-dwarf", "-Werror", "-Wall"]


def test_subst_self_referential():
    bs = BS(
        CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"], LINKFLAGS="$CCFLAGS"
    )

    result = subst(bs, "$CC $CCFLAGS $LINKFLAGS", for_command=True)
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
    bs = BS(CC="gcc", CCFLAGS=["-gsplit-dwarf", "-Werror", "-Wall"],)

    s = "$CC -o $target $CCFLAGS $LINKFLAGS $sources"
    result = subst(bs, s, targets=["foo"], sources=["foo.c"], for_command=True)
    assert result == [
        "gcc",
        "-o",
        "foo",
        "-gsplit-dwarf",
        "-Werror",
        "-Wall",
        "foo.c",
    ]


def test_subst_callable():
    def include_paths(bs):
        include_flags = [
            "-I{}".format(subst(bs, path, for_command=False))
            for path in bs.get("CPATH", [])
        ]
        return include_flags

    def recursive_callable(bs):
        return "$RECURSED"

    bs = BS(
        CC_COMMAND="$CC $_INCLUDES $CCFLAGS -o $target $sources $recursive_callable",
        _INCLUDES=include_paths,
        recursive_callable=recursive_callable,
        RECURSED=True,
        BUILD_DIR="build",
        CPATH=["$BUILD_DIR", "/usr/local/include"],
        CC="gcc",
    )

    result = subst(
        bs, "$CC_COMMAND", for_command=True, targets=["foo"], sources=["foo.c"]
    )
    assert result == [
        "gcc",
        "-Ibuild",
        "-I/usr/local/include",
        "-o",
        "foo",
        "foo.c",
        "True",
    ]


def test_subst_callable_cannot_mutate_build_state():
    def mutator(bs):
        bs["MUTATED"] = True

    bs = BS(MUTATOR=mutator)
    try:
        subst(bs, "$MUTATOR")
        assert False, "MUTATOR mutated the build state!"
    except TypeError:
        pass
