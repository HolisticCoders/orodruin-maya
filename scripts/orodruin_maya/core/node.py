from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Union
from uuid import UUID

from maya import cmds
from orodruin.core.node import Node, NodeLike
from orodruin.core.port.port import Port, PortDirection

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


@dataclass
class OMNode:
    """Orodruin Maya Node handling the events from the Orodruin Node."""

    _om_state: OMState
    _uuid: UUID
    _name: str

    _input_node: str = field(init=False)
    _output_node: str = field(init=False)

    _om_ports: List[UUID] = field(init=False, default_factory=list)

    @classmethod
    def from_node(cls, om_state: OMState, node: Node) -> OMNode:
        om_node = cls(om_state, node.uuid(), node.name())
        node.port_registered.subscribe(om_node.register_port)
        node.name_changed.subscribe(om_node.set_name)
        return om_node

    def __post_init__(self) -> None:
        self.build()

    def om_state(self) -> OMState:
        return self._om_state

    def uuid(self) -> UUID:
        return self._uuid

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._input_node = cmds.rename(self._input_node, name)
        self._name = name

    def input_node(self) -> str:
        """This Component's input maya node"""
        return self._input_node

    def output_node(self) -> str:
        """This Component's output maya node"""
        return self._output_node

    def register_port(self, port: Port) -> None:
        """Unregister a port from the OMGraph."""

        if port.direction() is PortDirection.input:
            node = self._input_node
        else:
            node = self._output_node

        om_port = self._om_state.get_om_port(port)

        maya_attribute = self.maya_attribute_map().get(port.name(), port.name())

        if not cmds.attributeQuery(maya_attribute, node=node, exists=True):
            kwargs = om_port.add_attr_kwargs()
            cmds.addAttr(node, **kwargs)

        self._om_ports.append(om_port)

    @staticmethod
    def maya_attribute_map() -> Dict[str, str]:
        """Return a dictionary mapping the ports names and their maya attributes."""
        return {}

    def build(self):
        self._input_node = cmds.createNode("network", name=self._name)
        self._output_node = self._input_node

    def delete(self):
        cmds.delete(self._input_node)


class OMGroupNode(OMNode):
    """Class for all Group Nodes."""

    def build(self):
        self._input_node = cmds.createNode("network", name=self._name + "_IN")
        self._output_node = cmds.createNode("network", name=self._name + "_OUT")

    def set_name(self, name: str) -> None:
        self._input_node = cmds.rename(self._input_node, name + "_IN")
        self._output_node = cmds.rename(self._output_node, name + "_OUT")

    def delete(self):
        cmds.delete(self._input_node)
        cmds.delete(self._output_node)


OMNodeLike = Union[OMNode, NodeLike]

__all__ = ["OMNode", "OMNodeLike", "OMGroupNode"]
