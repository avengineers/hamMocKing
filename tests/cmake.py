from typing import List
from subprocess import Popen, PIPE

"""
Helper functions to run CMake commands.
"""


def run_process(args: List[str], cwd=None) -> int:
    with Popen(
        args, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True, cwd=cwd
    ) as p:
        for line in p.stdout:
            print(line, end="")
        for line in p.stderr:
            print(line, end="")

    return p.returncode


def cmake_configure(project_dir: str, build_dir: str):
    return run_process(["cmake", "-S", project_dir, "-B", build_dir, "-G", "Ninja"])


def cmake_build_target(build_dir: str, target: str):
    return run_process(["cmake", "--build", build_dir, "--target", target])
