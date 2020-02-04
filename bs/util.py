from os.path import splitext


def get_file_extension(filename):
    return splitext(filename)[1]
