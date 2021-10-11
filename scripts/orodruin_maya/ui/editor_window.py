from orodruin.core.state import State
from orodruin_editor.ui.window import OrodruinWindow
from orodruin_maya.core.state import OMState
from PySide2.QtWidgets import QVBoxLayout

from .dockable_widget import DockableWidget


class OrodruinMayaWindow(DockableWidget):
    WINDOW_TITLE = "Orodruin Editor"

    def __init__(self):
        super().__init__()
        self.resize(1280, 720)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        state = State()

        orodruin_editor = OrodruinWindow(state)

        om_state = OMState(state, orodruin_editor.graphics_state())

        self.layout.addWidget(orodruin_editor)

    def keyPressEvent(self, *args, **kwargs) -> None:
        """Don't pass any keyboard event to maya."""
