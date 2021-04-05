import maya.cmds as cmds
from orodruinmaya.dg_rig import DGRig


class ChainBlender(DGRig):
    def build(self):
        for i in range(3):
            blend = cmds.createNode("blendMatrix")
            cmds.connectAttr(
                f"{self}.blender",
                f"{blend}.target[1].weight",
            )

            cmds.connectAttr(
                f"{self}.chain_a_0{i+1}",
                f"{blend}.target[0].targetMatrix",
            )
            cmds.connectAttr(
                f"{self}.chain_b_0{i+1}",
                f"{blend}.target[1].targetMatrix",
            )
            cmds.connectAttr(
                f"{blend}.outputMatrix",
                f"{self.output_node.get()}.output{i+1}",
            )
