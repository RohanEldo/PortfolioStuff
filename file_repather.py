import shutil
import os
import maya.OpenMaya as om
import maya.OpenMaya as omui
from maya import cmds
import copy as cp

from  maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import getCppPointer
import os

class File_Repather():

    def __init__(self):
        pass

    def get_file_nodes_in_scene(self):
        nodes = []
        for node in cmds.ls():
            if cmds.nodeType(node) == "file":
                nodes.append(node)
        return nodes

    def verify_file(self, filepath):
        info = QtCore.QFileInfo(filepath)
        return info.isFile() and info.exists()

    def get_filepath_attr(self, node):
        return cmds.getAttr(f"{node}.fileTextureName")

    def set_filepath_attr(self, node, filepath):
        return cmds.setAttr(f"{node}.fileTextureName", filepath, type="string")

    def verify_file_list(self, nodes):
        invalid_paths = []
        for node in nodes:
            if not self.verify_file(self.get_filepath_attr(node)):
                invalid_paths.append(node)
        return invalid_paths


    def repath_files(self, node, new_path, directory="", all_paths=False, copy_files=False):
        filepath = self.get_filepath_attr(node)

        if copy_files:
            if not directory:
                output_path = f"{self.get_maya_project_path()}sourceimages"
            else:
                output_path = directory

            output_path = self.copy_file(new_path, output_path)
            self.set_filepath_attr(node, output_path)
        else:
            if not directory:
                output_path = f"{self.get_maya_project_path()}sourceimages"
            else:
                output_path = directory

            output_path = self.copy_file(new_path, output_path)
            self.set_filepath_attr(node, output_path)
            os.remove(new_path)

        return new_path

    def find_missing_textures(self, filepath, directory):
        filename = os.path.basename(filepath)
        for root, dirs, files, in os.walk(directory):
            if filename in files:
                return os.path.join(root, filename)

    def copy_file(self, filepath, destination_directory):
        filename = os.path.basename(filepath)
        new_path = destination_directory
        shutil.copyfile(filepath, new_path)
        return new_path

    def get_maya_project_path(self):

        return cmds.workspace(q=True, rd=True)

class File_Node_Widget(QtWidgets.QWidget):

    # cb_checked =QtCore.Signal()
    def __init__(self, name, original_path):
        super().__init__()

        self.name = str(name)
        self._original_path = original_path
        self._is_valid = False

        self.maya_helpers = File_Repather()
        self.filename = os.path.basename(self.maya_helpers.get_filepath_attr(self.name))

        self.create_widgets()
        self.create_connections()
        self.is_valid()

    def create_widgets(self):
        self.select_cb = QtWidgets.QCheckBox("")
        temp_layout = QtWidgets.QHBoxLayout()
        temp_layout.addWidget(self.select_cb)
        temp_layout.setAlignment(QtCore.Qt.AlignCenter)
        temp_layout.setContentsMargins(0,0,0,0)
        self.temp_widget = QtWidgets.QLabel("")
        self.temp_widget.setLayout(temp_layout)

        self.name_label = QtWidgets.QLabel(self.name)

        self.name_label.setMinimumWidth(30)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.orig_filepath_label = QtWidgets.QLabel(self._original_path)
        self.new_filepath_label = QtWidgets.QLineEdit("New FilePath")
        self.open_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")

    def create_connections(self):
        # self.select_cb.toggled.connect(lambda: self.cb_checked.emit())
        self.select_cb.toggled.connect(print)
        self.open_folder_btn.clicked.connect(self.open_file_menu)

    def change_bg_colour_selection(self, checked):
        palette = self.palette()
        if checked:
            print("checked")
            colour= QtGui.QColor(128, 128, 128)
        else:
            print("unchecked")
            colour= QtGui.QColor(255, 255, 255)
        palette.setColor(QtGui.QPalette.Window, colour)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_name_label_width(self, width):
        self.name_label.setFixedWidth(width)

    def set_orig_filepath_label_width(self, width):
        self.orig_filepath_label.setFixedWidth(width)

    def set_new_filepath_label_width(self, width):
        self.new_filepath_label.setFixedWidth(width)

    def open_file_menu(self):
        location = QtWidgets.QFileDialog.getOpenFileName()
        location = location[0]
        self.new_filepath_label.setText(location)
        return location

    def is_valid(self):
        info = QtCore.QFileInfo(self._original_path)
        if info.exists() and info.isFile():
            self._is_valid=True
        else:
            self._is_valid=False

        return self._is_valid

