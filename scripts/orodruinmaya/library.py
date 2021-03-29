import os
import site
import sys

from orodruin.library import LibraryManager


class MayaLibraryManager(LibraryManager):
    """Utility class to manage orodruin libraries from maya.
    This redefines
    """

    @classmethod
    def register_library(cls, path: os.PathLike) -> None:
        try:
            super().register_library(path)
        except NotADirectoryError as e:
            raise NotADirectoryError(e)
        else:
            maya_lib_path = str(path / "maya")
            if maya_lib_path not in sys.path:
                site.addsitedir(maya_lib_path)
