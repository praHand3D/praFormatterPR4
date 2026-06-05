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
        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected:
            layout.label(text="No mesh selected", icon='INFO')
        else:
            for obj in selected:
                has_anim = obj.animation_data is not None and obj.animation_data.action is not None
                anim_tag = " (a)" if has_anim else ""
                row = layout.row()
                row.label(text=f"{obj.name}  ->  {obj.data.name}{anim_tag}")

        layout.separator()
        layout.operator("pr4.export", text="Export Selected", icon='EXPORT')
        layout.separator()
        layout.operator("pr4.import", text="Import .PR4", icon='IMPORT')