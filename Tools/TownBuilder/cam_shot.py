"""Places the level viewport camera and records the camera read back to Saved/TownBuilder/cam.json.

    run('cam_shot.py', x, y, z, pitch, yaw)
"""
import json
import sys

import unreal

x, y, z, pitch, yaw = (float(v) for v in sys.argv[1:6])

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r = unreal.Rotator()
r.pitch = pitch
r.yaw = yaw
r.roll = 0
ues.set_level_viewport_camera_info(unreal.Vector(x, y, z), r)
loc, rot = ues.get_level_viewport_camera_info()

saved = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/"
with open(saved + "cam.json", "w", encoding="utf-8") as f:
    json.dump({"loc": [loc.x, loc.y, loc.z], "rot": [rot.pitch, rot.yaw, rot.roll]}, f)
