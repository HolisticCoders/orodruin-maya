import logging
import traceback
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Iterator, Optional, TYPE_CHECKING, Any, Type

import maya.api.OpenMaya as om2
import maya.cmds as cmds
from orodruinmaya.utils import get_mplug

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .metanode import MetaNode
    from .validators import FieldValidator


class Accessibility(Enum):
    private = "private"
    public = "public"


class Field(ABC):
    def __init__(
        self,
        validator: Type["FieldValidator"],
        metanode: "MetaNode",
        name: str,
        default_value=None,
    ) -> None:
        self._validator = validator
        self._metanode = metanode
        self._name = name
        self._value = (
            default_value if default_value is not None else validator.default_value()
        )

        self.create_maya_attribute()

        self._mplug = get_mplug(self.path())

        self.read()

    @abstractmethod
    def create_maya_attribute(self) -> None:
        """Create the maya attribute."""

    @abstractmethod
    def get(self) -> Any:
        """Return the field value."""

    @abstractmethod
    def set(self, value) -> None:
        """Set the field value."""

    @abstractmethod
    def read(self) -> Any:
        """Read the field value from Maya."""

    @abstractmethod
    def write(self) -> None:
        """Write the field value to Maya."""

    def name(self) -> str:
        return self._name

    def validator(self) -> Type["FieldValidator"]:
        return self._validator

    def metanode(self) -> "MetaNode":
        return self._metanode

    def mplug(self) -> "om2.MPlug":
        return self._mplug

    def path(self) -> str:
        return f"{self.metanode().path()}.{self.name()}"


class SingleField(Field):
    def __init__(
        self,
        validator: Type["FieldValidator"],
        metanode: "MetaNode",
        name: str,
        accessibility: "Accessibility",
        default_value: Optional[Any] = None,
    ) -> None:

        self._accessibility = accessibility

        super().__init__(validator, metanode, name, default_value)

    def create_maya_attribute(self) -> None:
        attribute_exits = cmds.attributeQuery(
            self.name(),
            node=self.metanode().path(),
            exists=True,
        )
        if not attribute_exits:
            cmds.addAttr(
                self.metanode().path(),
                longName=self.name(),
                keyable=False,
                **self.validator().add_attr_kwargs(),
            )
            if self.accessibility() is Accessibility.public:
                cmds.setAttr(self.path(), edit=True, channelBox=True)

    @contextmanager
    def _protect_attribute(self):
        """Lock the maya attribute if it is private."""
        cmds.setAttr(self.path(), lock=False)

        yield

        cmds.setAttr(self.path(), lock=True)

    def write(self) -> None:
        try:
            value = self._validator.to_attribute(self._value)
        except Exception as error:
            logger.debug(traceback.format_exc())
            logger.warning(error)
        else:
            if self.accessibility() is Accessibility.private:
                with self._protect_attribute():
                    self._set_maya_attr(value)
            else:
                self._set_maya_attr(value)

    def _set_maya_attr(self, value) -> None:
        if cmds.listConnections(self.path(), source=True, destination=False):
            return
        cmds.setAttr(self.path(), value, **self.validator().set_attr_kwargs())

    def read(self) -> None:
        value = cmds.getAttr(self.path())
        if value is None:
            return
        self._value = self.validator().from_attribute(value)

    def get(self) -> Any:
        if self.accessibility() is Accessibility.public:
            # read the value from maya in case it was manually changed.
            self.read()

        return self._value

    def set(self, value: Any) -> None:
        self._value = value

        if self.accessibility() is Accessibility.public:
            # Value was likely set by the user directly or from a GUI, the value
            # needs to be written to maya to be accessed properly later on.
            self.write()

    def accessibility(self) -> "Accessibility":
        return self._accessibility


class MultiField(Field):
    def __init__(
        self,
        validator: Type["FieldValidator"],
        metanode: "MetaNode",
        name: str,
        default_value=None,
    ) -> None:
        if default_value is None:
            default_value = []
        super().__init__(validator, metanode, name, default_value=default_value)

    def create_maya_attribute(self) -> None:
        attribute_exits = cmds.attributeQuery(
            self.name(),
            node=self.metanode().path(),
            exists=True,
        )
        if not attribute_exits:
            cmds.addAttr(
                self.metanode().path(),
                longName=self.name(),
                multi=True,
                **self.validator().add_attr_kwargs(),
            )

    def get(self) -> Any:
        """Return the field value."""
        return self._value

    def set(self, value) -> None:
        """Set the field value."""
        self._value = value

    def write(self) -> None:
        value = self._value

        with self._protect_attribute():

            self._clear_maya_attribute()

            for i, index_value in enumerate(value):

                index_value = self.validator().to_attribute(index_value)
                cmds.setAttr(
                    f"{self.path()}[{i}]",
                    index_value,
                    **self.validator().set_attr_kwargs(),
                )

    def read(self) -> None:
        result = []
        for attr in self._iter_elements():
            value = self.validator().from_attribute(cmds.getAttr(attr))
            result.append(value)

        self._value = result

    def clear(self) -> None:
        self._clear_python_attribute()
        self._clear_maya_attribute()

    def _clear_python_attribute(self) -> None:
        self._value = []

    def _clear_maya_attribute(self) -> None:
        cmds.setAttr(self.path(), lock=False)

        for attr in self._iter_elements():
            cmds.setAttr(attr, lock=False)

        cmds.removeMultiInstance(self.path(), allChildren=True, b=True)

    @contextmanager
    def _protect_attribute(self):
        for attr in self._iter_elements():
            cmds.setAttr(attr, lock=False)

        yield

        for attr in self._iter_elements():
            cmds.setAttr(attr, lock=True)

    def _iter_elements(self) -> Iterator[str]:
        for index in range(self.mplug().numElements()):
            plug = self.mplug().elementByLogicalIndex(index)
            yield plug.name()
