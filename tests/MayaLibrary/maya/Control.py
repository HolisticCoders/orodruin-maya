import importlib
from importlib import reload

import maya.cmds as cmds
import Transform

reload(Transform)
from orodruin.component import Component


class Control(Transform.Transform):
    @classmethod
    def new(cls, component: Component) -> "Control":
        node = super().new(component)

        curve_transform = cmds.circle(normal=[1, 0, 0], constructionHistory=False)[0]
        curve = cmds.listRelatives(curve_transform, shapes=True)[0]

        cmds.parent(curve, node.path(), relative=True, shape=True)
        cmds.delete(curve_transform)

        return node
