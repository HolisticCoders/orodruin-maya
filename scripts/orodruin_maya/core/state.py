from __future__ import annotations

import logging
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from typing import Dict
from uuid import UUID

from orodruin.core import Connection, Graph, Node, Port, State
from orodruin.core.library import LibraryManager

from .connection import OMConnection, OMConnectionLike
from .graph import OMGraph, OMGraphLike
from .node import OMGroupNode, OMNode, OMNodeLike
from .port import OMPort, OMPortLike

logger = logging.getLogger(__name__)


@dataclass
class OMState:
    """Orodruin Maya State class handling the events from the Orodruin State"""

    _state: State

    _om_graphs: Dict[UUID, OMGraph] = field(init=False, default_factory=dict)
    _om_nodes: Dict[UUID, OMNode] = field(init=False, default_factory=dict)
    _om_ports: Dict[UUID, OMPort] = field(init=False, default_factory=dict)
    _om_connections: Dict[UUID, OMConnection] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._state.graph_created.subscribe(self.create_om_graph)
        self._state.graph_deleted.subscribe(self.delete_om_graph)
        self._state.node_created.subscribe(self.create_om_node)
        self._state.node_deleted.subscribe(self.delete_om_node)
        self._state.port_created.subscribe(self.create_om_port)
        self._state.port_deleted.subscribe(self.delete_om_port)
        self._state.connection_created.subscribe(self.create_om_connection)
        self._state.connection_deleted.subscribe(self.delete_om_connection)

    def state(self) -> State:
        return self._state

    def get_om_graph(self, graph: OMGraphLike) -> OMGraph:
        """Return a OMGraph from a OMGraphLike object.

        Raises:
            TypeError: When the graph is not a valid OMGraphLike object.
        """

        if isinstance(graph, UUID):
            om_graph = self._om_graphs[graph]
        elif isinstance(graph, Graph):
            om_graph = self._om_graphs[graph.uuid()]
        elif isinstance(graph, OMGraph):
            om_graph = self._om_graphs[graph.uuid()]
        else:
            raise TypeError(
                f"{type(graph)} is not a valid OMGraphLike type. "
                "Should be Union[OMGraph, Graph, UUID]"
            )

        return om_graph

    def get_om_node(self, node: OMNodeLike) -> OMNode:
        """Return a OMNode from a OMNodeLike object.

        Raises:
            TypeError: When the node is not a valid OMNodeLike object.
        """

        if isinstance(node, UUID):
            om_node = self._om_nodes[node]
        elif isinstance(node, Node):
            om_node = self._om_nodes[node.uuid()]
        elif isinstance(node, OMNode):
            om_node = self._om_nodes[node.uuid()]
        else:
            raise TypeError(
                f"{type(node)} is not a valid OMNodeLike type. "
                "Should be Union[OMNode, Node, UUID]"
            )

        return om_node

    def get_om_port(self, port: OMPortLike) -> OMPort:
        """Return a OMPort from a OMPortLike object.

        Raises:
            TypeError: When the port is not a valid OMPortLike object.
        """

        if isinstance(port, UUID):
            om_port = self._om_ports[port]
        elif isinstance(port, Port):
            om_port = self._om_ports[port.uuid()]
        elif isinstance(port, OMPort):
            om_port = self._om_ports[port.uuid()]
        else:
            raise TypeError(
                f"{type(port)} is not a valid OMPortLike type. "
                "Should be Union[OMPort, Port, UUID]"
            )

        return om_port

    def get_om_connection(self, connection: OMConnectionLike) -> OMConnection:
        """Return a OMConnection from a OMConnectionLike object.

        Raises:
            TypeError: When the Connection is not a valid OMConnectionLike object.
        """

        if isinstance(connection, UUID):
            om_connection = self._om_connections[connection]
        elif isinstance(connection, Connection):
            om_connection = self._om_connections[connection.uuid()]
        elif isinstance(connection, OMConnection):
            om_connection = self._om_connections[connection.uuid()]
        else:
            raise TypeError(
                f"{type(connection)} is not a valid OMConnectionLike type. "
                "Should be Union[OMConnection, Connection, UUID]"
            )

        return om_connection

    def create_om_graph(self, graph: Graph) -> None:
        om_graph = OMGraph.from_graph(self, graph)
        self._om_graphs[graph.uuid()] = om_graph
        logger.debug("Created OM graph %s.", graph.uuid())

    def delete_om_graph(self, uuid: UUID) -> None:
        del self._om_graphs[uuid]
        logger.debug("Deleted OM graph %s.", uuid)

    def create_om_node(self, node: Node) -> None:

        om_node_class = OMGroupNode
        if node.library():
            python_node_path = LibraryManager.find_node(
                node_name=node.type(),
                library_name=node.library().name(),
                target_name="maya",
                extension="py",
            )
            if python_node_path:
                spec = spec_from_file_location(python_node_path.stem, python_node_path)
                mod = module_from_spec(spec)
                spec.loader.exec_module(mod)
                _class = getattr(mod, python_node_path.stem)
                if _class:
                    om_node_class = _class

        om_node = om_node_class.from_node(self, node)

        self._om_nodes[node.uuid()] = om_node
        logger.debug("Created OM node %s.", node.path())

    def delete_om_node(self, uuid: UUID) -> None:
        om_node = self._om_nodes.pop(uuid)
        om_node.delete()
        logger.debug("Deleted OM node %s.", uuid)

    def create_om_port(self, port: Port) -> None:
        om_port = OMPort.from_port(self, port)
        self._om_ports[port.uuid()] = om_port
        logger.debug("Created OM port %s.", port.path())

    def delete_om_port(self, uuid: UUID) -> None:
        del self._om_ports[uuid]
        logger.debug("Deleted OM port %s.", uuid)

    def create_om_connection(self, connection: Connection) -> None:
        om_connection = OMConnection.from_connection(self, connection)
        om_connection.build()
        self._om_connections[connection.uuid()] = om_connection
        logger.debug("Created OM connection %s.", connection.uuid())

    def delete_om_connection(self, uuid: UUID) -> None:
        om_connection = self._om_connections.pop(uuid)
        om_connection.delete()
        logger.debug("Deleted OM connection %s.", uuid)
