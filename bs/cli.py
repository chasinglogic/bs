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

from docopt import docopt


def main():
    arguments = docopt(__doc__, version="bs 1.0")
    print(arguments)


# Support python -m bs operation
if __name__ == "__main__":
    main()
