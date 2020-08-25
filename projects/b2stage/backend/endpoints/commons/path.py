"""
TODO: apply the / magic of pathlib
src: http://j.mp/2nwz908
"""

import os
from contextlib import contextmanager
from pathlib import Path, PurePath

from restapi.utilities.logs import log

COMPRESSION_FORMAT = "zip"


def root():
    return os.path.abspath(os.sep)


def current_dir():
    return os.getcwd()


@contextmanager
def cd(newdir):
    """
    https://stackoverflow.com/a/24176022
    """
    prevdir = current_dir()
    os.chdir(os.path.expanduser(str(newdir)))
    try:
        yield
    finally:
        os.chdir(prevdir)


def build(path=None):

    # no path would just mean the FS root directory
    if path is None:
        path = root()

    if not isinstance(path, list):
        if isinstance(path, str) or isinstance(path, Path):
            path = [path]
        else:
            path = list(path)

    p = Path(*path)
    return p


def join(*paths, return_str=False):
    path = build(paths)
    if return_str:
        path = str(path)
    return path


def home(relative_path=None):
    if relative_path is None:
        return Path.home()
    else:
        if relative_path.startswith(os.sep):
            log.exit("Requested abspath '{}' in relative context", relative_path)
        return build("~" + os.sep + relative_path).expanduser()


def current():
    return Path.cwd()


def create(pathobj, directory=False, force=False, parents=False):
    if directory:
        # pathobj.mkdir(exist_ok=force)  # does not work with Python 3.4...
        try:
            pathobj.mkdir(parents=parents)
        except FileExistsError:
            if force:
                pass
            else:
                log.exit("Cannot overwrite existing: {}", pathobj)
    else:
        raise NotImplementedError("Yet to do!")


def file_exists_and_nonzero(pathobj, accept_link=False):

    if pathobj.exists():
        iostats = pathobj.stat()
        return not iostats.st_size == 0
    else:
        if accept_link:
            if os.path.islink(pathobj):
                return True
        return False


def parts(my_path):
    return PurePath(my_path).parts


def last_part(my_path):
    return os.path.basename(my_path)


def dir_name(my_path):
    return os.path.dirname(my_path)


def append_compress_extension(base_name):
    return f"{base_name}.{COMPRESSION_FORMAT}"


def compress(dir_path, zip_file_path):
    # backward compatibility with python 3.5
    dir_path = str(dir_path)
    import shutil

    base_name = str(zip_file_path).replace("." + COMPRESSION_FORMAT, "")
    shutil.make_archive(
        base_name=base_name, format=COMPRESSION_FORMAT, root_dir=dir_path
    )
