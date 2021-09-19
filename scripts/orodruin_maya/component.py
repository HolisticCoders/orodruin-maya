from dataclasses import dataclass, field
from typing import Dict
from uuid import UUID

from maya import cmds
from orodruin.core import Component, Port, PortDirection
from orodruin_maya.graph import OMGraph
from orodruin_maya.port import OMPort


@dataclass
class OMComponent:
    """Orodruin Maya Graph handling the events from the Orodruin Graph."""

    _component: Component

    _graph: OMGraph = field(init=False)
    _ports: Dict[UUID, OMPort] = field(init=False, default_factory=dict)
    _input_node: str = field(init=False)
    _output_node: str = field(init=False)

    def __post_init__(self):
        self._graph = OMGraph(self._component.graph(), self)

        self._component.name_changed.subscribe(self.rename)
        self._component.port_registered.subscribe(self.register_port)
        self._component.port_unregistered.subscribe(self.unregister_port)

        self.build()

    def build(self):
        """Create the maya graph for this component.

        This range from simply mapping to a maya native node or create a full graph.
        This method _must_ define `self._input_node` and `self._output_node`.
        """
        self._input_node = cmds.createNode(
            "network",
            name=self._component.name() + "_IN",
        )

        self._output_node = cmds.createNode(
            "network",
            name=self._component.name() + "_OUT",
        )

    @staticmethod
    def maya_attribute_map() -> Dict[str, str]:
        """Return a dictionary mapping the ports names and their maya attributes."""
        return {}

    def uuid(self) -> UUID:
        """Return the UUID of the Component."""
        return self._component.uuid()

    def component(self) -> Component:
        """Return the Orodruin Component."""
        return self._component

    def ports(self) -> Dict[UUID, OMPort]:
        """Return the Orodruin Component."""
        return self._ports

    def graph(self) -> OMGraph:
        """Return the inner OMGraph."""
        return self._graph

    def input_node(self) -> str:
        """This Component's input maya node"""
        return self._input_node

    def output_node(self) -> str:
        """This Component's output maya node"""
        return self._output_node

    def delete(self) -> None:
        """Delete the maya nodes of this Component"""
        cmds.delete([self._input_node, self._output_node])

    def rename(self, value: str) -> None:
        """Rename the maya nodes"""
        self._input_node = cmds.rename(
            self._input_node,
            value + "_IN",
        )
        self._input_node = cmds.rename(
            self._input_node,
            value + "_OUT",
        )

    def register_port(self, port: Port) -> None:
        """Unregister a port from the OMGraph."""
        if port.direction() is PortDirection.input:
            node = self._input_node
        else:
            node = self._output_node

        maya_attribute = self.maya_attribute_map().get(port.name(), port.name())

        om_port = OMPort(port, maya_attribute)

        if not cmds.attributeQuery(maya_attribute, node=node, exists=True):
            kwargs = om_port.add_attr_kwargs()
            cmds.addAttr(node, **kwargs)

        self._ports[port.uuid()] = om_port

    def unregister_port(self, port: Port) -> None:
        """Register a port to the OMGraph."""
        om_port = self._ports.pop(port.uuid())

        if port.direction() is PortDirection.input:
            node = self._input_node
        else:
            node = self._output_node

        user_defined_attributes = cmds.listAttr(node, ud=True) or []
        if om_port in user_defined_attributes:
            cmds.deleteAttr(f"{node}.{port.name()}")
