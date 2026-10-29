"""Whole-codebase audit, pass 6 (issue #37), at ``1dca8d75ab6f49a82397cd493714d8602131538b``: the import boundary.

- B2 (P3): the import boundary forbade network and process modules by their top-level name only, so the facilities
  of packages that are not themselves one passed with no finding: ``logging.handlers`` (socket, datagram, HTTP, SMTP
  and syslog handlers), ``logging.config`` (``listen`` opens a socket server) and ``concurrent.futures``
  (``ProcessPoolExecutor`` spawns processes). The class of B1 (pass 5). They are now forbidden; ``logging`` itself,
  which the capability gate uses, stays allowed.

Every ``test_b2_*`` case but the clean ones failed on the pass-6 commit."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import check_import_boundary


def _package(tmp_path: Path, source: str) -> Path:
    package = tmp_path / "cpe"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "m.py").write_text(source)
    return package


@pytest.mark.parametrize("source", [
    "from logging.handlers import SocketHandler\n",
    "import logging.handlers\n",
    "from logging import handlers\n",
    "import logging.config\nlogging.config.listen(9999)\n",
    "from logging.handlers import *\n",
    "from concurrent.futures import ProcessPoolExecutor\n",
    "import concurrent.futures\n",
])
def test_b2_network_and_process_submodules_are_forbidden(tmp_path: Path, source: str) -> None:
    assert check_import_boundary.check_package(_package(tmp_path, source))


@pytest.mark.parametrize("source", ["import logging\n", "from logging import getLogger\n",
                                    "import logging\nlog = logging.getLogger('cpe')\n"])
def test_b2_logging_itself_stays_allowed(tmp_path: Path, source: str) -> None:
    assert check_import_boundary.check_package(_package(tmp_path, source)) == []
