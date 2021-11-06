from __future__ import annotations

from typing import TYPE_CHECKING, Union
from uuid import UUID

import attr
from maya import cmds
from orodruin.core.connection import Connection, ConnectionLike
from orodruin.core.port.port import PortDirection

if TYPE_CHECKING:

    from .port import OMPort, OMPortLike
    from .state import OMState


@attr.s()
class OMConnection:
    """Orodruin Maya Connection handling the events from the Orodruin Connection."""

    _om_state: OMState = attr.ib()
    _uuid: UUID = attr.ib()

    _source_id: UUID = attr.ib()
    _target_id: UUID = attr.ib()

    @classmethod
    def from_connection(cls, om_state: OMState, connection: Connection) -> OMConnection:
        return cls(
            om_state,
            connection.uuid(),
            connection.source().uuid(),
            connection.target().uuid(),
        )

    def om_state(self) -> OMState:
        """Return the OMState the connection belongs to."""
        return self._om_state

    def uuid(self) -> UUID:
        """Return the UUID of the connection"""
        return self._uuid

    def source(self) -> OMPort:
        return self._om_state.get_om_port(self._source_id)

    def target(self) -> OMPort:
        return self._om_state.get_om_port(self._target_id)

    def build(self) -> None:
        """Create the maya connection"""
        source_maya_attr = self._maya_attribute_from_port(self._source_id)
        target_maya_attr = self._maya_attribute_from_port(self._target_id)

        cmds.connectAttr(source_maya_attr, target_maya_attr, force=True)

    def delete(self) -> None:
        """Delete the maya connection."""
        source_maya_attr = self._maya_attribute_from_port(self._source_id)
        target_maya_attr = self._maya_attribute_from_port(self._target_id)
        cmds.disconnectAttr(source_maya_attr, target_maya_attr)

    def _maya_attribute_from_port(self, om_port: OMPortLike) -> str:
        """Return the maya attribute name from an OMPort"""
        om_port = self._om_state.get_om_port(om_port)

        port = self._om_state.state().get_port(om_port.uuid())
        node = port.node()
        om_node = self._om_state.get_om_node(node)
        maya_node = (
            om_node.input_node()
            if port.direction() is PortDirection.input
            else om_node.output_node()
        )
        maya_attr = om_node.maya_attribute_map().get(
            port.name(),
            port.name(),
        )

        return f"{maya_node.path()}.{maya_attr}"


OMConnectionLike = Union[OMConnection, ConnectionLike]

__all__ = ["OMConnection", "OMConnectionLike"]
