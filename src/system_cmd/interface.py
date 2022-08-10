from __future__ import unicode_literals

from typing import List, Optional, Union

from zuper_commons.fs import DirPath
from .meat import system_cmd_result

__all__ = [
    "system_cmd",
    "system_cmd_show",
    "system_run",
]


def system_cmd_show(cwd: Optional[DirPath], cmd: Union[str, List[str]]) -> None:
    """Display command, raise exception."""
    system_cmd_result(cwd, cmd, display_stdout=True, display_stderr=True, raise_on_error=True)


def system_cmd(cwd: Optional[DirPath], cmd: Union[str, List[str]]) -> int:
    """Do not output; return value."""
    res = system_cmd_result(cwd, cmd, display_stdout=False, display_stderr=False, raise_on_error=False)
    return res.ret


def system_run(cwd: Optional[DirPath], cmd: Union[str, List[str]]) -> str:
    """Gets the stdout of a command,  raise exception if it failes"""
    res = system_cmd_result(cwd, cmd, display_stdout=False, display_stderr=False, raise_on_error=True)
    return res.stdout
