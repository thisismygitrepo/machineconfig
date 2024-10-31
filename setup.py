
""" Setup file for machineconfig package.
"""

import setuptools  # type: ignore
from src.machineconfig import __version__
import platform

# this is a comment
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
        "rich",  # required for pretty printing of many scripts.
        "paramiko",  # required by SSH
        "gitpython",  # required by repo commands
        "pudb",  # required by fire command
        "pyfzf",
        "clipboard",
        "psutil",
        "pydantic",
        "fire",  # required by fire command
        "call-function-with-timeout",
        "openai"
    ]

if platform.system() == "Windows":
    # _ = install_n_import("win32api", "pywin32")  # this is crucial for windows to pop up the concent window in case python was not run as admin.
    install_requires.append("pywin32")


setuptools.setup(
    name="machineconfig",
    version=__version__,
    author="Alex Al-Saffar",
    author_email="programmer@usa.com",
    description="Dotfiles management package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thisismygitrepo/machineconfig",
    project_urls={
        "Bug Tracker": "https://github.com/thisismygitrepo/machineconfig/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=install_requires,
)
