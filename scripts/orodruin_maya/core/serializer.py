from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import attr
from orodruin.core import SerializationType, Serializer

if TYPE_CHECKING:
    from orodruin.core import Connection, Graph, Node, Port
    from orodruin_maya.core.state import OMState


@attr.s
class MayaSerializer(Serializer):
    _om_state: OMState = attr.ib()

    def serialize_graph(
        self, graph: Graph, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        return {}

    def serialize_node(
        self, node: Node, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        return {}

    def serialize_port(
        self, port: Port, serialization_type: SerializationType
    ) -> Dict[str, Any]:
        if serialization_type is SerializationType.instance:
            om_port = self._om_state.get_om_port(port)
            value = om_port.maya_attribute().read()
            data = {"value": value}
        else:
            om_port = self._om_state.get_om_port(port)
            value = om_port.maya_attribute().read()
            data = {"default_value": value}

        return data

    def serialize_connection(
        self,
        connection: Connection,
        parent_node: Node,
        serialization_type: SerializationType,
    ) -> Dict[str, Any]:
        return {}
