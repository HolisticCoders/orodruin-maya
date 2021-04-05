import maya.cmds as cmds
from orodruinmaya.dag_rig import DAGRig


class Joint(DAGRig):
    maya_node_type = "joint"

    def build(self):
        super().build()
        cmds.setAttr(f"{self}.inheritsTransform", False)
