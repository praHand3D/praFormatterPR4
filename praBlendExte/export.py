import bpy
import bmesh
import struct
from bpy_extras.io_utils import ExportHelper
from config import MAGIC_CODE, VERSION


def get_keyframe_frames(obj):
    frames = set()
    action = obj.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                for fcurve in channelbag.fcurves:
                    for kp in fcurve.keyframe_points:
                        frames.add(int(kp.co[0]))
    return sorted(frames)


def get_animation_keyframes(obj):
    frames = get_keyframe_frames(obj)
    keyframes = []
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        loc = obj.location.copy()
        rot = obj.rotation_quaternion.copy()
        scale = obj.scale.copy()
        keyframes.append((loc, rot, scale))
    return keyframes


def export(path: str):
    objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

    if not objects:
        return 0

    exported_meshes = {}
    for obj in objects:
        if obj.data not in exported_meshes:
            exported_meshes[obj.data] = len(exported_meshes)

    anim_count = sum(1 for obj in objects if obj.animation_data and obj.animation_data.action)

    with open(path, "wb") as f:
        f.write(MAGIC_CODE.encode('ascii'))
        f.write(struct.pack("B", VERSION))
        f.write(struct.pack("B", len(exported_meshes)))
        f.write(struct.pack("B", len(objects)))
        f.write(struct.pack("B", anim_count))

        for mesh_data, mesh_id in exported_meshes.items():
            bm = bmesh.new()
            bm.from_mesh(mesh_data)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            f.write(struct.pack("B", mesh_id))
            f.write(struct.pack("H", len(mesh_data.vertices)))
            f.write(struct.pack("H", len(bm.faces)))

            for v in mesh_data.vertices:
                f.write(struct.pack("f", v.co.x))
                f.write(struct.pack("f", v.co.z))
                f.write(struct.pack("f", v.co.y))

            for face in bm.faces:
                indices = [v.index for v in face.verts]
                f.write(struct.pack("H", indices[0]))
                f.write(struct.pack("H", indices[1]))
                f.write(struct.pack("H", indices[2]))

            bm.free()

        for obj_id, obj in enumerate(objects):
            mesh_ref = exported_meshes[obj.data]
            position = obj.location
            rot = obj.rotation_quaternion
            scale = obj.scale

            f.write(struct.pack("B", obj_id))
            f.write(struct.pack("B", mesh_ref))
            f.write(struct.pack("f", position.x))
            f.write(struct.pack("f", position.z))
            f.write(struct.pack("f", position.y))
            f.write(struct.pack("f", rot.x))
            f.write(struct.pack("f", rot.z))
            f.write(struct.pack("f", rot.y))
            f.write(struct.pack("f", rot.w))
            f.write(struct.pack("f", scale.x))
            f.write(struct.pack("f", scale.z))
            f.write(struct.pack("f", scale.y))

        for obj_id, obj in enumerate(objects):
            if obj.animation_data is None or obj.animation_data.action is None:
                continue

            keyframes = get_animation_keyframes(obj)

            f.write(struct.pack("B", obj_id))
            f.write(struct.pack("B", obj_id))
            f.write(struct.pack("B", 24))
            f.write(struct.pack("H", len(keyframes)))

            for loc, rot, scale in keyframes:
                f.write(struct.pack("f", loc.x))
                f.write(struct.pack("f", loc.z))
                f.write(struct.pack("f", loc.y))
                f.write(struct.pack("f", rot.x))
                f.write(struct.pack("f", rot.z))
                f.write(struct.pack("f", rot.y))
                f.write(struct.pack("f", rot.w))
                f.write(struct.pack("f", scale.x))
                f.write(struct.pack("f", scale.z))
                f.write(struct.pack("f", scale.y))

    return len(objects)


class PR4_OT_Export(bpy.types.Operator, ExportHelper):
    bl_idname = "pr4.export"
    bl_label = "Export .PR4"
    filename_ext = ".PR4"

    def execute(self, context):
        count = export(self.filepath)
        if count == 0:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Exported {count} object(s) to {self.filepath}")
        return {'FINISHED'}


def menu_export(self, context):
    self.layout.operator(PR4_OT_Export.bl_idname, text="praHand3D (.PR4)")