from pathlib import Path
from platform import system

from .cmake import cmake_configure, cmake_build_target


class TestMiniCProject:
    def test_build_and_test_mini_c_gmock(self):
        project_dir = "tests/data/mini_c_test"
        build_dir = f"{project_dir}/build"
        if "Windows" in system():
            binary = f"{build_dir}/mini_c.exe"
        else:
            binary = f"{build_dir}/mini_c"

        exit_code = cmake_configure(project_dir, build_dir)
        """CMake configure shall be successful."""
        assert exit_code == 0

        exit_code = cmake_build_target(build_dir, "clean")
        """CMake clean shall be successful."""
        assert exit_code == 0

        exit_code = cmake_build_target(build_dir, "all")
        """CMake build shall be successful. The build includes the unit tests here."""
        assert exit_code == 0
        assert Path(binary).exists()
