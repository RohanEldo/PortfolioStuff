import os.path
import sys
import glob
from datetime import datetime
from PySide2 import QtGui, QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
class WorflowMayaCmds:
    TEXTURE_TYPE = {"BaseColor": "baseColor",
                    "Metalness": "metalness",
                    "Roughness": "specularRoughness",
                    "Normal": "normal",
                    "Height": "displacement",
                    "Emission": "emissionColor"}
    ALPHAS = ["metalness", "specularRoughness", "emissionColor"]


    @classmethod
    def get_selected(cls):
        return cmds.ls(sl=True)[0]

    @classmethod
    def connect_attr(cls, node1, attr1, node2, attr2):
        cmds.connectAttr(f"{node1}.{attr1}", f"{node2}.{attr2}")

    @classmethod
    def set_file_node_filepath(cls, file_node, filepath, raw=False):
        cmds.setAttr(f"{file_node}.fileTextureName", filepath, type="string")
        if raw:
            cls.set_file_image_raw(file_node)

    @classmethod
    def create_shader(cls, material_type, name, prefix="", suffix=""):
        shader = cmds.shadingNode(f"{material_type}", asShader=True, n=f"{prefix}{name}{suffix}")
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader")
        return shader

    @classmethod
    def create_file_node(cls, filepath, material="", texture_type=""):
        texture_type = cls.TEXTURE_TYPE[texture_type]

        if texture_type == "normal":
            cls.connect_normal(material, filepath=filepath)

        elif texture_type in cls.ALPHAS:
            mel.eval('createRenderNodeCB -as2DTexture "" file "";')
            file_node = cls.get_selected()
            cls.set_file_node_filepath(file_node, filepath, True)
            cls.connect_attr(file_node,"outAlpha", material, texture_type)

        elif texture_type == "baseColor":
            mel.eval('createRenderNodeCB -as2DTexture "" file "";')
            file_node = cls.get_selected()
            cls.set_file_node_filepath(file_node, filepath, False)
            cls.connect_attr(file_node,"outColor", material, texture_type)

        elif texture_type == "displacement":
            cls.connect_displacement(material, filepath=filepath)

    @classmethod
    def connect_displacement(cls, material, filepath):

        shading_engine = cmds.listConnections(material, s=False, t="shadingEngine")[0]
        mel.eval(f'createRenderNodeCB -as2DTexture "" file "defaultNavigation -ce -d {shading_engine}.displacementShader -source %node; ";')
        displacement_node = cls.get_selected()
        #
        file_node = cmds.listConnections(displacement_node, source=True, type="file")[0]
        cls.set_file_node_filepath(file_node, filepath, True)
    @classmethod
    def connect_normal(cls, material, filepath):
        mel.eval(f'createRenderNodeCB - as2DTexture "" file "defaultNavigation -connectToExisting -destination {material}.normalCamera -source %node;";')

        bump_node = cls.get_selected()
        cmds.setAttr(f"{bump_node}.bumpInterp", 1)
        file_node = cmds.listConnections(bump_node, source=True, type="file")[0]
        cls.set_file_node_filepath(file_node, filepath, True)

    @classmethod
    def set_file_image_raw(cls, file_node):
        cmds.setAttr(f"{file_node}.colorSpace", "Raw", type="string")
        cmds.setAttr(f"{file_node}.alphaIsLuminance", 1)

    @classmethod
    def apply_shader(cls, object_name):

        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.sets(object_name, e=1, forceElement=shading_group)


class AffixLineEdit(QtWidgets.QWidget):

    def __init__(self, map_type, suffix=None):
        super().__init__()
        self.map_type = map_type

        self.suffix_le = QtWidgets.QLineEdit(suffix)
        self.suffix_le.setPlaceholderText("Suffix")

        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0,0,0,0)
        # layout.addStretch()
        layout.addWidget(self.suffix_le)
        self.setLayout(layout)

    def get_suffix(self):
        return self.suffix_le.text()

    def get_map_type(self):
        return self.map_type

class FilesLineEdit(QtWidgets.QWidget):

    updated = QtCore.Signal(list)

    def __init__(self, label_text="Label", filepath_text=None):
        super().__init__()
        self.filepaths = []
        label = QtWidgets.QLabel(label_text)
        self._file_le = QtWidgets.QLineEdit(filepath_text)
        self._file_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self._file_btn.setFixedWidth(40)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self._file_le)
        layout.addWidget(self._file_btn)
        layout.setContentsMargins(0,0,0,10)
        self.setLayout(layout)

        self._file_btn.clicked.connect(self.update_filepath)

    def get_filepath(self):
        return self.filepaths

    def update_filepath(self):
        multiple_filters = "Image Files (*.jpeg *.jpg *.png *.exr *.tiff);; jpeg (*.jpeg *.jpg);; PNG (*.png);; EXR (*.exr);; TIFF (*.tiff);;"
        self.filepaths = cmds.fileDialog2(fileMode=4, fileFilter=multiple_filters)
        self.updated.emit(self.get_filepath())

