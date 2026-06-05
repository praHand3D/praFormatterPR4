import bpy
import bmesh
import struct
import os
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

    # znajdz unikalne meshe
    exported_meshes = {}
    for obj in objects:
        if obj.data not in exported_meshes:
            exported_meshes[obj.data] = len(exported_meshes)

    anim_count = sum(1 for obj in objects if obj.animation_data and obj.animation_data.action)

    with open(path, "wb") as f:

        # HEADER
        f.write(MAGIC_CODE.encode('ascii'))
        f.write(struct.pack("B", VERSION))
        f.write(struct.pack("B", len(exported_meshes)))  # mesh_count
        f.write(struct.pack("B", len(objects)))          # object_count
        f.write(struct.pack("B", anim_count))            # animation_count

        # MESHES - tylko unikalne
        for mesh_data, mesh_id in exported_meshes.items():
            bm = bmesh.new()
            bm.from_mesh(mesh_data)
            bmesh.ops.triangulate(bm, faces=bm.faces)

            f.write(struct.pack("B", mesh_id))
            f.write(struct.pack("H", len(mesh_data.vertices)))
            f.write(struct.pack("H", len(bm.faces)))

            for v in mesh_data.vertices:
                f.write(struct.pack("f", v.co.x))
                f.write(struct.pack("f", v.co.y))
                f.write(struct.pack("f", v.co.z))

            for face in bm.faces:
                indices = [v.index for v in face.verts]
                f.write(struct.pack("H", indices[0]))
                f.write(struct.pack("H", indices[1]))
                f.write(struct.pack("H", indices[2]))

            bm.free()

        # OBJECTS
        for obj_id, obj in enumerate(objects):
            mesh_ref = exported_meshes[obj.data]
            position = obj.location
            rot = obj.rotation_quaternion
            scale = obj.scale

            f.write(struct.pack("B", obj_id))
            f.write(struct.pack("B", mesh_ref))

            f.write(struct.pack("f", position.x))
            f.write(struct.pack("f", position.y))
            f.write(struct.pack("f", position.z))

            f.write(struct.pack("f", rot.x))
            f.write(struct.pack("f", rot.y))
            f.write(struct.pack("f", rot.z))
            f.write(struct.pack("f", rot.w))

            f.write(struct.pack("f", scale.x))
            f.write(struct.pack("f", scale.y))
            f.write(struct.pack("f", scale.z))

        # ANIMATIONS
        for obj_id, obj in enumerate(objects):
            if obj.animation_data is None or obj.animation_data.action is None:
                continue

            keyframes = get_animation_keyframes(obj)

            f.write(struct.pack("B", obj_id))         # animation_id
            f.write(struct.pack("B", obj_id))         # object_ref
            f.write(struct.pack("B", 24))             # fps
            f.write(struct.pack("H", len(keyframes))) # keyframe_count

            for loc, rot, scale in keyframes:
                f.write(struct.pack("f", loc.x))
                f.write(struct.pack("f", loc.y))
                f.write(struct.pack("f", loc.z))
                f.write(struct.pack("f", rot.x))
                f.write(struct.pack("f", rot.y))
                f.write(struct.pack("f", rot.z))
                f.write(struct.pack("f", rot.w))
                f.write(struct.pack("f", scale.x))
                f.write(struct.pack("f", scale.y))
                f.write(struct.pack("f", scale.z))


