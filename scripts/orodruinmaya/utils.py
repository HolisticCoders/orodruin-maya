import logging

import sys
from typing import Set, Type

import maya.api.OpenMaya as om2

logger = logging.getLogger(__name__)


def reload_orodruin():
    """Remove all orodruin modules from the Python session."""
    search = ["orodruin", "orodruinmaya"]

    target_modules = []
    for module in sys.modules:
        for term in search:
            if term in module:
                target_modules.append(module)
                break

    for module in target_modules:
        del sys.modules[module]

    logger.info("Finished reloading orodruin.")


def all_subclasses(cls: Type) -> Set[Type]:
    """Recursively find subclasses of a class.

    The subclasses should already be imported for this function to work properly.

    Args:
        cls (type): Class to inspect.

    Returns:
        set[type]: The set of subclasses.
    """
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def get_mobject(node: str) -> om2.MObject:
    """Return a `maya.api.OpenMaya.MObject` from a node name."""
    sel_list = om2.MSelectionList()
    sel_list.add(node)
    mobject = sel_list.getDependNode(0)
    return mobject


def get_uuid(mobject: om2.MObject) -> str:
    """Return the uuid of the given mobject."""
    return om2.MFnDependencyNode(mobject).uuid().asString()


def get_mplug(attribute: str) -> om2.MObject:
    """Return the mplug for the node attribute."""
    sel_list = om2.MSelectionList()
    sel_list.add(attribute)
    mobject = sel_list.getPlug(0)
    return mobject
