from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Dict, Union
from uuid import UUID

from orodruin.core import Port
from orodruin.core.port.port import PortDirection, PortLike, PortType

if TYPE_CHECKING:
    from .state import OMState

logger = logging.getLogger(__name__)


class PortKwargs(Enum):
    """A Mapping between the port type and maya addAttr kwargs."""

    Matrix4 = {"dataType": "matrix"}
    Vector2 = {}
    Vector3 = {}
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

    @classmethod
    def from_port(cls, om_state: OMState, port: Port) -> OMPort:
        return cls(om_state, port.uuid(), port.name(), port.type(), port.direction())

    def om_state(self) -> OMState:
        return self._om_state

    def uuid(self) -> UUID:
        return self._uuid

    def add_attr_kwargs(self) -> Dict[str, str]:
        """Return the kwargs needed to create the maya attribute for this Port"""
        kwargs = PortKwargs[self._type.__name__].value
        kwargs["longName"] = self._name

        return kwargs


OMPortLike = Union[OMPort, PortLike]

__all__ = ["OMPort", "OMPortLike"]
