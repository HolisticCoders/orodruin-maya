import importlib
import maya.cmds as cmds
from orodruin.component import Component
from orodruinmaya.dag_rig import DAGRig


class Control(DAGRig):
    @classmethod
    def new(cls, component: Component) -> "Control":
        node = super().new(component)

        curve_transform = cmds.circle(normal=[1, 0, 0], constructionHistory=False)[0]
        curve = cmds.listRelatives(curve_transform, shapes=True)[0]

        cmds.parent(curve, node.path(), relative=True, shape=True)
        cmds.delete(curve_transform)

        return node
