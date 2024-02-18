from functools import partial

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.mel as mel
import maya.app.renderSetup.model.renderLayer as renderLayer


class CustomMayaSlider(QtWidgets.QWidget):


    valueChanged = QtCore.Signal(int)

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("CustomSliderSpinbox")
        self.title = "title"
        self.create_control()
        self.set_size(50, 14)
        # self.change_bg_colour_selection()

    def change_bg_colour_selection(self):
        palette = self.palette()
        colour= QtGui.QColor(128, 128, 128)
        palette.setColor(QtGui.QPalette.Window, colour)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def create_control(self):
        window = cmds.window()
        value_slider_name = cmds.intSliderGrp(field=True, minValue=0, fieldMaxValue=999999999, cw2=[30, 300])


        self._value_slider_obj = omui.MQtUtil.findControl(value_slider_name)
        if self._value_slider_obj:
            self._value_slider_widget = wrapInstance(int(self._value_slider_obj), QtWidgets.QWidget)



            self._slider_widget  =self._value_slider_widget.findChild(QtWidgets.QWidget, "slider")
            self._spin_box_widget = self._value_slider_widget.findChild(QtWidgets.QWidget, "field")
            self._label_box_widget = self._value_slider_widget.findChild(QtWidgets.QWidget, "label")
            # self._label_box_widget.setFixedSize(10, 10)
            # Reparent the slider to the widget

            main_layout =QtWidgets.QHBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0,0,0,0)
            main_layout.addWidget(self._value_slider_widget)
            # main_layout.addWidget(self._spin_box_widget)
            # main_layout.addWidget(self._slider_widget)
            print(self._label_box_widget)
            # x = QtWidgets.QLabel()
            # x.setFixedSize(10, 10)

            cmds.intSliderGrp(self.get_full_name(), edit=True, changeCommand=partial(self.on_value_changed))
        # Delete mel window
        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(int(self._value_slider_obj))

    def set_size(self, width, height):
        # self._slider_widget.set(height)
        pass

    def set_value(self, value):
        value = int(value)
        cmds.intSliderGrp(self.get_full_name(), e=True, value=value)
        self.on_value_changed()

    def get_value(self):
        value = cmds.intSliderGrp(self.get_full_name(), q=True, value=True)
        return int(value)



    def on_value_changed(self, *args):
        self.valueChanged.emit(self.get_value())


class RenderLayerHelpers:
# Helper function for creating a shader

    def __init__(self):
        self.rs = renderSetup.instance()

        # Create and append the render layer
        self.green_shader, self.green_shading_grp = self.createShader("surfaceShader")
        self.green_shader = cmds.rename(self.green_shader, "green_shader")
        self.red_shader, self.red_shading_grp = self.createShader("surfaceShader")
        self.red_shader = cmds.rename(self.red_shader, "red_shader")

        self.setColor(self.green_shader + ".outColor", [0.0, 1.0, 0.0])
        self.setColor(self.red_shader + ".outColor", [1.0, 0.0, 0.0])

        self.create_vertex_layer()

    def createShader(self, shaderType):
        shaderName = cmds.shadingNode(shaderType, asShader=True)
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=(shaderName + "SG"))
        cmds.connectAttr(shaderName + ".outColor", shading_group + ".surfaceShader")
        return (shaderName, shading_group)


    # Helper function for assigning a material
    def assignMaterial(self, shapeName, shadingGroupName):
        cmds.sets(shapeName, forceElement=shadingGroupName)


    # Helper function for setting a color attribute to some color value
    def setColor(self, attr, color):
        cmds.setAttr(attr, color[0], color[1], color[2], type="float3")


    def create_vertex_layer(self):
        self.vertex_layer = self.rs.createRenderLayer("PolyCountVisualisation")

        self.valid_vertex_geos_collection = self.vertex_layer.createCollection("valid")
        self.invalid_vertex_geos_collection = self.vertex_layer.createCollection("invalid")

        self.valid_vertex_geos_collection.createOverride("valid_obj_mat", renderSetup.typeIDs.materialOverride)
        self.invalid_vertex_geos_collection.createOverride("invalid_obj_mat", renderSetup.typeIDs.materialOverride)

        cmds.defaultNavigation(ce=True, s="green_shader", d="valid_obj_mat.attrValue")
        cmds.defaultNavigation(ce=True, s="red_shader", d="invalid_obj_mat.attrValue")

    def set_vertex_layer(self, valid_nodes, invalid_nodes):
        valid_pattern = " ".join(valid_nodes)
        self.valid_vertex_geos_collection.getSelector().setPattern(valid_pattern)

        invalid_pattern = " ".join(invalid_nodes)
        self.invalid_vertex_geos_collection.getSelector().setPattern(invalid_pattern)
        self.rs.switchToLayer(self.vertex_layer)

    def delete_visibility_layer(self):
        # print(self.vertex_layer)
        self.rs.switchToLayer(self.rs.getDefaultRenderLayer())
        self.rs.detachRenderLayer(self.vertex_layer)
        renderLayer.delete(self.vertex_layer)



