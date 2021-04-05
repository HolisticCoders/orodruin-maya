"""Base class for all the DAG rigs."""
import maya.cmds as cmds
from orodruin.component import Component

from .rig import Rig


class DAGRig(Rig):

    maya_node_type = "transform"

    @classmethod
    def new(cls, component: Component) -> "DAGRig":
        node = cmds.createNode(
            cls.maya_node_type,
            name=component.name(),
        )
        return super().new(component, node, node)

    def build(self) -> None:
        """Build the Rig."""
