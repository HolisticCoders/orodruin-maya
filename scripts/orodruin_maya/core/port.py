from __future__ import annotations

import logging
import re
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional, Union
from uuid import UUID

import attr
import cmdx
from maya import cmds
from orodruin.core import Port
from orodruin.core.port.port import PortDirection, PortLike, PortType
from orodruin_maya.core.node import OMNode

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


ATTRIBUTE_RE = re.compile(r"(?P<attribute>\w+)(?:\[(?P<index>\d+)\])?")


class PortKwargs(Enum):
    """A Mapping between the port type and maya addAttr kwargs."""

    Matrix4 = {"attributeType": cmdx.Matrix}
    Vector2 = {"attributeType": cmdx.Double2}
    Vector3 = {"attributeType": cmdx.Double3}
    Quaternion = {"attributeType": cmdx.Double4}
    bool = {"attributeType": cmdx.Boolean}
    float = {"attributeType": cmdx.Double}
    int = {"attributeType": cmdx.Long}
    str = {"attributeType": cmdx.String}


@attr.s
class OMPort:
    """Orodruin Maya Port handling the events from the Orodruin Port."""

    _om_state: OMState = attr.ib()
    _om_node_id: UUID = attr.ib()

    _uuid: UUID = attr.ib()
    _name: str = attr.ib()
    _type: PortType = attr.ib()
    _direction: PortDirection = attr.ib()
    _parent_id: Optional[UUID] = attr.ib(default=None)

    @classmethod
    def from_port(cls, om_state: OMState, port: Port) -> OMPort:

        parent_port = port.parent_port()
        if parent_port:
            parent_port_id = parent_port.uuid()
        else:
            parent_port_id = None

        om_port = cls(
            om_state,
            port.node().uuid(),
            port.uuid(),
            port.name(),
            port.type(),
            port.direction(),
            parent_port_id,
        )

        port.value_changed.subscribe(om_port._set_maya_attribute)

        return om_port

    def __attrs_post_init__(self):
        self._create_maya_attribute()

    def om_state(self) -> OMState:
        return self._om_state

    def uuid(self) -> UUID:
        return self._uuid

    def name(self) -> str:
        return self._name

    def type(self) -> PortType:
        return self._type

    def direction(self) -> PortDirection:
        return self._direction

    def parent(self) -> Optional[OMPort]:
        if self._parent_id:
            return self._om_state.get_om_port(self._parent_id)
        return None

    def om_node(self) -> OMNode:
        return self._om_state.get_om_node(self._om_node_id)

    def _maya_node(self) -> cmdx.Node:
        return (
            self.om_node().input_node()
            if self._direction is PortDirection.input
            else self.om_node().output_node()
        )

    def maya_attribute(self) -> cmdx.Plug:
        maya_attribute_name = (
            self.om_node().maya_attribute_map().get(self._name, self._name)
        )

        attribute_parent = self._maya_node()

        for attribute, index in ATTRIBUTE_RE.findall(maya_attribute_name):
            attribute_parent = attribute_parent[attribute]
            if index:
                attribute_parent = attribute_parent[int(index)]

        return attribute_parent

    def _create_maya_attribute(self) -> None:
        attribute_needs_created = self.name() not in self.om_node().maya_attribute_map()
        if attribute_needs_created:
            maya_attribute = (
                self.om_node().maya_attribute_map().get(self.name(), self.name())
            )

            if not self._maya_node().has_attr(maya_attribute):
                kwargs = self.add_attr_kwargs(self.om_node().maya_attribute_map())

                cmdx.addAttr(self._maya_node(), **kwargs)

    def _set_maya_attribute(self, value: PortType) -> None:
        maya_attribute = self.maya_attribute()
        if (
            cmds.attributeQuery(
                maya_attribute.name(),
                node=self._maya_node().path(),
                writable=True,
                exists=True,
            )
            and maya_attribute.writable
        ):

            maya_attribute.write(value)

    def add_attr_kwargs(
        self, attribute_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Return the kwargs needed to create the maya attribute for this Port"""
        kwargs = PortKwargs[self._type.__name__].value
        kwargs["longName"] = self._name

        parent_port = self.parent()
        if parent_port:

            attribute_map = attribute_map or {}
            maya_parent_attribute = attribute_map.get(
                parent_port.name(), parent_port.name()
            )

            kwargs["parent"] = maya_parent_attribute

        return kwargs


OMPortLike = Union[OMPort, PortLike]

__all__ = ["OMPort", "OMPortLike"]