class WorflowUI(QtWidgets.QDialog):
    maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

    def __init__(self):
        super().__init__(WorflowUI.maya_main_window)

        self.material_dict_temp = {}
        self.txt_suffix_list = []
        self.tree_widget_items = []

        self.setWindowTitle("Apply workflow to Image Maps")
        self.setMinimumWidth(210)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.configuration_label = QtWidgets.QLabel("Configuration")
        self.channels_label = QtWidgets.QLabel("Channels")

        self.workflow_cmb = QtWidgets.QComboBox()
        self.workflow_cmb.addItem("Arnold")

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.West)
        self.create_txt_affixes()
        self.create_geo_affixes()

    def create_txt_affixes(self):
        self.tab_txt_affix = QtWidgets.QWidget()

        txt_line_edit_layout = QtWidgets.QFormLayout()

        self.txt_base_colour_le = AffixLineEdit("base_colour", "BaseColor")
        self.txt_normal_le = AffixLineEdit("normal", "Normal")
        self.txt_roughness_le = AffixLineEdit("roughness", "Roughness")
        self.txt_metallic_le = AffixLineEdit("metallic", "Metalness")
        self.txt_height_le = AffixLineEdit("height", "Height")
        self.txt_emission_le = AffixLineEdit("emission", "Emissive")

        txt_line_edit_layout.addRow("Base Colour", self.txt_base_colour_le)
        txt_line_edit_layout.addRow("Normal", self.txt_normal_le)
        txt_line_edit_layout.addRow("Roughness", self.txt_roughness_le)
        txt_line_edit_layout.addRow("Metallic", self.txt_metallic_le)
        txt_line_edit_layout.addRow("Height", self.txt_height_le)
        txt_line_edit_layout.addRow("Emissive", self.txt_emission_le)

        self.affix_widgs = [self.txt_base_colour_le, self.txt_normal_le, self.txt_roughness_le,
                            self.txt_metallic_le, self.txt_height_le, self.txt_emission_le]

        self.tab_widget.addTab(self.tab_txt_affix, "Textures")

        label = QtWidgets.QLabel("Import Textures")
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.txt_tree_widget = QtWidgets.QTreeWidget()
        self.txt_tree_widget.setHeaderHidden(True)

        # create materials
        ####################
        self.create_mat_affixes()
        self.create_btn = QtWidgets.QPushButton("Create")

        create_button_layout = QtWidgets.QHBoxLayout()
        create_button_layout.addStretch()
        create_button_layout.addWidget(self.create_btn)

        ###################

        # Tree  WIdget

        tree_btn_layout= QtWidgets.QVBoxLayout()
        self.txt_tree_btn_add = QtWidgets.QPushButton("+")
        self.txt_tree_btn_remove = QtWidgets.QPushButton("-")

        self.txt_tree_btn_add.clicked.connect(self.add_tree_items)
        self.txt_tree_btn_remove.clicked.connect(self.remove_tree_items)
        self.txt_tree_btn_add.setFixedSize(20,20)
        self.txt_tree_btn_remove.setFixedSize(20,20)
        tree_btn_layout.setContentsMargins(0,0,0,0)
        tree_btn_layout.addWidget(self.txt_tree_btn_add)
        tree_btn_layout.addWidget(self.txt_tree_btn_remove)
        tree_btn_layout.addStretch()

        tree_widget_layout =QtWidgets.QHBoxLayout()
        tree_widget_layout.addWidget(self.txt_tree_widget)
        tree_widget_layout.addLayout(tree_btn_layout)

        #######

        main_txt_layout = QtWidgets.QVBoxLayout()
        main_txt_layout.addWidget(label)
        main_txt_layout.addLayout(txt_line_edit_layout)
        main_txt_layout.addLayout(tree_widget_layout)
        main_txt_layout.addWidget(self.tab_mat_affix)
        main_txt_layout.addLayout(create_button_layout)

        self.tab_txt_affix.setLayout(main_txt_layout)


    def create_mat_affixes(self):
        self.tab_mat_affix = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.tab_mat_affix.setLayout(layout)

        self.mat_prefix_le = QtWidgets.QLineEdit()
        self.mat_prefix_le.setPlaceholderText("Prefix")
        self.mat_suffix_le = QtWidgets.QLineEdit()
        self.mat_suffix_le.setPlaceholderText("Suffix")
        mat_layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,10,0,0)
        mat_layout.addStretch()
        mat_layout.addWidget(self.mat_prefix_le)
        mat_layout.addWidget(self.mat_suffix_le)

        layout.addRow("Material Name", mat_layout)

    def create_geo_affixes(self):
        self.tab_geo_affix = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.tab_geo_affix.setLayout(layout)

        self.geo_prefix_le = QtWidgets.QLineEdit()
        self.geo_prefix_le.setPlaceholderText("Prefix")
        self.geo_suffix_le = QtWidgets.QLineEdit()
        self.geo_suffix_le.setPlaceholderText("Suffix")
        geo_layout = QtWidgets.QHBoxLayout()
        geo_layout.addStretch()
        geo_layout.addWidget(self.geo_prefix_le)
        geo_layout.addWidget(self.geo_suffix_le)

        layout.addRow("Geometry Name", geo_layout)

        self.tab_widget.addTab(self.tab_geo_affix, "Geometry")

    def create_layouts(self):

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.configuration_label)
        main_layout.addWidget(self.workflow_cmb)
        main_layout.addWidget(self.channels_label)
        main_layout.addWidget(self.tab_widget)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_materials)

    def update_material_list(self, files):
        self.update_affixes()
        for filename in files:
            mat, suffix, path = self.add_file(filename)

            if mat:
                if mat not in self.material_dict_temp:
                    self.material_dict_temp[mat] = {}
                if path not in self.material_dict_temp[mat]:
                    self.material_dict_temp[mat].update({suffix: path})

        self.update_tree_widget()

    def add_file(self, file):
        if file[-3:] == ".tx":
            return None, None, None
        filename = os.path.basename(file).split(".")[0]
        for suffix in self.txt_suffix_list:
            if filename.endswith(suffix):

                filename = filename.removesuffix(suffix)
                return filename, suffix, file

        return None, None, None

    def update_affixes(self):
        for i in self.affix_widgs:
            self.txt_suffix_list.append(i.get_suffix())

    def update_tree_widget(self):

        for i in self.get_tree_widget_list():
            if i not in self.tree_widget_items:
                self.tree_widget_items.append(i)

        for i in self.material_dict_temp:
            if i not in self.tree_widget_items:


                tree_widget = QtWidgets.QTreeWidgetItem([i])
                font = QtGui.QFont()
                font.setBold(True)
                tree_widget.setFont(0, font)

                self.txt_tree_widget.addTopLevelItem(tree_widget)

                for each in self.material_dict_temp[i]:
                    tree_child = each + ": " + str(self.material_dict_temp[i][each])
                    tree_child = QtWidgets.QTreeWidgetItem([tree_child])
                    tree_widget.addChild(tree_child)

    def create_materials(self):
        prefix = self.mat_prefix_le.text()
        suffix = self.mat_suffix_le.text()

        items = self.get_tree_widget_list()

        for item in items:
            if self.workflow_cmb.currentText()=="Arnold":
                material = WorflowMayaCmds.create_shader("aiStandardSurface", item, prefix=prefix, suffix=suffix)
                for each in self.material_dict_temp[item]:
                    filepath = self.material_dict_temp[item][each]
                    WorflowMayaCmds.create_file_node(filepath, material=material, texture_type=each)
                    print(each, ":  ", self.material_dict_temp[item][each])

    def get_tree_widget_list(self):
        temp_list = []
        for i in range(self.txt_tree_widget.topLevelItemCount()):
            text = self.txt_tree_widget.topLevelItem(i).text(0)
            temp_list.append(text)

        return temp_list

    def remove_tree_items(self):
        root = self.txt_tree_widget.invisibleRootItem()
        for item in self.txt_tree_widget.selectedItems():
            print(item.text(0))
            self.material_dict_temp.pop(item.text(0))
            (item.parent() or root).removeChild(item)

    def add_tree_items(self):
        multiple_filters = "Image Files (*.jpeg *.jpg *.png *.exr *.tiff);; jpeg (*.jpeg *.jpg);; PNG (*.png);; EXR (*.exr);; TIFF (*.tiff);;"
        filepaths = cmds.fileDialog2(fileMode=4, fileFilter=multiple_filters)

        self.update_material_list(filepaths)


if __name__ == "__main__":
    cmds.file(force=True, new=True)
    try:
        window.close()
        window.deleteLater()

    except:
        pass
    window = WorflowUI()
    window.show()