import importlib
from sys import path
from typing import Dict

import maya.cmds as cmds
from orodruin.component import Component
from orodruinmaya import dg_rig
from orodruinmaya.dg_rig import DGRig


class ComponentBuilder:
    @staticmethod
    def build_component(component: Component, target: str = "maya") -> DGRig:

        component_class = DGRig
        if component.library():
            try:
                module = importlib.import_module(
                    f"{component.library().name()}.{component.type()}"
                )
            except ModuleNotFoundError:
                pass
            else:
                importlib.reload(module)
                component_class = module.__dict__[component.type()]

        rig = component_class.new(component)
        rigs: Dict[str, Component] = {}
        rigs[component.name()] = rig

        if type(rig) is DGRig:
            sub_components = component.components()
            for sub_component in sub_components:
                sub_rig = ComponentBuilder.build_component(sub_component)
                rigs[sub_component.name()] = sub_rig

            connections = set()
            for sub_component in sub_components:
                for port in sub_component.ports():
                    if port.name() == "dag_parent":
                        parent_component = port.get()
                        if parent_component:
                            parent_rig = rigs[parent_component.name()]
                            child_rig = rigs[sub_component.name()]
                            cmds.parent(child_rig.path(), parent_rig.path())
                    else:
                        for connection in port.external_connections():
                            source = connection[0]
                            target = connection[1]

                            source_rig = rigs[source.component().name()]
                            target_rig = rigs[target.component().name()]

                            if source_rig is rig:
                                source_node = source_rig
                                target_node = target_rig
                            elif target_rig is rig:
                                source_node = source_rig.output_node.get()
                                target_node = target_rig.output_node.get()
                            else:
                                if isinstance(source_rig, DGRig):
                                    source_node = source_rig.output_node.get()
                                else:
                                    source_node = source_rig
                                target_node = target_rig

                            # TODO: make sure the connection isn't done multiple times
                            try:
                                cmds.connectAttr(
                                    f"{source_node.path()}.{source.name()}",
                                    f"{target_node.path()}.{target.name()}",
                                )
                            except:
                                pass
        else:
            rig.build()

        rig.write_fields()

        return rig
