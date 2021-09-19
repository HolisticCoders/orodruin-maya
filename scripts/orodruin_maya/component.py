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

    _maya_node_type: str = field(init=False, default="network")

    _graph: OMGraph = field(init=False)
    _ports: Dict[UUID, OMPort] = field(init=False, default_factory=dict)
    _input_node: str = field(init=False)
    _output_node: str = field(init=False)

    def __post_init__(self):
        self._graph = OMGraph(self._component.graph(), self)
        self._input_node = cmds.createNode(
            self._maya_node_type,
            name=self._component.name() + "_IN",
        )

        self._output_node = cmds.createNode(
            self._maya_node_type,
            name=self._component.name() + "_OUT",
        )

        self._component.name_changed.subscribe(self.rename)
        self._component.port_registered.subscribe(self.register_port)
        self._component.port_unregistered.subscribe(self.unregister_port)

    def uuid(self) -> UUID:
        """Return the UUID of the Component."""
        return self._component.uuid()

    def component(self) -> Component:
        """Return the Orodruin Component."""
        return self._component

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

        om_port = OMPort(port)

        kwargs = om_port.add_attr_kwargs()
        cmds.addAttr(node, **kwargs)

        self._ports[port.uuid()] = om_port

    def unregister_port(self, port: Port) -> None:
        """Register a port to the OMGraph."""
        if port.direction() is PortDirection.input:
            node = self._input_node
        else:
            node = self._output_node

        attribute = f"{node}.{port.name()}"

        cmds.deleteAttr(attribute)

        del self._ports[port.uuid()]
