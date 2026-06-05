import bpy
import bmesh
import struct
import os
from config import MAGIC_CODE, VERSION


def _import(path: str):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "rb") as f:

        # HEADER
        magic = f.read(4).decode('ascii')
        if magic != MAGIC_CODE:
            print(f"Invalid magic: {magic}")
            return

        version = struct.unpack("B", f.read(1))[0]
        if version != VERSION:
            print(f"Invalid version: {version}")
            return

        mesh_count    = struct.unpack("B", f.read(1))[0]
        object_count  = struct.unpack("B", f.read(1))[0]
        animation_count = struct.unpack("B", f.read(1))[0]

        # MESHES
        meshes = []
        for _ in range(mesh_count):
            mesh_id      = struct.unpack("B", f.read(1))[0]
            vertex_count = struct.unpack("H", f.read(2))[0]
            index_count  = struct.unpack("H", f.read(2))[0]

            vertices = []
            for _ in range(vertex_count):
                x = struct.unpack("f", f.read(4))[0]
                y = struct.unpack("f", f.read(4))[0]
                z = struct.unpack("f", f.read(4))[0]
                vertices.append((x, y, z))

            indices = []
            for _ in range(index_count):
                v0 = struct.unpack("H", f.read(2))[0]
                v1 = struct.unpack("H", f.read(2))[0]
                v2 = struct.unpack("H", f.read(2))[0]
                indices.append((v0, v1, v2))

            meshes.append((mesh_id, vertices, indices))

        # OBJECTS
        for _ in range(object_count):
            obj_id   = struct.unpack("B", f.read(1))[0]
            mesh_ref = struct.unpack("B", f.read(1))[0]

            px, py, pz = struct.unpack("fff", f.read(12))
            rx, ry, rz, rw = struct.unpack("ffff", f.read(16))
            sx, sy, sz = struct.unpack("fff", f.read(12))

            # znajdz mesh
            _, vertices, indices = meshes[mesh_ref]

            # stworz mesh w blenderze
            mesh_name = f"PR4_mesh_{mesh_id}"
            if mesh_name in bpy.data.meshes:
                bl_mesh = bpy.data.meshes[mesh_name]
            else:
                bl_mesh = bpy.data.meshes.new(mesh_name)
                bl_mesh.from_pydata(vertices, [], indices)
                bl_mesh.update()

            bl_obj = bpy.data.objects.new(f"PR4_object_{obj_id}", bl_mesh)
            bpy.context.collection.objects.link(bl_obj)

            bl_obj.location = (px, py, pz)
            bl_obj.rotation_mode = 'QUATERNION'
            bl_obj.rotation_quaternion = (rw, rx, ry, rz)
            bl_obj.scale = (sx, sy, sz)

        # ANIMATIONS
        for _ in range(animation_count):
            anim_id    = struct.unpack("B", f.read(1))[0]
            object_ref = struct.unpack("B", f.read(1))[0]
            fps        = struct.unpack("B", f.read(1))[0]
            kf_count   = struct.unpack("H", f.read(2))[0]

            # znajdz obiekt po object_ref
            target_obj = bpy.data.objects.get(f"PR4_object_{object_ref}")
            if target_obj is None:
                # pomiń keyframe'y
                f.read(kf_count * 40)
                continue

            target_obj.animation_data_create()
            action = bpy.data.actions.new(f"PR4_action_{anim_id}")
            target_obj.animation_data.action = action

            for frame_idx in range(kf_count):
                px, py, pz = struct.unpack("fff", f.read(12))
                rx, ry, rz, rw = struct.unpack("ffff", f.read(16))
                sx, sy, sz = struct.unpack("fff", f.read(12))

                target_obj.location = (px, py, pz)
                target_obj.rotation_quaternion = (rw, rx, ry, rz)
                target_obj.scale = (sx, sy, sz)
                target_obj.keyframe_insert("location", frame=frame_idx*10)
                target_obj.keyframe_insert("rotation_quaternion", frame=frame_idx*10)
                target_obj.keyframe_insert("scale", frame=frame_idx*10 )