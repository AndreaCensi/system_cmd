from __future__ import unicode_literals

from typing import List, Optional

from zuper_commons.fs import DirPath
from .utils import indent

__all__ = [
    "CmdException",
    "CmdResult",
]


class CmdResult:
    def __init__(
        self,
        cwd: Optional[DirPath],
        cmd: List[str],
        ret: int,
        rets: Optional[str],
        interrupted: bool,
        stdout: str,
        stderr: str,
    ):
        self.cwd = cwd
        self.cmd = cmd
        self.ret = ret
        self.rets = rets
        self.stdout = stdout
        self.stderr = stderr
        self.interrupted = interrupted

    def __str__(self) -> str:
        from .utils import copyable_cmd

        msg = "The command: %s\n" "     in dir: %s\n" % (copyable_cmd(self.cmd), self.cwd)

        if self.interrupted:
            msg += "Was interrupted by the user\n"
        else:
            msg += "returned: %s" % self.ret
        if self.rets is not None:
            msg += "\n" + indent(self.rets, "error>")
        if self.stdout:
            msg += "\n" + indent(self.stdout, "stdout>")
        if self.stderr:
            msg += "\n" + indent(self.stderr, "stderr>")
        return msg


class CmdException(Exception):
    res: CmdResult

    def __init__(self, cmd_result: CmdResult):
        Exception.__init__(self, str(cmd_result))
        self.res = cmd_result
