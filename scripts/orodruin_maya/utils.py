import logging
import sys  # pylint: disable = unused-import

import maya.api.OpenMaya as om2
from maya import cmds

logger = logging.getLogger(__name__)


def reload_orodruin():
    """Remove all orodruin modules from the Python session."""
    search = ["orodruin"]

    # HACK: We need to hold a reference to these here
    # because they will get reloaded and as such garbage collected.
    logger = globals()["logger"]  # pylint: disable = redefined-outer-name
    sys = globals()["sys"]  # pylint: disable = redefined-outer-name

    target_modules = []
    for module in sys.modules:
        for term in search:
            if term in module:
                target_modules.append(module)
                break

    for module in target_modules:
        del sys.modules[module]

    logger.info("Finished reloading orodruin.")


def get_mobject(name: str) -> om2.MFnDependencyNode:
    sel = om2.MSelectionList()
    sel.add(name)
    return om2.MFnDependencyNode(sel.getDependNode(0))


def create_node(*args, **kwargs) -> om2.MFnDependencyNode:
    return get_mobject(cmds.createNode(*args, **kwargs))
