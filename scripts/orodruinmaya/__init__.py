import logging
import site
from pathlib import Path

from maya.utils import executeDeferred

logger = logging.getLogger(__name__)


def initialize() -> None:
    executeDeferred(init_deferred)


def init_deferred() -> None:
    add_vendor_to_path()


def add_vendor_to_path() -> None:
    repo_root = Path(__file__).parent.parent.parent
    orodruin_path = (repo_root / "vendor" / "orodruin").resolve()

    site.addsitedir(str(orodruin_path))


__all__ = ["initialize"]
