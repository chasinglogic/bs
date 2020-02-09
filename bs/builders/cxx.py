from shutil import which
from sys import platform
from os import getenv

from bs.builder import Builder
from bs.errors import UserError
from bs.log import warning


class CXX(Builder):
    """Implements a builder for C programs"""

    def get_command(self):
        return self.bs.subst_command(
            "${CXX_COMMAND}", targets=self.targets, sources=self.sources,
        )


def platform_compiler():
    """Try to set a reasonable default for CXX based on platform."""
    if platform == "win32":
        msvc = which("mvsc.exe")
        if msvc:
            return msvc

        clang = which("clang++.exe")
        if clang:
            return mvsc

        raise UserError("Could not find clang++ or msvc compilers and no CXX provided.")

    elif platform == "darwin":
        clang = which("clang++")
        if clang:
            return clang

        raise UserError("Could not find clang++ and no CXX provided.")

    gcc = which("g++")
    if gcc:
        return gcc

    clang = which("clang++")
    if clang:
        return clang

    raise UserError("Could not find g++ or clang++ compilers and no CXX provided.")


def c_include_flags(bs):
    """Build the include flags for CXX from CPATH."""
    # TODO: make the targets depend on these paths
    prefix = bs["_include_flag_prefix"]
    include_flags = [
        "{flag_prefix}{path}".format(flag_prefix=prefix, path=bs.subst(bs, path))
        for path in bs.get("CPATH", [])
    ]
    return include_flags


def setup(bs):
    bs["CXX"] = getenv("CXX", None)
    if bs["CXX"] is None:
        try:
            bs["CXX"] = platform_compiler()
        except UserError as e:
            warning("CXX tool was asked for however was unable to load:", str(e))
            return False

    bs["CXXFLAGS"] = getenv("CXXFLAGS", "").split()
    bs["CCFLAGS"] = getenv("CCFLAGS", "").split()
    bs["CPATH"] = getenv("CPATH", "").split()
    bs["_c_includs"] = c_include_flags
    bs["_include_flag_prefix"] = "/I" if "msvc" in bs["CXX"] else "-I"
    bs["CXX_COMMAND"] = "$CXX $CCFLAGS $CXXFLAGS $_c_includes -o $target $sources"
    return True
