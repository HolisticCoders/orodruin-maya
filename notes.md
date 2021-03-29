MayaComponent
It's a metanode
It's an Abstract Class, just meant to be subclassed
A Maya Component Only defines what it is. Its ports and functionality. Doesn't care about the bigger picture.
Should be given a node type.

DAGComponent
Simple component to give a common interface for the DAG nodes 
Subclasse to create specific types of DAG components (controls, transforms, joints, guides, etc.)

DGComponent
Simple component to give a common interface for the DG nodes (pretty much all rig modules)
by default, has two nodes: input and output
Is instantiated by the RigBuilder for all (?) Vanilla Orodruin Components
Subclass to create maya specific components

ComponentBuilder
This is the Helper class that will deal with building the components whether they're maya defined or orodruin defined
It will also deal with connecting the components together properly.




----
Library.get_component needs to be passed an implementation in which to find components. search in implementation first and then in the orodruin folder.

This would return an Orodruin.Component object. not MayaComponent.

Wrap that in a MayaComponent?
```python
class MayaComponent:
    component: Component
    maya_node_type = "network"

    def build(self):
        self._maya_node = cmds.createNode(self.maya_node_type)
        for port in self.component.ports():
            cmds.addAttr(self._maya_node, longName = port.name())
        pass
```