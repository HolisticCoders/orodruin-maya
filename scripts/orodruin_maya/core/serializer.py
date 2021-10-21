from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import attr
from maya import cmds
from orodruin.core import ExternalSerializer

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, Node, Port
    from orodruin_maya.core.state import OMState


@attr.s
class MayaSerializer(ExternalSerializer):
    _om_state: OMState = attr.ib()

    def serialize_graph(self, graph: Graph) -> Dict[str, Any]:
        return {}

    def serialize_node(self, node: Node) -> Dict[str, Any]:
        return {}

    def serialize_port(self, port: Port) -> Dict[str, Any]:
        om_port = self._om_state.get_om_port(port)
        value = om_port.maya_attribute().read()
        return {"value": value}

    def serialize_connection(
        self, connection: Connection, parent_node: Node
    ) -> Dict[str, Any]:
        return {}
