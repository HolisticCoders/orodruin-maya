from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional, Tuple
from uuid import UUID

from maya import cmds
from orodruin.core import Component, Connection, Graph
from orodruin.core.library import LibraryManager
from orodruin.core.port.port import PortDirection

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from orodruin_maya.component import OMComponent


@dataclass
class OMGraph:
    """Orodruin Maya Graph handling the events from the Orodruin Graph."""

    _graph: Graph
    _parent_component: Optional[OMComponent] = None

    _components: Dict[UUID, OMComponent] = field(init=False, default_factory=dict)
    _connections: Dict[UUID, Tuple[str, str]] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self._graph.component_registered.subscribe(self.register_component)
        self._graph.component_unregistered.subscribe(self.unregister_component)
        self._graph.connection_registered.subscribe(self.register_connection)
        self._graph.connection_unregistered.subscribe(self.unregister_connection)

    def graph(self) -> Graph:
        """Return the Orodruin Graph."""
        return self._graph

    def register_component(self, component: Component) -> None:
        """Register a component to the OMGraph."""
        # pylint: disable = import-outside-toplevel
        from orodruin_maya.component import OMComponent

        maya_component_class = OMComponent

        if component.library():
            python_component_path = LibraryManager.find_component(
                component_name=component.type(),
                library_name=component.library().name(),
                target_name="maya",
                extension="py",
            )
            if python_component_path:
                spec = importlib.util.spec_from_file_location(
                    python_component_path.stem, python_component_path
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _class = getattr(mod, python_component_path.stem)
                if _class:
                    maya_component_class = _class

        om_component = maya_component_class(component)

        self._components[component.uuid()] = om_component
        logger.debug("Registered component %s", component.name())

    def unregister_component(self, component: Component) -> None:
        """Unregister a component from the OMGraph."""
        om_component = self._components.pop(component.uuid())
        om_component.delete()
        logger.debug("Unregistered component %s", component.name())

    def register_connection(self, connection: Connection) -> None:
        """Register a connection to the OMGraph."""
        source_port = connection.source()
        source_component = source_port.component()

        source_om_component = self._components.get(source_component.uuid())
        if not source_om_component:
            if (
                self._parent_component
                and source_component.uuid() == self._parent_component.uuid()
            ):
                source_om_component = self._parent_component
            else:
                raise RuntimeError(
                    f"Found no OMComponent matching {source_component.name()}"
                )

        if source_port.direction() is PortDirection.input:
            source_maya_node = source_om_component.input_node()
        else:
            source_maya_node = source_om_component.output_node()
        source_om_port = source_om_component.ports().get(source_port.uuid())
        source_attribute = f"{source_maya_node}.{source_om_port.maya_attribute()}"

        target_port = connection.target()
        target_component = target_port.component()
        target_om_component = self._components.get(target_component.uuid())
        if not target_om_component:
            if (
                self._parent_component
                and target_component.uuid() == self._parent_component.uuid()
            ):
                target_om_component = self._parent_component
            else:
                raise RuntimeError(
                    f"Found no OMComponent matching {target_component.name()}"
                )

        if target_port.direction() is PortDirection.input:
            target_maya_node = target_om_component.input_node()
        else:
            target_maya_node = target_om_component.output_node()
        target_om_port = target_om_component.ports().get(target_port.uuid())
        target_attribute = f"{target_maya_node}.{target_om_port.maya_attribute()}"

        cmds.connectAttr(source_attribute, target_attribute)
        self._connections[connection.uuid()] = (source_attribute, target_attribute)
        logger.debug("Registered connection %s", connection.uuid())

    def unregister_connection(self, connection: Connection) -> None:
        """Unregister a connection from the OMGraph."""
        source, target = self._connections.pop(connection.uuid())
        cmds.disconnectAttr(source, target)
        logger.debug("Unregistered connection %s", connection.uuid())
