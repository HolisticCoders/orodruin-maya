"""Base class for all the purely DG rigs."""
from abc import abstractmethod
import maya.cmds as cmds
from orodruin.component import Component
from orodruin.port import Port
from orodruinmaya.metanode.fields import Accessibility

from orodruinmaya.metanode.validators import MetaNodeValidator

from .metanode.metanode import MetaNode

port_to_maya_attr_map = {
    Port.Type.int: {"attributeType": "long"},
    Port.Type.float: {"attributeType": "double"},
    Port.Type.bool: {"attributeType": "bool"},
    Port.Type.string: {"dataType": "string"},
    Port.Type.matrix: {"dataType": "matrix"},
}


class DGRig(MetaNode):
    @classmethod
    def new(cls, component: Component) -> "DGRig":
        input_node = cls(
            cmds.createNode(
                "network",
                name=f"{component.name()}_input",
            )
        )
        input_node.add_field(MetaNodeValidator, "output_node", Accessibility.private)
        output_node = input_node.create_node(
            "network",
            name=f"{component.name()}_output",
        )
        input_node.output_node.set(output_node)

        for port in component.ports():
            if port.direction() is Port.Direction.input:
                node = input_node.path()
            else:
                node = output_node.path()

            kwargs = port_to_maya_attr_map[port.type()]
            cmds.addAttr(node, longName=port.name(), **kwargs)

        return input_node

    def build(self) -> None:
        """Build the Rig."""
        pass
