from dataclasses import dataclass
from enum import Enum
from typing import Dict
from uuid import UUID

from orodruin.core import Port


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
    """Orodruin Maya Graph handling the events from the Orodruin Graph."""

    _port: Port
    _maya_attribute: str

    def add_attr_kwargs(self) -> Dict[str, str]:
        """Return the kwargs needed to create the maya attribute for this Port"""
        kwargs = PortKwargs[self._port.type().__name__].value
        kwargs["longName"] = self._port.name()

        return kwargs

    def port(self) -> Port:
        """Return the Orodruin Component."""
        return self._port

    def maya_attribute(self) -> str:
        """Return the maya attribute this port maps to."""
        return self._maya_attribute

    def uuid(self) -> UUID:
        """Return the UUID of the Port."""
        return self._port.uuid()
