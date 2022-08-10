from typing import cast

from system_cmd import system_cmd_result
from zuper_commons.fs import DirPath

ROOT = cast(DirPath, ".")


def test_one() -> None:
    system_cmd_result(ROOT, "ls -a")


def test_false() -> None:
    res = system_cmd_result(ROOT, "cp not-existing done")
    print(res)


def test_false2() -> None:
    res = system_cmd_result(ROOT, "cat UTF-8-test.txt", display_stderr=True, display_stdout=True)
    print(res)
