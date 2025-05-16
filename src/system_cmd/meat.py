import os
import subprocess
import sys
import tempfile
from typing import IO
from typing import Any

from zuper_commons.fs import DirPath

from . import logger
from .structures import CmdException
from .structures import CmdResult
from .utils import cmd2args
from .utils import copyable_cmd
from .utils import indent

__all__ = [
    "system_cmd_result",
]


def system_cmd_result(
    cwd: DirPath | None,
    cmd: str | list[str],
    display_stdout: bool = False,
    display_stderr: bool = False,
    raise_on_error: bool = False,
    display_prefix: str | None = None,  # leave it there
    write_stdin: bytes = b"",
    capture_keyboard_interrupt: bool = False,
    display_stream: Any = sys.stdout,
    env: dict[str, str] | None = None,
) -> CmdResult:
    """
    Returns the structure CmdResult; raises CmdException.
    Also OSError are captured.
    KeyboardInterrupt is passed through unless specified

    write_stdin: A string to write to the process.
    """

    if env is None:
        env = os.environ.copy()

    tmp_stdout = tempfile.TemporaryFile()
    tmp_stderr = tempfile.TemporaryFile()
    cmd1 = cmd2args(cmd)

    # ret = None
    rets = None
    # interrupted = False

    #     if (display_stdout and captured_stdout) or (display_stderr and captured_stderr):

    try:
        # stdout = None if display_stdout else
        stdout = tmp_stdout.fileno()
        # stderr = None if display_stderr else
        stderr = tmp_stderr.fileno()

        assert isinstance(cmd1, list)
        if display_stdout or display_stderr:
            logger.info("$ %s" % copyable_cmd(cmd1))
        p = subprocess.Popen(cmd1, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, bufsize=0, cwd=cwd, env=env)
        #         set_term_function(p)
        stdin = p.stdin
        assert stdin is not None
        if write_stdin:
            stdin.write(write_stdin)
            stdin.flush()

        stdin.close()
        p.wait()
        ret = p.returncode
        rets = None
        interrupted = False

    except KeyboardInterrupt:
        logger.debug("Keyboard interrupt for:\n %s" % " ".join(cmd1))
        if capture_keyboard_interrupt:
            ret = 100
            interrupted = True
        else:
            raise
    except OSError as e:
        interrupted = False
        ret = 200
        rets = str(e)

    # remember to go back
    def read_all(f: IO[bytes]) -> bytes:
        os.lseek(f.fileno(), 0, 0)
        return f.read().strip()

    captured_stdout_b: bytes = read_all(tmp_stdout).strip()
    captured_stderr_b: bytes = read_all(tmp_stderr).strip()

    s = ""

    # captured_stdout = remove_empty_lines(captured_stdout)
    # captured_stderr = remove_empty_lines(captured_stderr)

    def decode_one(x: bytes) -> str:
        try:
            return x.decode("utf-8")
        except UnicodeDecodeError as e2:
            msg = "Cannot decode the output of the command %s" % cmd1
            msg += "\nStream is not valid UTF-8: %s" % e2
            msg += "\nI will read the rest ignoring the errors."
            logger.error(msg)
            return x.decode("utf-8", errors="ignore")

    captured_stdout = decode_one(captured_stdout_b)
    captured_stderr = decode_one(captured_stderr_b)

    if display_stdout and captured_stdout:
        s += indent(captured_stdout, "stdout>") + "\n"

    if display_stderr and captured_stderr:
        s += indent(captured_stderr, "stderr>") + "\n"

    if s:
        logger.debug(s)

    res = CmdResult(cwd, cmd1, ret, rets, interrupted, stdout=captured_stdout, stderr=captured_stderr)

    if raise_on_error:
        if res.ret != 0:
            raise CmdException(res)

    return res


def remove_empty_lines(s: bytes) -> bytes:
    lines = s.split(b"\n")
    lines = [l for l in lines if not is_empty(l)]
    return b"\n".join(lines)


def is_empty(line: bytes) -> bool:
    return len(line.strip()) == 0
