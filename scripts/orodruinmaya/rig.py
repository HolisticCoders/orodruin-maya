from abc import abstractmethod, ABC

import maya.cmds as cmds
from orodruin.component import Component
from orodruin.port import Port

from .metanode.fields import Accessibility
from .metanode.metanode import MetaNode
from .metanode.validators import (
    BoolValidator,
    FloatValidator,
    IntValidator,
    MatrixValidator,
    MetaNodeValidator,
    StringValidator,
)

validator_from_port = {
    Port.Type.int: IntValidator,
    Port.Type.float: FloatValidator,
    Port.Type.bool: BoolValidator,
    Port.Type.string: StringValidator,
    Port.Type.matrix: MatrixValidator,
    Port.Type.reference: MetaNodeValidator,
}


class Rig(MetaNode, ABC):
    @classmethod
    def new(cls, component: Component, input_node: str, output_node: str) -> "Rig":
        """create a new

        Args:
            component: The Orodruin Component of this Rig.
            node: The input node of this rig, on which the input port will be created.
            output_node: The input node of this rig, on which the input port will be created.

        Note: The node and output_node can be the same
        """
        rig = cls(input_node)
        output_node = MetaNode(output_node)

        rig.add_field(MetaNodeValidator, "output_node", Accessibility.private)
        rig.output_node.set(output_node)

        for port in component.ports():
            if port.direction() is Port.Direction.input:
                node = rig
            else:
                node = rig.output_node.get()

            validator = validator_from_port[port.type()]

            node.add_field(validator, port.name(), Accessibility.public)
            node.fields()[port.name()].set(port.get())

        return rig

    @abstractmethod
    def build(self) -> None:
        """Build the Rig."""
