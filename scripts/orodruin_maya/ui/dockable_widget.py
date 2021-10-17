from __future__ import annotations

from typing import Optional

import attr
from maya import OpenMayaUI, cmds
from PySide2 import QtCore, QtWidgets
from shiboken2 import getCppPointer


@attr.s
class WorkspaceControl:
    name: str = attr.ib()

    widget: Optional[QtWidgets.QWidget] = attr.ib(init=False, default=None)

    def exists(self) -> bool:
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self) -> bool:
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible: bool):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label: str) -> None:
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self) -> bool:
        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self) -> bool:
        return cmds.workspaceControl(self.name, q=True, collapsed=True)

    def add_widget_to_layout(self, widget: QtWidgets.QWidget) -> None:
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            workspace_control_ptr = int(OpenMayaUI.MQtUtil.findControl(self.name))
            widget_ptr = int(getCppPointer(self.widget)[0])

            OpenMayaUI.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def restore(self, widget: QtWidgets.QWidget) -> None:
        self.add_widget_to_layout(widget)

    def create(
        self,
        label: str,
        widget: QtWidgets.QWidget,
        ui_script: Optional[str] = None,
    ) -> None:
        cmds.workspaceControl(self.name, label=label)
        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)


class DockableWidget(QtWidgets.QWidget):
    """A Base class to create Dockable Widgets for Maya."""

    WINDOW_TITLE = "Dockable Widget"

    ui_instance: Optional[DockableWidget] = None

    @classmethod
    def open(cls):
        """Create or show this widget."""
        if cls.ui_instance:
            cls.ui_instance.show_workspace_control()
        else:
            cls.ui_instance = cls()
        return cls.ui_instance

    @classmethod
    def workspace_control_name(cls):
        """Return this widget workspace control name."""
        return cls.__name__ + "WorkspaceControl"

    def __init__(self):
        super().__init__()
        self.setObjectName(self.__class__.__name__)
        self.create_workspace_control()

    def create_workspace_control(self):
        """Create or restore the WorkspaceControl for this widget."""
        self.workspace_control_instance = WorkspaceControl(
            self.workspace_control_name()
        )

        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.WINDOW_TITLE, self)

    def show_workspace_control(self):
        """Set the WorkspaceControl of this widget visible."""
        self.workspace_control_instance.set_visible(True)


if __name__ == "__main__":

    try:
        dockable_widget.setParent(None)
        dockable_widget.deleteLater()
    except:
        pass

    dockable_widget = DockableWidget.open()
