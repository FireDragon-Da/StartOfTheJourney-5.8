"""Writes one sample of each town Blueprint class (actor bounds plus per-component local boxes) to Saved/TownBuilder/bounds.json."""
import json
import os

import unreal

seen = {}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    cls = a.get_class().get_name()
    if not cls.startswith("BP_Town") or cls in seen:
        continue
    origin, extent = a.get_actor_bounds(False)
    comps = []
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        o, e, _ = unreal.SystemLibrary.get_component_bounds(c)
        comps.append({"name": c.get_name(), "center": [round(o.x - origin.x), round(o.y - origin.y), round(o.z)],
                      "extent": [round(e.x), round(e.y), round(e.z)]})
    loc = a.get_actor_location()
    seen[cls] = {"actor": a.get_actor_label(), "loc": [round(loc.x), round(loc.y)], "yaw": round(a.get_actor_rotation().yaw),
                 "bounds_center": [round(origin.x), round(origin.y), round(origin.z)],
                 "bounds_extent": [round(extent.x), round(extent.y), round(extent.z)],
                 "components": comps[:40] if not cls.startswith("BP_TownHouse") else len(comps)}

path = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                    "TownBuilder", "bounds.json")
with open(path, "w") as f:
    json.dump(seen, f, indent=1)
