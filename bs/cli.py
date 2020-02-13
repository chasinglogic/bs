"""
(b)uild (s)ystem

Usage:
  bs [options] [<targets>]...

Options:
  -h --help  Show this screen.
  --version  Show version.
  --verbose  Increase verbosity.

  --task=(clean | configure | compiledb)  Run the specified task instead of compiling
"""


import itertools
import sys

from docopt import docopt
from os import getcwd, walk
from os.path import join

from bs.BS import BS
from bs.loader import Loader
from bs.progress import Spinner


def main():
    arguments = docopt(__doc__, version="bs 1.0")
    global_bs = BS()
    script_loader = Loader(bs)

    spinner = Spinner()
    print("Loading build defintions...")

    # TODO efficiently skip .git dir
    for root, dirs, files in os.walk(getcwd()):
        if ".git" in dirs:
            dirs.remove(".git")

        bs = None
        try:
            build_yml_idx = files.index("build.yml")
            bs = script_loader.load_yaml(os.path.join(root, files[build_yml_idx]))
        except KeyError:
            continue

        try:
            build_py_idx = files.index("build.py")
            scripted_bs = script_loader.load_python(
                os.path.join(root, files[build_py_idx])
            )
            if scripted_bs is not None:
                bs.update(scripted_bs)
        except KeyError:
            pass

        global_bs.add(bs)
        spinner.spin()


# Support python -m bs operation
if __name__ == "__main__":
    main()
