import logging
import site
from pathlib import Path

logger = logging.getLogger(__name__)


def init_module() -> None:
    """Init the orodruin maya module."""
    venv_path = Path(__file__).parent.parent / ".venv" / "Lib" / "site-packages"
    if venv_path.exists():
        site.addsitedir(venv_path)
    else:
        logger.error(f"Virtual env path does not exist: {venv_path}")
