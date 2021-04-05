import os
import maya.cmds as cmds

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
            pass
            # library_name = path.name
            # maya_module = path / "maya" / "modules" / f"{library_name}.mod"
            # cmds.loadModule(load=str(maya_module))
