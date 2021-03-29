import maya.cmds as cmds
from orodruinmaya.dg_rig import DGRig


class IKChain(DGRig):
    def build(self):
        cmds.connectAttr(
            f"{self}.base",
            f"{self.output_node.get()}.output1",
        )
        cmds.connectAttr(
            f"{self}.end",
            f"{self.output_node.get()}.output2",
        )
        cmds.connectAttr(
            f"{self}.pole_vector",
            f"{self.output_node.get()}.output3",
        )
