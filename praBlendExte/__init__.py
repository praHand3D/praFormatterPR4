import bpy
from . import panel

def register():
    bpy.utils.register_class(panel.PR4_PT_Panel)

def unregister():
    bpy.utils.unregister_class(panel.PR4_PT_Panel)

bl_info = {
    "name": "praHand3D .PR4 Format",
    "author": "oliwiawaszczuk",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > N Panel > PR4",
    "description": "Export and import .PR4 files",
    "category": "Import-Export",
}

def register():
    bpy.utils.register_class(panel.PR4_PT_Panel)

def unregister():
    bpy.utils.unregister_class(panel.PR4_PT_Panel)
