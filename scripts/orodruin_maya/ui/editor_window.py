from orodruin.core import Component
from orodruin_editor.gui.editor_window import OrodruinEditorWindow
from orodruin_maya.core import OMGraph
from PySide2.QtWidgets import QVBoxLayout

from .dockable_widget import DockableWidget


class OrodruinMayaWindow(DockableWidget):
    WINDOW_TITLE = "Orodruin Editor"

    def __init__(self):
        super().__init__()
        self.resize(1280, 720)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.orodruin_editor = OrodruinEditorWindow()
        self.layout.addWidget(self.orodruin_editor)

        self.root_component = Component("root")
        self.om_graph = OMGraph(self.root_component.graph())
        self.orodruin_editor.set_active_scene(self.root_component)
