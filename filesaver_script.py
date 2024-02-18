import os.path
import sys
import glob
from  datetime import datetime
from PySide2 import QtGui, QtWidgets, QtCore
from maya import cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


class FileSaver(QtWidgets.QDialog):
    maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)


    def __init__(self):
        super().__init__(FileSaver.maya_main_window)
        self.setMinimumSize(300, 300)
        self.setObjectName("PolyCountCheckerGUI")
        self.setWindowTitle("File")
        self.setMinimumWidth(210)

        self.text = ""

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connection()

    def create_actions(self):
        self.menu_bar = QtWidgets.QMenuBar()
        # self.menu_bar.setFixedHeight(20)
        # self.menu_bar.setContentsMargins(1,1,1,1)
        # palette = QtGui.QPalette()
        # palette.setColor(self.menu_bar, QtGui.QColor(1, 1, 1))
        # self.menu_bar.setAutoFillBackground(True)
        # self.menu_bar.setPalette(palette)
        # self.setB


        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.addAction("Action 1")
        self.file_menu.addAction("Action 2")

        self.help_menu = QtWidgets.QMenu("Help")
        self.help_menu.addAction("Action 1")
        self.help_menu.addAction("Action 2")

        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.help_menu)
    def create_widgets(self):


        self.artist_name_le = QtWidgets.QLineEdit("Rohan")
        self.artist_name_le.setToolTip("Set Artist Name")
        self.artist_name_le.setPlaceholderText("Artist Name")

        self.directory_le = QtWidgets.QLineEdit(r"C:/Users/vboxuser/Desktop/test3")
        self.directory_le.setPlaceholderText("Directory to save files ")
        self.directory_cb = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")



        self.studio_name_le = QtWidgets.QLineEdit("StC")
        self.studio_name_le.setToolTip("Set Studio Name")
        self.studio_name_le.setPlaceholderText("Studio Name")

        self.project_name_le = QtWidgets.QLineEdit("ALN")
        self.project_name_le.setToolTip("Set Project Name")
        self.project_name_le.setPlaceholderText("Project Name")

        self.shot_name_le = QtWidgets.QLineEdit("Shot_001")
        self.shot_name_le.setToolTip("Set Shot Name")
        self.shot_name_le.setPlaceholderText("Shot Name")

        self.department_cmb = QtWidgets.QComboBox()

        self.department_cmb.addItem("Rigging")
        self.department_cmb.addItem("Animation")
        self.department_cmb.addItem("Modelling")
        self.department_cmb.addItem("Lighting")
        self.department_cmb.addItem("Rendering")
        self.department_cmb.addItem("FX")
        self.department_cmb.setFixedWidth(100)

        self.status_cmb = QtWidgets.QComboBox()

        self.status_cmb.addItem("WIP")
        self.status_cmb.addItem("QC")
        self.status_cmb.addItem("Final")
        self.status_cmb.setFixedWidth(100)


        self.message_comment_box = QtWidgets.QTextEdit()
        self.message_comment_box.setPlaceholderText("Notes")
        self.message_comment_box.setToolTip("Enter notes here.")

        self.update_note_button = QtWidgets.QPushButton("Update Note")
        self.export_button = QtWidgets.QPushButton("Export")

    def create_layouts(self):

        directory_layout = QtWidgets.QHBoxLayout()
        directory_layout.addWidget(self.directory_le)
        directory_layout.addWidget(self.directory_cb)

        options_layout = QtWidgets.QFormLayout()
        options_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        options_layout.addRow("Artist Name: ", self.artist_name_le)
        options_layout.addRow("Studio Name: ", self.studio_name_le)
        options_layout.addRow("Project Name: ", self.project_name_le)
        options_layout.addRow("Shot Name: ", self.shot_name_le)
        options_layout.addRow("Department: ", self.department_cmb)
        options_layout.addRow("Status: ", self.status_cmb)

        export_layout = QtWidgets.QHBoxLayout()
        # export_layout.addWidget(self.update_note_button)
        export_layout.addStretch()
        export_layout.addWidget(self.export_button)

        body_layout = QtWidgets.QVBoxLayout()

        body_layout.addLayout(directory_layout)
        body_layout.addLayout(directory_layout)
        body_layout.addLayout(options_layout)
        body_layout.addWidget(self.message_comment_box)
        body_layout.addLayout(export_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4,4,4,4)
        main_layout.addWidget(self.menu_bar)
        main_layout.addLayout(body_layout)


    def create_connection(self):
        self.directory_cb.clicked.connect(self.open_file_menu_directory)

        self.update_note_button.clicked.connect(self.update_notebox)
        self.export_button.clicked.connect(self.save_file)

    def create_path(self):
        base_directory = self.directory_le.text()
        studio = self.studio_name_le.text()
        project = self.project_name_le.text()
        shot = self.shot_name_le.text()
        department = self.department_cmb.currentText()
        status = self.status_cmb.currentText()

        filename = f"{studio}_{project}_{shot}_{department}_{status}"
        path = f"{base_directory}/{status}/{filename}"
        return path

    def open_file_menu_directory(self):
        location = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.directory_le.setText(location)
        return location

    def update_notebox(self):
        bars = "***********************************"

        studio = self.studio_name_le.text()
        project = self.project_name_le.text()
        shot = self.shot_name_le.text()
        department = self.department_cmb.currentText()
        status = self.status_cmb.currentText()
        artist = self.artist_name_le.text()
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S, %d %B %Y")
        text = self.message_comment_box.toPlainText()

        extra = ""
        if status == "QC" or status == "Final":
            extra = f"Original FilePath: {cmds.file(expandName=True, q=True)}"


        text = f"{bars}\n" \
                   f"{studio} - {project}   " \
                   f"Shot: {shot} \n" \
                   f"Department: {department}  \n" \
                   f"Artist: {artist}  \n" \
                   f"Status: {status}  \n" \
                   f"{bars}\n\n" \
                   f"{text}\n\n\n" \
                   f"{extra}\n\n" \
                   f"Time Saved: {formatted_time}\n" \
                   f"{bars}"
        self.text = text
        return

    def update_file_paths(self):

        path = self.create_path()
        file_directory = path.split("/")
        filename = file_directory[-1]
        self.base_directory = "/".join(file_directory[:-2])
        self.file_directory = "/".join(file_directory[:-1])
        version = 1
        while True:
            text_file_path = self.file_directory + "/" + filename + "_v" + f"{version:04d}" +".txt"
            if not os.path.isfile(text_file_path):
                self.text_file_path = text_file_path
                break
            else:
                version += 1

        self.maya_file_path = self.file_directory + "/" + filename + "_v" + f"{version:04d}" + ".ma"


    def write_text_file(self, text):

        print(self.file_directory)
        if os.path.isdir(self.base_directory):
            # print("scucces")
            if not os.path.isdir(self.file_directory):
                os.makedirs(self.file_directory)
            #
            # print(filename)
            with open(self.text_file_path, "w") as file:
                file.write(text)

    def save_maya_file(self):
        cmds.file(rename=self.maya_file_path)
        cmds.file(save=True, type='mayaAscii')

    def save_file(self):
        self.update_file_paths()
        self.update_notebox()
        self.set_asset_note()
        self.write_text_file(self.text)
        self.save_maya_file()

    def set_asset_note(self):
        assemblies = cmds.ls(assemblies=True)
        print(f"Assemblies: {assemblies}")
        print(self.text)
        if "Asset" in assemblies:
            print("success")
            cmds.setAttr(f"Asset.notes", self.text, type="string")


if __name__ == "__main__":

    try:
        FileSaver_UI_dialog.close()  # pylint: disable=E0601
        FileSaver_UI_dialog.deleteLater()

    except:
        pass

    # cmds.file(r"C:/Users/vboxuser/Desktop/BugsMaya/scenes/testScene.mb", o=True, force=True)

    FileSaver_UI_dialog = FileSaver()
    FileSaver_UI_dialog.show()