from shutil import which
from sys import platform
from os import getenv

from bs.builder import Builder
from bs.errors import UserError
from bs.log import warning


class CC(Builder):
    """Implements a builder for C programs"""

    def get_command(self):
        return self.bs.subst_command(
            "${CC_COMMAND}", targets=self.targets, sources=self.sources,
        )


def platform_compiler():
    """Try to set a reasonable default for CC based on platform."""
    if platform == "win32":
        msvc = which("mvsc.exe")
        if msvc:
            return msvc

        clang = which("clang.exe")
        if clang:
            return mvsc

        raise UserError("Could not find clang or msvc compilers and no CC provided.")

    elif platform == "darwin":
        clang = which("clang")
        if clang:
            return clang

        raise UserError("Could not find clang and no CC provided.")

    gcc = which("gcc")
    if gcc:
        return gcc

    clang = which("clang")
    if clang:
        return clang

    raise UserError("Could not find gcc or clang compilers and no CC provided.")


def c_include_flags(bs):
    """Build the include flags for CC from CPATH."""
    # TODO: make the targets depend on these paths
    prefix = bs["_include_flag_prefix"]
    include_flags = [
        "{flag_prefix}{path}".format(flag_prefix=prefix, path=bs.subst(bs, path))
        for path in bs.get("CPATH", [])
    ]
    return include_flags


def setup(bs):
    bs["CC"] = getenv("CC", bs.get("CC", None))
    if bs["CC"] is None:
        try:
            bs["CC"] = platform_compiler()
        except UserError as e:
            warning("CC tool was asked for however was unable to load:", str(e))
            return False

    bs["CFLAGS"] = getenv("CFLAGS", "").split()
    bs["CCFLAGS"] = getenv("CCFLAGS", "").split()
    bs["CPATH"] = getenv("CPATH", "").split()
    bs["_c_includs"] = c_include_flags
    bs["_include_flag_prefix"] = "/I" if "msvc" in bs["CC"] else "-I"
    bs["CC_COMMAND"] = "$CC $CFLAGS $CCFLAGS $_c_includes -o $target $sources"
    return True