class TableWidget(QtWidgets.QTableWidget):

    def __init__(self):
        super().__init__()
        self.column_widths = [ 5, 100, 150, 150, 20]
        self.file_node_list = []
        self.current_row = 0

        self.setContentsMargins(120, 10, 10, 10)
        self.setColumnCount(5)
        self.setRowCount(0)
        self.setShowGrid(False)

        self.create_widgets()

    def create_widgets(self):


        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self)
        self.setHorizontalHeader(header_view)
        self.setHorizontalHeaderLabels(["", "Filename", "Orig", "new", "open"])
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        header_vertical_view = QtWidgets.QHeaderView(QtCore.Qt.Vertical, self)
        header_vertical_view.setHidden(True)
        self.setVerticalHeader(header_vertical_view)

        header_view_cb_temp_layout = QtWidgets.QHBoxLayout()
        temp_widget = QtWidgets.QWidget(self)
        temp_widget.setLayout(header_view_cb_temp_layout)
        self.header_cb = QtWidgets.QCheckBox()
        header_view_cb_temp_layout.addWidget(self.header_cb)
        header_view_cb_temp_layout.setAlignment(QtCore.Qt.AlignCenter)
        header_view_cb_temp_layout.setContentsMargins(12, 8, 0,0)
        self.header_cb.stateChanged.connect(self.select_all)

        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)


        # self.header_cb.setGeometry(QtCore.QRect(10, 0, 0, 0))

        for j in range(0, 5):
            self.setColumnWidth(j, self.column_widths[j])


    def add_row(self, name, original_path):
        self.setRowCount(self.current_row+1)
        widg = File_Node_Widget(name, original_path)

        self.file_node_list.append(widg)
        for j in range(0, 5):
            self.setItem(self.current_row, j, QtWidgets.QTableWidgetItem(" "))
            if widg.is_valid():
                self.item(self.current_row, j).setBackground(QtGui.QColor(0, 70, 0))
            else:
                self.item(self.current_row, j).setBackground(QtGui.QColor(70, 0, 0))

        self.setCellWidget(self.current_row, 0, widg.temp_widget)
        self.setCellWidget(self.current_row, 1, widg.name_label)
        self.setCellWidget(self.current_row, 2, widg.orig_filepath_label)
        self.setCellWidget(self.current_row, 3, widg.new_filepath_label)
        self.setCellWidget(self.current_row, 4, widg.open_folder_btn)
        self.current_row +=1
        # widg.cb_checked.connect(self.check_box_state_changed)

    def check_box_state_changed(self, *args):
        # for i in self.file_node_list:
        #     if i.select_cb.isChecked():
        #         print("checked")
        #     else:
        print(args)
        pass

    def select_all(self):
        if self.header_cb.isChecked():
            for each in self.file_node_list:
                each.select_cb.setChecked(True)
        else:
            for each in self.file_node_list:
                each.select_cb.setChecked(False)

    def clear_table(self):
        self.file_node_list = []
        self.current_row=0
        self.setRowCount(0)

