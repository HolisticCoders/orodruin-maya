import importlib
from importlib import reload

import maya.cmds as cmds
import Transform

reload(Transform)
from orodruin.component import Component


class Joint(Transform.Transform):
    maya_node_type = "joint"

    def build(self):
        cmds.setAttr(f"{self}.inheritsTransform", False)
