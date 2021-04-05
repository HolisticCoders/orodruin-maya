"""Base class for all the purely DG rigs."""
import maya.cmds as cmds
from orodruin.component import Component

from .rig import Rig


class DGRig(Rig):
    @classmethod
    def new(cls, component: Component) -> "DGRig":
        input_node = cmds.createNode(
            cls.maya_node_type,
            name=f"{component.name()}_input",
        )

        output_node = cmds.createNode(
            cls.maya_node_type,
            name=f"{component.name()}_output",
        )
        return super().new(component, input_node, output_node)

    def build(self) -> None:
        """Build the Rig."""
