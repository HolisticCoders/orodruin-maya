from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID

import attr
import cmdx
from maya import cmds
from orodruin.core.connection import Connection
from orodruin.core.node import Node, NodeLike
from orodruin.core.port.port import Port

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


@attr.s
class OMNode:
    """Orodruin Maya Node handling the events from the Orodruin Node."""

    _om_state: OMState = attr.ib()
    _uuid: UUID = attr.ib()
    _name: str = attr.ib()

    _input_node: cmdx.Node = attr.ib(init=False)
    _output_node: cmdx.Node = attr.ib(init=False)
    _nodes: List[cmdx.Node] = attr.ib(init=False, factory=list)

    _om_ports: List[UUID] = attr.ib(init=False, factory=list)

    @classmethod
    def from_node(cls, om_state: OMState, node: Node) -> OMNode:
        """Instantiate an OMNode from an orodruin node."""
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
        self._input_node.rename(name)
        self._name = name

    def input_node(self) -> cmdx.Node:
        """This Component's input maya node"""
        return self._input_node

    def output_node(self) -> cmdx.Node:
        """This Component's output maya node"""
        return self._output_node

    def register_port(self, port: Port) -> None:
        """Unregister a port from the OMGraph."""
        om_port = self._om_state.get_om_port(port)
        self._om_ports.append(om_port.uuid())

    @staticmethod
    def maya_attribute_map() -> Dict[str, str]:
        """Return a dictionary mapping the ports names and their maya attributes."""
        return {}

    def build(self):
        """Build the OMNode."""
        self._input_node = self.create_node("network", name=self._name)
        self._output_node = self._input_node

    def delete(self):
        """Delete all the nodes owned by the OMNode"""
        for node in self._nodes:
            if node.exists:
                cmds.delete(node.path())

    def create_node(
        self,
        node_type: str,
        name: Optional[str] = None,
        parent: Optional[cmdx.Node] = None,
    ) -> cmdx.Node:
        """Create a maya node and register it."""
        node = cmdx.create_node(node_type, name, parent)
        self._nodes.append(node)
        return node

    def on_connection_received(self, connection: Connection) -> None:
        """Called whenever a port of this node receives a connection."""

    def on_connection_removed(self, connection: Connection) -> None:
        """Called whenever a port of this node gets disconnected."""


class OMGroupNode(OMNode):
    """Class for all Group Nodes."""

    def build(self):
        self._input_node = self.create_node("network", name=self._name + "_IN")
        self._output_node = self.create_node("network", name=self._name + "_OUT")

    def set_name(self, name: str) -> None:
        self._input_node.rename(name + "_IN")
        self._output_node.rename(name + "_OUT")


OMNodeLike = Union[OMNode, NodeLike]

__all__ = ["OMNode", "OMNodeLike", "OMGroupNode"]
