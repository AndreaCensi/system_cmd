import os

__all__ = [
    "find_executable",
]


def find_executable(program: str) -> str | None:
    """Checks if a program exists. Returns None otherwise"""

    fpath, _fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def is_exe(fpath: str) -> bool:
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