class PolyCountHelpers:

    @classmethod
    def get_selected_nodes(cls):
        selected_nodes = cmds.ls(sl=True)
        if not selected_nodes:
            selected_nodes = cmds.ls(geometry=True)
        return selected_nodes

    @classmethod
    def get_polycount(cls, node):
        vertices = cmds.polyEvaluate(node, vertex=True)
        edges = cmds.polyEvaluate(node, edge=True)
        faces = cmds.polyEvaluate(node, face=True)
        triangles = cmds.polyEvaluate(node, triangle=True)

        return vertices, edges, triangles, faces
    #
    # @classmethod
    # def create_render_layers(cls):
    #     cmds.createRenderLayer("vertex_poly_count")
    #     cmds.createRenderLayer("quad_poly_count")
    #     cmds.createRenderLayer("edge_poly_count")
    #     cmds.createRenderLayer("tris_poly_count")


class TableWidget(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()

        self.vertex_limit = 0
        self.edge_limit = 0
        self.tris_limit = 0
        self.quad_limit = 0

        self.vertex_nodes_valid = []
        self.vertex_nodes_invalid = []

        self.edge_nodes_valid = []
        self.edge_nodes_invalid = []

        self.tris_nodes_valid = []
        self.tris_nodes_invalid = []

        self.quad_nodes_valid = []
        self.quad_nodes_invalid = []

        self.column_width = 50

        self.node_list = []
        self.current_row = 0

        self.create_widgets()



    def create_widgets(self):
        self.setColumnCount(5)
        # self.setRowCount(0)

        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self)
        self.setHorizontalHeader(header_view)
        self.setHorizontalHeaderLabels(["Name", "Vertices", "Edges", "Tris", "Quads"])
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)

        self.setColumnWidth(1, self.column_width)
        self.setColumnWidth(2, self.column_width)
        self.setColumnWidth(3, self.column_width)
        self.setColumnWidth(4, self.column_width)
        #
        # for i  in range(5):
        #     for j in range(5):
        #         self.setItem(i, j, QtWidgets.QTableWidgetItem(f"{i}:{j}"))

        # self.setHorizontalHeaderLabels(["", "file", "orig", "new", "open"])

    def add_row(self, node):
        values = PolyCountHelpers.get_polycount(node)
        # print(values)
        self.setRowCount(self.current_row + 1)

        name_item = QtWidgets.QTableWidgetItem(f"{node}")
        name_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(self.current_row, 0, name_item)

        vertex_item = QtWidgets.QTableWidgetItem(f"{values[0]}")
        vertex_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(self.current_row, 1, vertex_item)

        edge_item = QtWidgets.QTableWidgetItem(f"{values[1]}")
        edge_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(self.current_row, 2, edge_item)

        tris_item = QtWidgets.QTableWidgetItem(f"{values[2]}")
        tris_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(self.current_row, 3, tris_item)

        quad_item = QtWidgets.QTableWidgetItem(f"{values[3]}")
        quad_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setItem(self.current_row, 4, quad_item)
        self.current_row += 1


    def clear_table(self):
        self.file_node_list = []
        self.current_row = 0
        self.setRowCount(0)

    def change_colour(self, index: int, valid_nodes_list: list, invalid_nodes_list: list, limit: int):
        for i in range(self.current_row):
            name = cmds.listRelatives(self.item(i, 0).text(), parent=True)[0]
            # print(f"parent = {name}")
            if int(self.item(i, index).text()) < limit:
                self.item(i, index).setBackground(QtGui.QColor(43, 43, 43))
                if name not in valid_nodes_list:
                    valid_nodes_list.append(name)
                if name in invalid_nodes_list:
                    invalid_nodes_list.remove(name)

            else:
                self.item(i, index).setBackground(QtGui.QColor(100, 0, 0))
                if name in valid_nodes_list:
                    valid_nodes_list.remove(name)
                if name not in invalid_nodes_list:
                    invalid_nodes_list.append(name)


    def change_colour_vertex(self):
        self.change_colour(1, self.vertex_nodes_valid, self.vertex_nodes_invalid, self.vertex_limit)

    def change_colour_edge(self):
        self.change_colour(2, self.edge_nodes_valid, self.edge_nodes_invalid, self.edge_limit)

    def change_colour_tris(self):
        self.change_colour(3, self.tris_nodes_valid, self.tris_nodes_invalid, self.tris_limit)
    def change_colour_quads(self):
        self.change_colour(4, self.quad_nodes_valid, self.quad_nodes_invalid, self.quad_limit)

    def set_vertex_limit(self, limit):
        self.vertex_limit = int(limit)

    def set_edge_limit(self, limit):
        self.edge_limit = int(limit)

    def set_quad_limit(self, limit):
        self.quad_limit = int(limit)

    def set_tris_limit(self, limit):
        self.tris_limit = int(limit)

    def select_item(self):
        print("")

