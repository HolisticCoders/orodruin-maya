import site
from pathlib import Path

venv_path = Path(__file__).parent.parent / ".venv" / "Scripts" / "site-packages"
site.addsitedir(venv_path)
