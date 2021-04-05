import maya.cmds as cmds
from orodruinmaya.dg_rig import DGRig


class TwistExtractor(DGRig):
    def build(self):
        rotation_matrix = self.create_node("pickMatrix")
        cmds.connectAttr(
            f"{self}.matrix",
            f"{rotation_matrix}.inputMatrix",
        )
        ignore_transforms = ["translate", "scale", "shear"]
        for attr in ignore_transforms:
            cmds.setAttr(f"{rotation_matrix}.use{attr.title()}", False)

        raw_bend_plane = self.create_node("aimMatrix")
        cmds.connectAttr(
            f"{rotation_matrix}.outputMatrix",
            f"{raw_bend_plane}.primaryTargetMatrix",
        )
        cmds.setAttr(f"{raw_bend_plane}.primaryTargetVector", 1, 0, 0)

        raw_bend_plane_inverse = self.create_node("inverseMatrix")
        cmds.connectAttr(
            f"{raw_bend_plane}.outputMatrix",
            f"{raw_bend_plane_inverse}.inputMatrix",
        )

        raw_twist = self.create_node("multMatrix")
        cmds.connectAttr(
            f"{rotation_matrix}.outputMatrix",
            f"{raw_twist}.matrixIn[0]",
        )
        cmds.connectAttr(
            f"{raw_bend_plane_inverse}.outputMatrix",
            f"{raw_twist}.matrixIn[1]",
        )

        raw_twist_inverse = self.create_node("inverseMatrix")
        cmds.connectAttr(
            f"{raw_twist}.matrixSum",
            f"{raw_twist_inverse}.inputMatrix",
        )

        new_bend_plane = self.create_node("multMatrix")
        cmds.connectAttr(
            f"{rotation_matrix}.outputMatrix",
            f"{new_bend_plane}.matrixIn[0]",
        )
        cmds.connectAttr(
            f"{raw_twist}.matrixSum",
            f"{new_bend_plane}.matrixIn[1]",
        )

        decompose_twist = self.create_node("decomposeMatrix")
        cmds.connectAttr(
            f"{raw_twist}.matrixSum",
            f"{decompose_twist}.inputMatrix",
        )
        cmds.connectAttr(
            f"{decompose_twist}.outputRotateX",
            f"{self.output_node.get()}.twist",
        )
