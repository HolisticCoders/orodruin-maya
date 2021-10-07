from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional, Union
from uuid import UUID

from orodruin.core import Port
from orodruin.core.port.port import PortDirection, PortLike, PortType

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


class PortKwargs(Enum):
    """A Mapping between the port type and maya addAttr kwargs."""

    Matrix4 = {"dataType": "matrix"}
    Vector2 = {"attributeType": "double2"}
    Vector3 = {"attributeType": "double3"}
    Quaternion = {"attributeType": "double4"}
    bool = {"attributeType": "bool"}
    float = {"attributeType": "double"}
    int = {"attributeType": "long"}
    str = {"dataType": "string"}


@dataclass
class OMPort:
    """Orodruin Maya Port handling the events from the Orodruin Port."""

    _om_state: OMState
    _uuid: UUID
    _name: str
    _type: PortType
    _direction: PortDirection
    _parent_id: Optional[UUID]

    @classmethod
    def from_port(cls, om_state: OMState, port: Port) -> OMPort:

        parent_port = port.parent_port()
        if parent_port:
            parent_port_id = parent_port.uuid()
        else:
            parent_port_id = None

        return cls(
            om_state,
            port.uuid(),
            port.name(),
            port.type(),
            port.direction(),
            parent_port_id,
        )

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

    def add_attr_kwargs(self) -> Dict[str, str]:
        """Return the kwargs needed to create the maya attribute for this Port"""
        kwargs = PortKwargs[self._type.__name__].value
        kwargs["longName"] = self._name

        parent_port = self.parent()
        if parent_port:
            kwargs["parent"] = parent_port.name()

        return kwargs


OMPortLike = Union[OMPort, PortLike]

__all__ = ["OMPort", "OMPortLike"]