class File_Repather_UI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    TITLE = "File Repather UI"
    UI_NAME = "FileRepatherUI"
    def __init__(self):
        super().__init__()
        self.setObjectName(File_Repather_UI.UI_NAME)
        self.setWindowTitle(File_Repather_UI.TITLE)
        self.setMinimumWidth(510)

        workspace_control_name = f"{File_Repather_UI.UI_NAME}WorkspaceControl"
        if cmds.workspaceControl(workspace_control_name, q=True, exists=True):
            workspace_control_pointer = int(omui.MQtUtil.findControl(workspace_control_name))
            widget_ptr = int(getCppPointer(self)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_pointer)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.maya_helpers = File_Repather()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()


    def create_widgets(self):

        self.directory_le = QtWidgets.QLineEdit()
        self.directory_le.setPlaceholderText("Directory to search for missing textures")
        self.directory_cb = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")

        self.directory_update_btn = QtWidgets.QPushButton("Update")
        self.directory_update_btn.setFixedWidth(60)
        self.directory_update_btn.setToolTip("Udpates the file paths with found textueres")


        self.table_widget = TableWidget()

        self.new_filepath_le = QtWidgets.QLineEdit()
        self.new_filepath_le.setPlaceholderText("Set Directory yo Copy or move to")

        self.open_new_filepath_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.update_filepaths_button =QtWidgets.QPushButton("Update Values")

        bottom_row_button_width = 60
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setFixedWidth(bottom_row_button_width)
        self.refresh_btn.setToolTip("Refreshes the List")
        self.copy_btn = QtWidgets.QPushButton("Copy")
        self.copy_btn.setFixedWidth(bottom_row_button_width)
        self.copy_btn.setToolTip("Copies the List to the project directory")
        self.move_btn = QtWidgets.QPushButton("Move")
        self.move_btn.setFixedWidth(bottom_row_button_width)
        self.move_btn.setToolTip("Copies the List to the project directory")
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setFixedWidth(bottom_row_button_width)
        self.close_btn.setToolTip("Closes the window")

    def create_layouts(self):

        directory_row = QtWidgets.QHBoxLayout()
        directory_row.addWidget(self.directory_le)
        directory_row.addWidget(self.directory_cb)
        directory_row.addWidget(self.directory_update_btn)
        options_layout = QtWidgets.QFormLayout()
        options_layout.addRow(QtWidgets.QLabel("Directory: "), directory_row)


        new_filepath_layoput =QtWidgets.QFormLayout()
        temp_filepath_layout = QtWidgets.QHBoxLayout()
        temp_filepath_layout.addWidget(self.new_filepath_le)
        temp_filepath_layout.addWidget(self.open_new_filepath_folder_btn)
        temp_filepath_layout.addWidget(self.update_filepaths_button)
        new_filepath_layoput.addRow("new File Direcory: ", temp_filepath_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.move_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(options_layout)
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(new_filepath_layoput)
        main_layout.addLayout(button_layout)


    def create_connections(self):
        self.directory_cb.clicked.connect(self.open_file_menu_directory)

        self.close_btn.clicked.connect(self.close)
        self.refresh_btn.clicked.connect(self.refresh)
        self.open_new_filepath_folder_btn.clicked.connect(self.open_file_menu_filepath)

        self.directory_update_btn.clicked.connect(self.update_directory_file_paths)
        self.directory_le.editingFinished.connect(self.update_directory_file_paths)

        self.new_filepath_le.editingFinished.connect(self.update_file_paths)



        self.copy_btn.clicked.connect(self.copy_textures)
        self.move_btn.clicked.connect(self.move_textures)

    def refresh(self):
        self.table_widget.clear_table()
        nodes = self.maya_helpers.get_file_nodes_in_scene()
        for node in nodes:
            # print(self.maya_helpers.get_filepath_attr(node) )
            self.table_widget.add_row(node,self.maya_helpers.get_filepath_attr(node) )

    def open_file_menu_filepath(self):
        location = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.new_filepath_le.setText(location)
        self.update_file_paths()
        return location

    def open_file_menu_directory(self):
        location = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.directory_le.setText(location)
        self.update_directory_file_paths()
        return location


    def change_table_widget_length(self, *args):
        print(args)

    def update_file_paths(self):
        text = self.new_filepath_le.text()
        for i in self.table_widget.file_node_list:
            i.new_filepath_label.setText(os.path.join(text, i.filename))


    def update_directory_file_paths(self):
        text = self.directory_le.text()

        for i in self.table_widget.file_node_list:
            new_filepath = self.maya_helpers.find_missing_textures(i.orig_filepath_label.text(), text)
            # i.new_filepath_label.setText(new_filepath)
            if new_filepath:
                # print(i.name+"."+new_filepath)
                if (i.is_valid):
                    self.maya_helpers.set_filepath_attr(i.name, new_filepath)
        self.refresh()

    def copy_textures(self):
        self.repath_texture(True)

    def move_textures(self):
        self.repath_texture(False)

    def repath_texture(self, copy=False):

        text = self.new_filepath_le.text()
        # print(text)
        info = QtCore.QFileInfo(text)
        for node in self.table_widget.file_node_list:
            new_dir = node.new_filepath_label.text()
            old_dir = node.orig_filepath_label.text()
            temp_old_dir = cp.deepcopy(old_dir)
            if copy:
                if node._is_valid:
                    if info.isDir():
                        self.maya_helpers.repath_files(node.name, old_dir, directory=new_dir, all_paths=False, copy_files=copy)
                    else:
                        self.maya_helpers.repath_files(node.name, old_dir,"", False, copy_files=copy)
            else:
                if node._is_valid:
                    if info.isDir():
                        self.maya_helpers.repath_files(node.name, old_dir, directory=new_dir, all_paths=False, copy_files=copy)
                    else:
                        self.maya_helpers.repath_files(node.name, old_dir,"", False, copy_files=copy)

            self.refresh()

try:
    if window and window.parent():
        workspace_control_name = window.parent().objectName()
        if cmds.window(workspace_control_name, exists=True):
            cmds.deleteUI(workspace_control_name)
except:
    pass

window = File_Repather_UI()
# DEelete late

window.refresh()
window.directory_le.setText(r"C:\Users\vboxuser\Desktop\BugsMaya\sourceimages")
window.new_filepath_le.setText(r"C:/Users/vboxuser/Desktop/BugsMaya/sourceimages/ee")
window.update_file_paths()



#  DE;ete LAter

ui_script = "from file_repather import File_Repather_UI\nwindow=File_Repather_UI"
window.show(dockable=True, uiScript=ui_script)

