"""Writes every actor in the open level (label, class, location, yaw, scale, folder) to Saved/TownBuilder/level_dump.json."""
import json
import os

import unreal

out = []
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    loc = a.get_actor_location()
    rot = a.get_actor_rotation()
    sc = a.get_actor_scale3d()
    out.append({
        "label": a.get_actor_label(),
        "class": a.get_class().get_name(),
        "loc": [round(loc.x), round(loc.y), round(loc.z)],
        "yaw": round(rot.yaw, 1),
        "scale": [round(sc.x, 2), round(sc.y, 2), round(sc.z, 2)],
        "folder": str(a.get_folder_path()),
    })
path = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                    "TownBuilder", "level_dump.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(sorted(out, key=lambda d: (d["folder"], d["label"])), f, indent=0)
