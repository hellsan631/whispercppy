from glob import glob
import os
import subprocess
import sys
from setuptools import setup
from sysconfig import get_path
from pybind11.setup_helpers import Pybind11Extension, build_ext as _build_ext
from distutils.core import setup, Extension

WHISPER_ENABLE_COREML = False

__version__ = "0.0.1"


class build_ext(_build_ext):
    def run(self):
        # Run CMake to build the libwhisper library
        cmake_dir = os.path.realpath(os.path.join("external", "whisper.cpp"))
        pkg_build_dir = os.path.realpath("build")
        os.makedirs(pkg_build_dir, exist_ok=True)

        extra_cmake_flags = []
        if WHISPER_ENABLE_COREML:
            extra_cmake_flags.append("-DWHISPER_COREML=1")

        subprocess.check_call(
            [
                "cmake",
                "-DCMAKE_BUILD_TYPE=Release",
                *extra_cmake_flags,
                "-Wno-dev",
                cmake_dir,
            ],
            cwd=pkg_build_dir,
        )
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "whisper"], cwd=pkg_build_dir
        )

        super().run()


def find_library_paths():
    yield from glob("build/libwhisper.*")


lib_path = get_path("platlib")
ext_modules = [
    Pybind11Extension(
        "whispercppy.api_cpp2py_export",
        [
            "src/api_cpp2py_export.cc",
            "src/params.cc",
            "src/context.cc",
            "external/whisper.cpp/examples/common.cpp",
        ],
        include_dirs=["src/", "external/whisper.cpp", "external/whisper.cpp/examples"],
        library_dirs=["./build"],
        libraries=["whisper"],
        runtime_library_dirs=[lib_path],
    ),
]

setup(
    name="whispercppy",
    version=__version__,
    author="pajowu",
    author_email="git@ca.pajowu.de",
    url="https://github.com/pajowu/whispercppy",
    description="Python bindings for whisper.cpp",
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    data_files=[(os.path.relpath(lib_path, sys.prefix), find_library_paths())],
    packages=["whispercppy"],
    package_dir={"whispercppy": "src/"},
)