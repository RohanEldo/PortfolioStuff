import sys
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance, getCppPointer
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import glob
import mtoa.core
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

class CollapsibleHeader(QtWidgets.QWidget):
    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")

    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.set_background_colour(None)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        self.set_text(text)
        self.set_expanded(False)

    def set_background_colour(self, colour):
        if not colour:
            colour = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, colour)
        self.setPalette(palette)

    def set_text(self, text):
        self.text_label.setText(f"<b>{text}</b>")

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded: bool):
        self._expanded = expanded

        if self._expanded:
            self.icon_label.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)

        self.body_wdg = QtWidgets.QWidget()

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)

    def add_widget(self, widget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)

    def set_header_background_color(self, colour):
        self.header_wdg.set_background_colour(colour)

    def set_expanded(self, expanded):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

    def on_header_clicked(self):
        self.set_expanded(not self.header_wdg.is_expanded())



class VdbImporter(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    UI_NAME = "VdbImporter"

    def __init__(self, workspace_control_name=None):
        super().__init__()
        self.setObjectName(self.UI_NAME)
        self.setWindowTitle("VDB Import")
        self.setMinimumWidth(250)

        workspace_control_name = "{0}WorkspaceControl".format(self.UI_NAME)

        if cmds.workspaceControl(workspace_control_name, q=True, exists=True):
            workspace_control_ptr = int(omui.MQtUtil.findControl(workspace_control_name))
            widget_ptr = int(getCppPointer(self)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

        self.accepted_files = []
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):

        self.file_header = CollapsibleWidget("Import VDBS")

        self.file_edit = QtWidgets.QLineEdit()
        self.load_btn = QtWidgets.QPushButton("..")
        self.load_btn.setFixedWidth(30)

        self.file_remove_btn = QtWidgets.QPushButton("Remove")
        self.volume_create_btn = QtWidgets.QPushButton("Create")

        self.material_header = CollapsibleWidget("Create Materials")

        self.file_list_field = QtWidgets.QListWidget()
        self.file_list_field.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.volume_checkbox = QtWidgets.QCheckBox("Volume")
        self.surface_checkbox = QtWidgets.QCheckBox("Surface")
        self.surface_checkbox.setChecked(True)

        self.update_btn = QtWidgets.QPushButton("Update")
        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.close_btn = QtWidgets.QPushButton("Close")

        self.material_list_field = QtWidgets.QListWidget()
        self.material_field = QtWidgets.QLineEdit("blinn")

    def create_layouts(self):
        self.body_wdg = QtWidgets.QWidget()

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)
        self.body_layout.setAlignment(QtCore.Qt.AlignTop)


        file_load_layout = QtWidgets.QHBoxLayout()
        file_load_layout.addWidget(self.file_edit)
        file_load_layout.addWidget(self.load_btn)

        file_button_layout = QtWidgets.QHBoxLayout()
        file_button_layout.addStretch()
        file_button_layout.addWidget(self.file_remove_btn)
        file_button_layout.addWidget(self.volume_create_btn)

        file_layout = QtWidgets.QFormLayout()
        file_layout.addRow("         File Path:", file_load_layout)
        file_layout.addRow("VDBs", self.file_list_field)
        file_layout.addRow("", file_button_layout)

        self.file_header.add_layout(file_layout)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Object Names:", self.material_list_field)
        form_layout.addRow("Material:", self.material_field)
        checkbox_layout = QtWidgets.QHBoxLayout()
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(self.surface_checkbox)
        checkbox_layout.addWidget(self.volume_checkbox)
        form_layout.addRow("", checkbox_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.close_btn)

        material_layout = QtWidgets.QVBoxLayout()
        material_layout.addLayout(form_layout)
        material_layout.addLayout(button_layout)

        self.material_header.add_layout(material_layout)

        self.body_layout.addWidget(self.file_header)
        self.body_layout.addWidget(self.material_header)

        scroll_layout = QtWidgets.QScrollArea()
        scroll_layout.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_layout.setWidgetResizable(True)
        scroll_layout.setWidget(self.body_wdg)


        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_layout)
        # main_layout.addStretch()

    def create_connections(self):

        self.file_remove_btn.clicked.connect(self.file_list_remove)
        self.close_btn.clicked.connect(self.close)
        self.update_btn.clicked.connect(self.update_material_list)
        self.accept_btn.clicked.connect(self.create_shaders_multiple)
        self.load_btn.clicked.connect(self.open_directory)
        self.file_edit.editingFinished.connect(self.update_VDB_list)
        self.volume_create_btn.clicked.connect(self.create_ai_volume)

    def get_selected_objects(self):
        sel = cmds.ls(selection=True)
        return sel

    def update_material_list(self):
        self.material_list_field.clear()
        selection = self.get_selected_objects()
        if selection:
            for obj in selection:
                self.material_list_field.addItem(obj)

    def create_shaders_multiple(self):

        material = self.material_field.text()
        for obj_name in self.get_list_widget_items(self.material_list_field):
            self.create_shader(material, obj_name)

    def create_shader(self, material_name, object_name):
        shader = cmds.shadingNode(f"{material_name}", asShader=True, n=f"{object_name}_MAT")
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        if self.surface_checkbox.isChecked():
            cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader")
        if self.volume_checkbox.isChecked():
            cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.volumeShader")

        cmds.sets(object_name, e=1, forceElement=shading_group)
        # cmds.setAttr(f"{shader}.color", 0, 2, 2)

    def get_list_widget_items(self, list_widget):
        items = []
        x = list_widget.count()
        for i in range(x):
            items.append(list_widget.item(i).text())
        return items

    def open_directory(self):
        result = QtWidgets.QFileDialog.getExistingDirectory()
        self.file_edit.setText(result)
        self.update_VDB_list()

    def update_VDB_list(self):
        if self.file_edit.text():
            if QtCore.QDir(self.file_edit.text()).exists():
                files = self.get_files()
                for file in files:
                    self.file_list_field.addItem(file)

    def get_files(self):
        filepath = self.file_edit.text()
        files = glob.glob(f"{filepath}/**/*.vdb", recursive=True)

        accepted_files = []
        for file in files:
            unique_name = file[:-9]
            unique_name = unique_name.replace("\\", r"/")
            if unique_name not in self.accepted_files:
                self.accepted_files.append(unique_name)
                accepted_files.append(unique_name)

        return accepted_files

    def create_ai_volume(self):
        selected = self.get_list_widget_items(self.file_list_field)

        for filepath in selected:
            name = filepath.split("/")
            obj_name = name[-1]

            files = "/".join(name[:-1])
            files = glob.glob(f"{files}/*.vdb")[0]

            ai_volume = mtoa.core.createArnoldNode("aiVolume", name=f"{obj_name}_VOL", skipSelect=False)
            cmds.setAttr(f"{ai_volume}.filename", files, type="string")
            cmds.setAttr(f"{ai_volume}.useFrameExtension", 1)
            parent = cmds.listRelatives(ai_volume, parent=True)[0]
            cmds.rename(parent, obj_name)

            shader = cmds.shadingNode(f"aiStandardVolume", asShader=True, n=f"{obj_name}_MAT")
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
            cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.volumeShader")
            cmds.sets(obj_name, e=1, forceElement=shading_group)

    def file_list_remove(self):
        selected = self.file_list_field.selectedItems()
        for each in selected:
            self.file_list_field.takeItem(self.file_list_field.row(each))
            self.accepted_files.remove(each.text())


if __name__ == "__main__":

    try:
        if vdb_instance and vdb_instance.parent():
            workspace_control_name = vdb_instance.parent().objectName()

            if cmds.window(workspace_control_name, exists=True):
                cmds.deleteUI(workspace_control_name)

    except:
        pass

    vdb_instance = VdbImporter()

    ui_script = "from vdb_importer import VdbImporter\nvdb_instance = VdbImporter()"
    vdb_instance.show(dockable=True, uiScript=ui_script)