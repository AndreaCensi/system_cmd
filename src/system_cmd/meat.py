import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, IO, List, Optional, Union

from zuper_commons.fs import DirPath
from . import logger
from .structures import CmdException, CmdResult
from .utils import cmd2args, copyable_cmd, indent

__all__ = [
    "system_cmd_result",
]


# class Shared:
#     p = None


#
# def on_sigterm(a,b):
#     #print('SIGTERM caught --- terminating child process')
#     try:
#         Shared.p.terminate()
#     except OSError: # e.g. OSError: [Errno 3] No such process
#         pass
#     #os.kill(Shared.p.pid, signal.SIGKILL)
#
# def set_term_function(process):
#     Shared.p = process
#     signal.signal(signal.SIGTERM, on_sigterm)


# @contract(cwd='None|string', cmd='string|list(string)', env='dict|None')
def system_cmd_result(
    cwd: Optional[DirPath],
    cmd: Union[str, List[str]],
    display_stdout: bool = False,
    display_stderr: bool = False,
    raise_on_error: bool = False,
    display_prefix: Optional[str] = None,  # leave it there
    write_stdin: bytes = b"",
    capture_keyboard_interrupt: bool = False,
    display_stream: Any = sys.stdout,  # @UnusedVariable
    env: Optional[Dict[str, str]] = None,
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
        p = subprocess.Popen(
            cmd1, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, bufsize=0, cwd=cwd, env=env
        )
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
        except UnicodeDecodeError as e:
            msg = "Cannot decode the output of the command %s" % cmd1
            msg += "\nStream is not valid UTF-8: %s" % e
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


#
# def system_cmd_result(
#     cwd, cmd,
#     display_stdout=False,
#     display_stderr=False,
#     raise_on_error=False,
#     display_prefix=None,
#     capture_keyboard_interrupt=False):
#     '''
#         Returns the structure CmdResult; raises CmdException.
#         Also OSError are captured.
#         KeyboardInterrupt is passed through unless specified
#
#         :param write_stdin: A string to write to the process.
#     '''
#     if display_prefix is None:
#         display_prefix = '%s %s' % (cwd, cmd)
#
#     try:
#
#         p = subprocess.Popen(
#                 cmd2args(cmd),
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 cwd=cwd)
#
#         if 1:  # XXX?
#             stdout, stderr = p.communicate()
#
#             stdout = stdout.strip()
#             stderr = stderr.strip()
#
#             prefix = display_prefix + 'err> '
#             if display_stderr and stderr:
#                 print(indent(stderr, prefix))
#
#             prefix = display_prefix + 'out> '
#             if display_stdout and stdout:
#                 print(indent(stdout, prefix))
#
#         else:
#             stdout, stderr = alternative_nonworking(p, display_stderr, display_stdout, display_prefix)
#
#         p.wait()
#
#     except KeyboardInterrupt:
#         if not capture_keyboard_interrupt:
#             raise
#         else:
#             if raise_on_error:
#                 raise CmdException('Interrupted')
#             else:
#                 res = CmdResult(cwd=cwd, cmd=cmd,
#                                 ret=None, stdout='Interrupted', stderr='Interrupted')
#                 return res
#
#     ret = p.returncode
#
#     res = CmdResult(cwd, cmd, ret, stdout, stderr)
#
#     if raise_on_error:
#         if res.ret != 0:
#             raise CmdException(res)
#
#     return res

#
# def alternative_nonworking(p, display_stderr, display_stdout, display_prefix):
#     """Returns stdout, stderr"""
#
#     # p.stdin.close()
#     stderr = ""
#     stdout = ""
#     stderr_lines = []
#     stdout_lines = []
#     stderr_to_read = True
#     stdout_to_read = True
#
#     def read_stream(stream, lines):
#         if stream:
#             nexti = stream.readline()
#             if not nexti:
#                 stream.close()
#                 return False
#             lines.append(nexti)
#             return True
#         else:
#             stream.close()
#             return False
#
#     # XXX: read all the lines
#     while stderr_to_read or stdout_to_read:
#
#         if stderr_to_read:
#             stderr_to_read = read_stream(p.stderr, stderr_lines)
#         #             stdout_to_read = False
#
#         if stdout_to_read:
#             stdout_to_read = read_stream(p.stdout, stdout_lines)
#
#         while stderr_lines:
#             l = stderr_lines.pop(0)
#             stderr += l
#             if display_stderr:
#                 sys.stderr.write("%s ! %s" % (display_prefix, l))
#
#         while stdout_lines:
#             l = stdout_lines.pop(0)
#             stdout += l
#             if display_stdout:
#                 sys.stderr.write("%s   %s" % (display_prefix, l))
#
#     stdout = p.stdout.read()
#     return stdout, stderr
