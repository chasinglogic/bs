from os.path import splitext


def get_suffix(filename):
    return splitext(filename)[1]
