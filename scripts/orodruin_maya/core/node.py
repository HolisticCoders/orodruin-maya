from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Union
from uuid import UUID

import attr
import maya.api.OpenMaya as om2
from maya import cmds
from orodruin.core.node import Node, NodeLike
from orodruin.core.port.port import Port, PortDirection
from orodruin_maya.utils import create_node

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


@attr.s
class OMNode:
    """Orodruin Maya Node handling the events from the Orodruin Node."""

    _om_state: OMState = attr.ib()
    _uuid: UUID = attr.ib()
    _name: str = attr.ib()

    _input_node: om2.MFnDependencyNode = attr.ib(init=False)
    _output_node: om2.MFnDependencyNode = attr.ib(init=False)
    _nodes: List[om2.MFnDependencyNode] = attr.ib(init=False, factory=list)

    _om_ports: List[UUID] = attr.ib(init=False, factory=list)

    @classmethod
    def from_node(cls, om_state: OMState, node: Node) -> OMNode:
        om_node = cls(om_state, node.uuid(), node.name())
        node.port_registered.subscribe(om_node.register_port)
        node.name_changed.subscribe(om_node.set_name)
        return om_node

    def __attrs_post_init__(self) -> None:
        self.build()

    def om_state(self) -> OMState:
        return self._om_state

    def uuid(self) -> UUID:
        return self._uuid

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        cmds.rename(self._input_node.name(), name)
        self._name = name

    def input_node(self) -> om2.MFnDependencyNode:
        """This Component's input maya node"""
        return self._input_node

    def output_node(self) -> om2.MFnDependencyNode:
        """This Component's output maya node"""
        return self._output_node

    def register_port(self, port: Port) -> None:
        """Unregister a port from the OMGraph."""

        if port.direction() is PortDirection.input:
            node = self._input_node.name()
        else:
            node = self._output_node.name()

        om_port = self._om_state.get_om_port(port)

        attribute_needs_created = port.name() not in self.maya_attribute_map()
        if attribute_needs_created:
            maya_attribute = self.maya_attribute_map().get(port.name(), port.name())

            if not cmds.attributeQuery(maya_attribute, node=node, exists=True):
                kwargs = om_port.add_attr_kwargs(self.maya_attribute_map())

                cmds.addAttr(node, **kwargs)

        self._om_ports.append(om_port)

    @staticmethod
    def maya_attribute_map() -> Dict[str, str]:
        """Return a dictionary mapping the ports names and their maya attributes."""
        return {}

    def build(self):
        self._input_node = create_node("network", name=self._name)
        self._output_node = self._input_node
        self._nodes.append(self._input_node)

    def delete(self):
        for node in self._nodes:
            if cmds.objExists(node.name()):
                cmds.delete(node.name())


class OMGroupNode(OMNode):
    """Class for all Group Nodes."""

    def build(self):
        self._input_node = create_node("network", name=self._name + "_IN")
        self._output_node = create_node("network", name=self._name + "_OUT")
        self._nodes.append(self._input_node)
        self._nodes.append(self._output_node)

    def set_name(self, name: str) -> None:
        cmds.rename(self._input_node.name(), name + "_IN")
        cmds.rename(self._output_node.name(), name + "_OUT")


OMNodeLike = Union[OMNode, NodeLike]

__all__ = ["OMNode", "OMNodeLike", "OMGroupNode"]
