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

        try:
            module = importlib.import_module(component.type())
            importlib.reload(module)
            component_class = module.__dict__[component.type()]
        except Exception:
            component_class = DGRig

        rig = component_class.new(component)
        rigs: Dict[str, Component] = {}
        rigs[component.name()] = rig

        if type(rig) is DGRig:
            sub_components = component.components()
            for sub_component in sub_components:
                sub_rig = ComponentBuilder.build_component(sub_component)
                rigs[sub_component.name()] = sub_rig

            for sub_component in sub_components:
                for port in sub_component.ports():
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

                        try:
                            cmds.connectAttr(
                                f"{source_node}.{source.name()}",
                                f"{target_node}.{target.name()}",
                            )
                        except RuntimeError:
                            pass
        else:
            rig.build()

        # rig.write_fields()

        return rig
