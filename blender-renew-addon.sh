#!/bin/bash

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
ADDON_NAME="praBlendExte"
ADDON_SRC="./$ADDON_NAME"
ADDON_DST="$HOME/Library/Application Support/Blender/5.0/scripts/addons/$ADDON_NAME"

rm -rf "$ADDON_DST"
cp -r "$ADDON_SRC" "$ADDON_DST"

TMP_PY=$(mktemp /tmp/blender_reload_XXXX.py)
cat > "$TMP_PY" << EOF
import bpy
bpy.ops.preferences.addon_enable(module="$ADDON_NAME")
bpy.ops.wm.save_userpref()
EOF

"$BLENDER" --background --python "$TMP_PY"
rm "$TMP_PY"