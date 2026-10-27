"""Dumps the gate actor, its components and nearby props to Saved/TownBuilder/gate_dump.json."""
import json

import unreal

OUT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/gate_dump.json"


def vec(v):
    return [round(v.x, 1), round(v.y, 1), round(v.z, 1)]


def rot(r):
    return [round(r.pitch, 1), round(r.yaw, 1), round(r.roll, 1)]


def main():
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    out = {"gate": [], "nearby": []}
    for a in actors:
        loc = a.get_actor_location()
        cls = a.get_class().get_name()
        entry = {"label": a.get_actor_label(), "class": cls, "loc": vec(loc), "rot": rot(a.get_actor_rotation()),
                 "folder": str(a.get_folder_path())}
        if "Gate" in cls:
            comps = []
            for c in a.get_components_by_class(unreal.SceneComponent):
                d = {"name": c.get_name(), "class": c.get_class().get_name(),
                     "rel_loc": vec(c.get_editor_property("relative_location")),
                     "rel_rot": rot(c.get_editor_property("relative_rotation")),
                     "rel_scale": vec(c.get_editor_property("relative_scale3d"))}
                if isinstance(c, unreal.StaticMeshComponent):
                    sm = c.get_editor_property("static_mesh")
                    d["mesh"] = sm.get_path_name() if sm else None
                    d["mats"] = [m.get_path_name() if m else None for m in c.get_materials()]
                if isinstance(c, unreal.PointLightComponent):
                    d["intensity"] = c.get_editor_property("intensity")
                    d["radius"] = c.get_editor_property("attenuation_radius")
                comps.append(d)
            entry["components"] = comps
            out["gate"].append(entry)
        elif 4800 < loc.x < 9000 and -2000 < loc.y < 2800:
            out["nearby"].append(entry)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


main()