class PolyCountVisualiser_UI(QtWidgets.QDialog):
    TITLE = "Poly Count Visualiser UI"


    def __init__(self):
        maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        super().__init__(maya_main_window)

        self.setObjectName("PolyCountCheckerGUI")


        self.setWindowTitle(PolyCountVisualiser_UI.TITLE)
        self.setMinimumWidth(210)
        #
        self.render_layer_helper = RenderLayerHelpers()
        cmds.select(clear=True)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.load_option_variables()

        self.refresh()

    def load_option_variables(self):
        if cmds.optionVar(exists="polyCountChecker_Vertex_Limit"):
            value = cmds.optionVar(q="polyCountChecker_Vertex_Limit")
            self.table_widget.set_vertex_limit(value)
            self.vertex_limit_sb.set_value(value)

        if cmds.optionVar(exists="polyCountChecker_Edge_Limit"):
            value = cmds.optionVar(q="polyCountChecker_Edge_Limit")
            self.table_widget.set_edge_limit(value)
            self.edge_limit_sb.set_value(value)

        if cmds.optionVar(exists="polyCountChecker_Tri_Limit"):
            value = cmds.optionVar(q="polyCountChecker_Tri_Limit")
            self.table_widget.set_tris_limit(value)
            self.tris_limit_sb.set_value(value)

        if cmds.optionVar(exists="polyCountChecker_Quad_Limit"):
            value = cmds.optionVar(q="polyCountChecker_Quad_Limit")
            self.table_widget.set_quad_limit(value)
            self.quad_limit_sb.set_value(value)

    def create_widgets(self):
        self.vertex_limit_label = QtWidgets.QLabel("Vertex Limit")
        self.vertex_limit_label.setFixedWidth(80)
        self.edge_limit_label = QtWidgets.QLabel("Edge Limit")
        self.edge_limit_label.setFixedWidth(80)
        self.tri_limit_label = QtWidgets.QLabel("Triangles Limit")
        self.tri_limit_label.setFixedWidth(80)
        self.quad_limit_label = QtWidgets.QLabel("Quads Limit")
        self.quad_limit_label.setFixedWidth(80)

        self.vertex_limit_sb = CustomMayaSlider()
        self.edge_limit_sb = CustomMayaSlider()
        self.tris_limit_sb = CustomMayaSlider()
        self.quad_limit_sb = CustomMayaSlider()

        self.table_widget = TableWidget()

        self.vertex_btn = QtWidgets.QPushButton("Vertex")
        self.edge_btn = QtWidgets.QPushButton("Edge")
        self.tris_btn = QtWidgets.QPushButton("Triangles")
        self.quad_btn = QtWidgets.QPushButton("Quads")

        self.refresh_button = QtWidgets.QPushButton("Refresh")

    def create_layouts(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.vertex_btn)
        button_layout.addWidget(self.edge_btn)
        button_layout.addWidget(self.tris_btn)
        button_layout.addWidget(self.quad_btn)


        row_layout =QtWidgets.QVBoxLayout()

        vertex_limit_layout = QtWidgets.QHBoxLayout()
        vertex_limit_layout.addWidget(self.vertex_limit_label)
        vertex_limit_layout.addWidget(self.vertex_limit_sb)

        edge_limit_layout = QtWidgets.QHBoxLayout()
        edge_limit_layout.addWidget(self.edge_limit_label)
        edge_limit_layout.addWidget(self.edge_limit_sb)

        tri_limit_layout = QtWidgets.QHBoxLayout()
        tri_limit_layout.addWidget(self.tri_limit_label)
        tri_limit_layout.addWidget(self.tris_limit_sb)

        quad_limit_layout = QtWidgets.QHBoxLayout()
        quad_limit_layout.addWidget(self.quad_limit_label)
        quad_limit_layout.addWidget(self.quad_limit_sb)

        row_layout.addLayout(vertex_limit_layout)
        row_layout.addLayout(edge_limit_layout)
        row_layout.addLayout(tri_limit_layout)
        row_layout.addLayout(quad_limit_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(row_layout)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(QtWidgets.QLabel("Visualise"))
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.refresh_button)

    def create_connections(self):
        self.vertex_limit_sb.valueChanged.connect(self.vertex_limit_changed)
        self.edge_limit_sb.valueChanged.connect(self.edge_limit_changed)
        self.tris_limit_sb.valueChanged.connect(self.tris_limit_changed)
        self.quad_limit_sb.valueChanged.connect(self.quad_limit_changed)

        self.table_widget.itemClicked.connect(self.item_clicked)

        self.vertex_btn.clicked.connect(self.vertex_visualisation)
        self.edge_btn.clicked.connect(self.edge_visualisation)
        self.tris_btn.clicked.connect(self.tris_visualisation)
        self.quad_btn.clicked.connect(self.quad_visualisation)

        self.refresh_button.clicked.connect(self.refresh)

    def item_clicked(self,  item):
        row = self.table_widget.indexFromItem(item).row()
        geo = self.table_widget.item(row, 0).text()
        cmds.select(cmds.listRelatives(geo, parent=True)[0])

    def refresh(self):
        self.table_widget.clear_table()
        nodes = PolyCountHelpers.get_selected_nodes()
        # print(nodes)
        # print(self.table_widget.vertex_nodes_valid)
        # print(self.table_widget.vertex_nodes_invalid)
        for node in nodes:
            self.table_widget.add_row(node)

        self.vertex_limit_changed(self.vertex_limit_sb.get_value())
        self.edge_limit_changed(self.edge_limit_sb.get_value())
        self.tris_limit_changed(self.tris_limit_sb.get_value())
        self.quad_limit_changed(self.quad_limit_sb.get_value())

    def vertex_visualisation(self):
        self.render_layer_helper.set_vertex_layer(self.table_widget.vertex_nodes_valid, self.table_widget.vertex_nodes_invalid)

    def edge_visualisation(self):
        self.render_layer_helper.set_vertex_layer(self.table_widget.edge_nodes_valid, self.table_widget.edge_nodes_invalid)

    def tris_visualisation(self):
        self.render_layer_helper.set_vertex_layer(self.table_widget.tris_nodes_valid, self.table_widget.tris_nodes_invalid)

    def quad_visualisation(self):
        self.render_layer_helper.set_vertex_layer(self.table_widget.quad_nodes_valid, self.table_widget.quad_nodes_invalid)

    def vertex_limit_changed(self, limit):
        cmds.optionVar(iv=("polyCountChecker_Vertex_Limit", limit))
        self.table_widget.set_vertex_limit(limit)
        self.table_widget.change_colour_vertex()

    def edge_limit_changed(self, limit):
        cmds.optionVar(iv=("polyCountChecker_Edge_Limit", limit))
        self.table_widget.set_edge_limit(limit)
        self.table_widget.change_colour_edge()

    def tris_limit_changed(self, limit):
        cmds.optionVar(iv=("polyCountChecker_Tri_Limit", limit))
        self.table_widget.set_tris_limit(limit)
        self.table_widget.change_colour_tris()

    def quad_limit_changed(self, limit):
        cmds.optionVar(iv=("polyCountChecker_Quad_Limit", limit))
        self.table_widget.set_quad_limit(limit)
        self.table_widget.change_colour_quads()

    def closeEvent(self, event):
        super().closeEvent(event)
        # # mel.eval('catchQuiet( delete("rs_PolyCountVisualisation") );')
        # mel.eval('MLdeleteUnused;')
        # mel.eval('delete("rs_PolyCountVisualisation");')
        self.render_layer_helper.delete_visibility_layer()


if __name__ == "__main__":

    try:
        PolyCountVisualiser_UI_dialog.close()  # pylint: disable=E0601
        PolyCountVisualiser_UI_dialog.deleteLater()
    except:
        pass

    cmds.file(r"C:/Users/vboxuser/Desktop/BugsMaya/scenes/testScene.mb", o=True, force=True)

    PolyCountVisualiser_UI_dialog = PolyCountVisualiser_UI()
    PolyCountVisualiser_UI_dialog.show()
