from typing import TYPE_CHECKING, Any, Dict, Type, Union

import maya.api.OpenMaya as om2
import maya.cmds as cmds
from orodruinmaya.utils import all_subclasses, get_mobject, get_uuid

from .fields import Accessibility, MultiField, SingleField, Field

if TYPE_CHECKING:
    from .validators import FieldValidator


class MetaNode:
    _instances: Dict[str, "MetaNode"] = {}

    _is_first_instance = True

    maya_node_type = "network"

    def __new__(cls, node: str) -> "MetaNode":
        """Re-instantiate the proper MetaNode subclass if the node has already been a MetaNode in its lifetime."""
        if not isinstance(node, str):
            raise TypeError("MetaNode can only be instanciated from a node name.")

        if not cmds.objExists(node):
            raise ValueError(
                f"Specified Maya node {node} does not exist; "
                "`MetaNode.new` can be used to create a node along with the MetaNode"
            )

        uuid = get_uuid(get_mobject(node))
        instance = MetaNode._instances.get(uuid)
        if instance:
            return instance

        if cmds.attributeQuery("metanode_type", node=node, exists=True):
            stored_class_name = cmds.getAttr(f"{node}.metanode_type")
        else:
            stored_class_name = cls.__name__

        class_to_instantiate = None

        if stored_class_name == cls.__name__:
            class_to_instantiate = cls
        else:
            for subclass in all_subclasses(cls):
                if stored_class_name == subclass.__name__:
                    class_to_instantiate = subclass

        if class_to_instantiate is None:
            raise Exception(
                f"The class name `{stored_class_name}` stored on the node {node}"
                f" wasn't found in {cls.__name__}'s subclasses"
            )

        return super(MetaNode, cls).__new__(class_to_instantiate)

    def __init__(self, node: str) -> None:
        self.mobject = get_mobject(node)

        if self._is_first_instance:
            self._fields: Dict[str, Any] = {}
            self._add_default_fields()

        if self.uuid() not in MetaNode._instances:
            MetaNode._instances[self.uuid()] = self

        self._is_first_instance = False

    @classmethod
    def new(cls, *args, **kwargs) -> "MetaNode":
        """Create a new MetaNode along with a new maya node.

        Subclasses should override this method to create the according maya node.

        Args:
            args and kwargs are passed as is to cmds.createNode()
        """
        return cls(cmds.createNode(cls.maya_node_type, *args, **kwargs))

    def _add_default_fields(self) -> None:
        """Create the Fields required for the `MetaNode` to work and be re-instantiated properly."""
        from .validators import (
            FieldValidator,
            JsonValidator,
            MetaNodeValidator,
            StringValidator,
        )

        self.add_field(JsonValidator, "metanode_fields", Accessibility.private)

        for field_name, field_data in self.metanode_fields.get().items():
            validator_name = field_data.pop("validator")
            accessibility = Accessibility(field_data.pop("accessibility"))
            multi = field_data.pop("multi")
            for validator_cls in all_subclasses(FieldValidator):
                if validator_cls.__name__ == validator_name:
                    self.add_field(
                        validator_cls,
                        field_name,
                        accessibility,
                        multi,
                        **field_data,
                    )

        self.add_field(StringValidator, "metanode_type", Accessibility.private)
        self.metanode_type.set(self.__class__.__name__)

        self.add_field(MetaNodeValidator, "owner", Accessibility.private)
        self.add_field(
            MetaNodeValidator,
            "owned_nodes",
            Accessibility.private,
            multi=True,
        )

    def add_field(
        self,
        validator: Type["FieldValidator"],
        name: str,
        accessibility: Accessibility,
        multi=False,
        **kwargs,
    ):
        if multi:
            field: Union[SingleField, MultiField] = MultiField(
                validator, self, name, **kwargs
            )
        else:
            field = SingleField(validator, self, name, accessibility, **kwargs)

        self._fields[name] = field

        field_data = {
            "validator": validator.__name__,
            "multi": multi,
            "accessibility": accessibility.value,
        }
        field_data.update(kwargs)

        self.metanode_fields.get()[name] = field_data

    def write_fields(self):
        """Recursively write fields from this node and its owned ones to Maya."""
        for field in self._fields.values():
            field.write()
        for node in self.owned_nodes.get():
            node.write_fields()

    def read_fields(self):
        """Recursively read fields from this node and its owned ones from Maya."""
        for field in self._fields.values():
            field.read()
        for node in self.owned_nodes.get():
            node.read_fields()

    def create_node(self, node_type, **kwargs) -> "MetaNode":
        if isinstance(node_type, str):
            metanode = MetaNode(cmds.createNode(node_type, **kwargs))
        elif issubclass(node_type, MetaNode):
            metanode = node_type.new(**kwargs)

        metanode.owner.set(self)
        owned_nodes = self.owned_nodes.get()
        owned_nodes.append(metanode)
        self.owned_nodes.set(owned_nodes)

        return metanode

    def uuid(self) -> str:
        """UUID of the MetaNode."""
        return get_uuid(self.mobject)

    def name(self) -> str:
        """Short name of the MetaNode."""
        return om2.MFnDependencyNode(self.mobject).name()

    def path(self) -> str:
        """Full DAG Path of the MetaNode."""
        if self.mobject.hasFn(om2.MFn.kDagNode):
            return om2.MFnDagNode(self.mobject).getPath().fullPathName()
        else:
            return self.name()

    def fields(self) -> Dict[str, Any]:
        """Fields of the metanode."""
        return self._fields

    def __getattr__(self, name) -> Field:
        """Get the fields of the MetaNode."""
        field = self._fields.get(name)
        if field is not None:
            return field

        raise AttributeError(f"{self.name} has no attribute or field named {name}.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name()})"

    def __str__(self) -> str:
        return self.path()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MetaNode):
            return NotImplemented
        return self.uuid() == other.uuid()
