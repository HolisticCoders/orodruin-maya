from orodruinmaya.utils import reload_orodruin

reload_orodruin()

from orodruin.component import Component
from orodruin.port import Port
import orodruin.serialization
from orodruinmaya.library import MayaLibraryManager
from orodruinmaya.component_builder import ComponentBuilder
from pathlib import Path
import maya.cmds as cmds

cmds.file(new=True, force=True)

library_path = Path(R"D:\projects\holistic-coders\orodruin-maya\tests\MayaLibrary")
MayaLibraryManager.register_library(library_path)

def create_ik_fk():
    ik_fk = Component("IKFK")

    ik_fk.add_port("ik_base", Port.Direction.input, Port.Type.matrix)
    ik_fk.add_port("ik_end", Port.Direction.input, Port.Type.matrix)
    ik_fk.add_port("ik_pole_vector", Port.Direction.input, Port.Type.matrix)
    for i in range(3):
        ik_fk.add_port(f"fk{i+1}", Port.Direction.input, Port.Type.matrix)
        ik_fk.add_port(f"output{i+1}", Port.Direction.output, Port.Type.matrix)

    fk_chain = MayaLibraryManager.get_component("FKChain")
    ik_chain = MayaLibraryManager.get_component("IKChain")
    chain_blender = MayaLibraryManager.get_component("ChainBlender")

    ik_fk_children = [
        chain_blender,
        fk_chain,
        ik_chain,
    ]
    for component in ik_fk_children:
        component.set_parent(ik_fk)

    ik_fk.fk1.connect(fk_chain.input1)
    ik_fk.fk2.connect(fk_chain.input2)
    ik_fk.fk3.connect(fk_chain.input3)

    ik_fk.ik_base.connect(ik_chain.base)
    ik_fk.ik_end.connect(ik_chain.end)
    ik_fk.ik_pole_vector.connect(ik_chain.pole_vector)

    fk_chain.output1.connect(chain_blender.chain_a_01)
    fk_chain.output2.connect(chain_blender.chain_a_02)
    fk_chain.output3.connect(chain_blender.chain_a_03)
    ik_chain.output1.connect(chain_blender.chain_b_01)
    ik_chain.output2.connect(chain_blender.chain_b_02)
    ik_chain.output3.connect(chain_blender.chain_b_03)

    chain_blender.output1.connect(ik_fk.output1)
    chain_blender.output2.connect(ik_fk.output2)
    chain_blender.output3.connect(ik_fk.output3)
    

    return ik_fk

def create_controls(ik_fk):
    fk_01 = MayaLibraryManager.get_component("Control")
    fk_01.set_name("fk_01_ctl")

    fk_02 = MayaLibraryManager.get_component("Control")
    fk_02.set_name("fk_02_ctl")

    fk_03 = MayaLibraryManager.get_component("Control")
    fk_03.set_name("fk_03_ctl")

    ik_base = MayaLibraryManager.get_component("Control")
    ik_base.set_name("ik_01_ctl")

    ik_end = MayaLibraryManager.get_component("Control")
    ik_end.set_name("ik_end_ctl")

    ik_pv = MayaLibraryManager.get_component("Control")
    ik_pv.set_name("ik_pv_ctl")

    fk_01.worldMatrix.connect(ik_fk.fk1)
    fk_02.worldMatrix.connect(ik_fk.fk2)
    fk_03.worldMatrix.connect(ik_fk.fk3)

    ik_base.worldMatrix.connect(ik_fk.ik_base)
    ik_end.worldMatrix.connect(ik_fk.ik_end)
    ik_pv.worldMatrix.connect(ik_fk.ik_pole_vector)
    
    controls = [
        fk_01,
        fk_02,
        fk_03,
        ik_base,
        ik_end,
        ik_pv
    ]
    

    return controls

def create_joints(ik_fk):
    joint_01 = MayaLibraryManager.get_component("Joint")
    joint_01.set_name("joint_01")

    joint_02 = MayaLibraryManager.get_component("Joint")
    joint_02.set_name("joint_02")

    joint_03 = MayaLibraryManager.get_component("Joint")
    joint_03.set_name("joint_03")
    
    ik_fk.output1.connect(joint_01.offsetParentMatrix)
    ik_fk.output2.connect(joint_02.offsetParentMatrix)
    ik_fk.output3.connect(joint_03.offsetParentMatrix)
    
    return [
        joint_01,
        joint_02,
        joint_03,
    ]

# ik_fk = create_ik_fk()

# with Path(R"D:\projects\holistic-coders\orodruin-maya\tests\MayaLibrary\orodruin\IKFKChain.json").open("w") as f:
#     f.write(orodruin.serialization.component_as_json(ik_fk))

ik_fk = MayaLibraryManager.get_component("IKFKChain")
controls = create_controls(ik_fk)
joints  = create_joints(ik_fk)

arm = Component("Arm")
components = [ik_fk, *controls, *joints]
for component in components:
    component.set_parent(arm)


ComponentBuilder.build_component(arm)

with Path(R"D:\projects\holistic-coders\orodruin-maya\tests\MayaLibrary\orodruin\Arm.json").open("w") as f:
    f.write(orodruin.serialization.component_as_json(arm))