import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import maya.api.OpenMaya as om2
import maya.cmds as cmds

from .metanode import MetaNode


class FieldValidator(ABC):
    """Base class for all field validators.
    A Field Validator ensures the data passed to and from the maya is of the proper type.
    """

    @staticmethod
    @abstractmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""

    @staticmethod
    @abstractmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""

    @staticmethod
    @abstractmethod
    def from_attribute(value: Any) -> Any:
        """Cast the Maya attribute return value to a Python friendly Value."""

    @staticmethod
    @abstractmethod
    def to_attribute(value: Any) -> Any:
        """Cast the Python value to a Maya compatible value."""

    @staticmethod
    @abstractmethod
    def default_value() -> Any:
        """Cast the Python value to a Maya compatible value."""


class IntValidator(FieldValidator):
    @staticmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""
        return {}

    @staticmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""
        return {"attributeType": "long"}

    @staticmethod
    def from_attribute(value: Any) -> int:
        """Cast the Maya attribute return value to a Python friendly Value."""
        return int(value)

    @staticmethod
    def to_attribute(value: Any) -> int:
        """Cast the Python value to a Maya compatible value."""
        return int(value)

    @staticmethod
    def default_value() -> int:
        return 0


class FloatValidator(FieldValidator):
    @staticmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""
        return {}

    @staticmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""
        return {"attributeType": "double"}

    @staticmethod
    def from_attribute(value: Any) -> float:
        """Cast the Maya attribute return value to a Python friendly Value."""
        return float(value)

    @staticmethod
    def to_attribute(value: Any) -> float:
        """Cast the Python value to a Maya compatible value."""
        return float(value)

    @staticmethod
    def default_value() -> float:
        return 0.0


class BoolValidator(FieldValidator):
    @staticmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""
        return {}

    @staticmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""
        return {"attributeType": "bool"}

    @staticmethod
    def from_attribute(value: Any) -> bool:
        """Cast the Maya attribute return value to a Python friendly Value."""
        return bool(value)

    @staticmethod
    def to_attribute(value: Any) -> bool:
        """Cast the Python value to a Maya compatible value."""
        return bool(value)

    @staticmethod
    def default_value() -> bool:
        return False


class StringValidator(FieldValidator):
    @staticmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""
        return {"dataType": "string"}

    @staticmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""
        return {"type": "string"}

    @staticmethod
    def from_attribute(value: Any) -> str:
        """Cast the Maya attribute return value to a Python friendly Value."""
        return str(value)

    @staticmethod
    def to_attribute(value: Any) -> str:
        """Cast the Python value to a Maya compatible value."""
        return str(value)

    @staticmethod
    def default_value() -> str:
        return ""


class MatrixValidator(FieldValidator):
    @staticmethod
    def add_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.addAttr`."""
        return {"dataType": "matrix"}

    @staticmethod
    def set_attr_kwargs() -> Dict[str, Any]:
        """kwargs passed to `cmds.setAttr`."""
        return {"type": "matrix"}

    @staticmethod
    def from_attribute(value: Any) -> om2.MMatrix:
        """Cast the Maya attribute return value to a Python friendly Value."""
        return om2.MMatrix(value)

    @staticmethod
    def to_attribute(value: Any) -> Any:
        """Cast the Python value to a Maya compatible value."""
        return value

    @staticmethod
    def default_value() -> om2.MMatrix:
        return om2.MMatrix()


class JsonValidator(StringValidator):
    @staticmethod
    def from_attribute(value: Any) -> Any:
        """Cast the Maya attribute return value to a Python friendly Value."""
        if value is None:
            value = "{}"
        return json.loads(value)

    @staticmethod
    def to_attribute(value: Any) -> str:
        """Cast the Python value to a Maya compatible value."""
        if value is None:
            value = {}
        return json.dumps(value)

    @staticmethod
    def default_value() -> om2.MMatrix:
        return {}


class MetaNodeValidator(StringValidator):
    """Stores the MetaNode as a uuid, returns a MetaNode."""

    @staticmethod
    def to_attribute(value: MetaNode) -> str:
        """Store the UUID of the maya node."""
        return value.uuid() if value else ""

    @staticmethod
    def from_attribute(value: str) -> MetaNode:
        """Get the MetaNode from the UUID."""
        if not value:
            return None

        res = cmds.ls(value)

        if res:
            node = MetaNode(res[0])
            return node

        return None

    @staticmethod
    def default_value() -> None:
        return None
