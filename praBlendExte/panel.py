import bpy


class PR4_PT_Panel(bpy.types.Panel):
    bl_label = "PR4 Exporter"
    bl_idname = "PR4_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PR4'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Selected objects:")

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                has_anim = obj.animation_data is not None and obj.animation_data.action is not None
                row = layout.row()
                row.label(text=f"{obj.name} {'[ANIM]' if has_anim else ''}")
