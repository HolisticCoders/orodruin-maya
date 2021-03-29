import maya.cmds as cmds
from orodruinmaya.dg_rig import DGRig


class FKChain(DGRig):
    def build(self):
        cmds.connectAttr(
            f"{self}.input1",
            f"{self.output_node.get()}.output1",
        )
        cmds.connectAttr(
            f"{self}.input2",
            f"{self.output_node.get()}.output2",
        )
        cmds.connectAttr(
            f"{self}.input3",
            f"{self.output_node.get()}.output3",
        )
