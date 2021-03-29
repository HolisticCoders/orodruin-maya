"""Base class for all the purely DG rigs."""
import maya.cmds as cmds
from orodruin.component import Component
from orodruin.port import Port

from orodruinmaya.metanode.metanode import MetaNode


class Transform(MetaNode):
    port_to_maya_attr_map = {
        Port.Type.int: {"attributeType": "long"},
        Port.Type.float: {"attributeType": "double"},
        Port.Type.bool: {"attributeType": "bool"},
        Port.Type.string: {"dataType": "string"},
        Port.Type.matrix: {"dataType": "matrix"},
    }

    maya_node_type = "transform"

    @classmethod
    def new(cls, component: Component) -> "Transform":
        node = cls(
            cmds.createNode(
                cls.maya_node_type,
                name=component.name(),
            )
        )
        for port in component.ports():
            kwargs = cls.port_to_maya_attr_map[port.type()]
            attribute_exists = cmds.attributeQuery(port.name(), node=node, exists=True)
            if not attribute_exists:
                cmds.addAttr(node, longName=port.name(), **kwargs)

        return node

    def build(self):
        pass
