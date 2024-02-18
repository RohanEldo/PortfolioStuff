# PortfolioStuff

VDB Importer
Problem:
Manually importing smoke VDBs with multiple version names is a time-consuming process. It requires the user to create an aiVolume, select the file path, and set the vel field if it exists. Additionally, creating the shader involves manually creating a material and connecting it to a shader's volume_out in the Hypershade. If there are multiple separate smoke/pyro simulations, the user needs to manually redo each step, which is inefficient.

Solution:
The tool simplifies the process by allowing the user to input a directory. It then scans through the subfolders, identifies files with similar names (except for the last 8 digits), and adds the first frame to a list. Subsequently, it automatically creates an aiVolume, sets the file path, generates a material based on the volume's name, and applies it to the aiVolume. Additionally, the tool provides functionality to select objects and create a new shader for each one with the same name.

---

File Repather
Problem it Solves:
When collaborating on freelance projects with individuals using different folder structures, inconsistent file paths can lead to issues when transferring projects between computers. The default file path editor in Maya only changes the path in the file node, making it incompatible with other systems. This necessitates manual effort to locate missing files and copy them.
Solution:
The tool features a table displaying file_node_name, original file path, new file path, a button to open the file directory, and a checkbox to select files for repathing. It refreshes automatically when the window is shown or the refresh button is pressed. Upon setting the directory, clicking the update button finds filenames in the directory or its subfolders and sets the node's filepath attribute to the new found filepath. Users can set the new file directory using the line edit and buttons for copying or moving files.

---
Polycount Visualizer
Problem:
It's challenging to visually identify individual geometries exceeding certain poly count limits.
Solution:
The tool provides intSliderGrps to set limits for vertices, quads, edges, and triangles. It displays every geometry and its polycounts in a table where cells turn red if they exceed the limit. Users can visualize whether geometries are over or under the limit using temporary render layers, which are deleted upon closing the window.

---

File Saver
Problem: 
Saving files with appropriate filenames and information can be cumbersome.
Solution:
The tool includes line edits for Artist Name, Studio Name, Project Name, and Shot Name, along with comboboxes for department and rigging. There's also a line edit for the location, defaulted to project/scenes. Upon pressing the export button, the tool saves the file with a name incorporating the input labels, alongside creating a text file in that directory with all the info and save time. Notes written in the textEdit are saved as a note in the text file. If there's a group called Asset in the scene's root, its notes are updated with all the info. If the Status is set to QC or Final, the original path of the currently saved file is saved in the text file and the asset notes. If the file is saved again without changes in location or status, the file number is automatically incremented, and the info is appended to the text file.

---
Material Importer
Problem:
Substance importer can only import one material's textures at a time.
Solution:
The tool provides a configuration combobox to select which shader to use (currently only Arnold Standard Surface is complete). Users can input material suffix patterns in line edits (e.g., XYZ_normal.exr). A tree widget displays materials and imported textures. Buttons allow users to add or remove items from the tree widget. Adding an item opens the Maya file window where users can select .png, .jpeg, .tiff files. Selected filenames with the same name but different suffixes are added into the same materials. Line edits for adding prefixes or suffixes for materials are also provided. Once set, the tool creates materials, imports texture files, and connects them to the material. Additionally, it sets the texture file nodes' color mode (e.g., Base_Color is set to sRGB, roughness to RAW).
