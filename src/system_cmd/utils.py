from typing import List, Optional, Union

from zuper_commons.fs import DirPath
from zuper_commons.text import joinlines


def cmd2args(s: Union[str, List[str]]) -> List[str]:
    """if s is a list, leave it like that; otherwise split()"""
    if isinstance(s, list):
        return s
    elif isinstance(s, str):
        return s.split()
    else:
        assert False


def wrap(header: str, s: str, N: int = 30) -> str:
    header = "  " + header + "  "
    l1 = "-" * N + header + "-" * N
    l2 = "-" * N + "-" * len(header) + "-" * N
    return l1 + "\n" + s + "\n" + l2


def result_format(
    cwd: Optional[DirPath],
    cmd: List[str],
    ret: int,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
) -> str:
    msg = "Command:\n\t{cmd}\n" "in directory:\n\t{cwd}\nfailed with error {ret}".format(
        cwd=cwd, cmd=cmd, ret=ret
    )
    if stdout is not None:
        msg += "\n" + wrap("stdout", stdout)
    if stderr is not None:
        msg += "\n" + wrap("stderr", stderr)
    return msg


def indent(s: str, prefix: str) -> str:
    lines = s.splitlines()
    lines = ["%s%s" % (prefix, line.rstrip()) for line in lines]
    return joinlines(lines)


def copyable_cmd(cmds: List[str]) -> str:
    """Returns the commands as a copyable string."""

    return " ".join(map(copyable, cmds))


def copyable(x: str) -> str:
    if (not " " in x) and (not '"' in x) and (not '"' in x):
        return x
    else:
        if '"' in x:
            return "'%s'" % x
        else:
            return '"%s"' % x
