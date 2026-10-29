"""Whole-codebase audit, pass 7 (issue #37), at ``c55e4cee65656355850bde32b07059e37d8b523b``: the import boundary.

- B3 (P3): further standard-library facilities whose own interface spawns a process or serves the network passed with
  no finding: ``_ctypes`` (the module beneath ``ctypes``), ``_bootsubprocess`` and ``distutils.spawn`` (Python 3.11),
  ``ensurepip`` and ``venv`` (pip in a subprocess), ``pydoc`` (``browse`` serves HTTP, ``pipepager`` spawns) and
  ``compileall`` (a process pool). The class of B1 (pass 5) and B2 (pass 6). ``platform`` and ``uuid``, which spawn
  only inside some of their functions, stay the documented limit of the static check.

Every ``test_b3_*`` forbidden case failed on the pass-7 pin."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import check_import_boundary
from tests.test_audit_pass6_tools import _package


@pytest.mark.parametrize("source", [
    "import _ctypes\n",
    "from _ctypes import dlopen\n",
    "import _bootsubprocess\n",
    "from distutils.spawn import spawn\n",
    "import ensurepip\n",
    "from venv import create\n",
    "import pydoc\npydoc.browse()\n",
    "from compileall import compile_dir\n",
])
def test_b3_process_and_network_facilities_are_forbidden(tmp_path: Path, source: str) -> None:
    assert check_import_boundary.check_package(_package(tmp_path, source))


def test_b3_the_package_stays_clean() -> None:
    package = Path(__file__).resolve().parent.parent / "cpe"
    assert check_import_boundary.check_package(package) == []
