bl_info = {
    "name": "praHand3D .PR4 Format",
    "author": "oliwiawaszczuk",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > N Panel > PR4",
    "description": "Export and import .PR4 files",
    "category": "Import-Export",
}

import bpy
from . import export
from . import _import
from . import panel


def register():
    bpy.utils.register_class(panel.PR4_PT_Panel)
    bpy.utils.register_class(export.PR4_OT_Export)
    bpy.utils.register_class(_import.PR4_OT_Import)
    bpy.types.TOPBAR_MT_file_export.append(export.menu_export)
    bpy.types.TOPBAR_MT_file_import.append(_import.menu_import)

def unregister():
    bpy.utils.unregister_class(panel.PR4_PT_Panel)
    bpy.utils.unregister_class(export.PR4_OT_Export)
    bpy.utils.unregister_class(_import.PR4_OT_Import)
    bpy.types.TOPBAR_MT_file_export.remove(export.menu_export)
    bpy.types.TOPBAR_MT_file_import.remove(_import.menu_import)