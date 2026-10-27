"""Writes docstrings of the merge-related editor APIs to Saved/TownBuilder/probe.txt."""
import os

import unreal

lines = []
for obj, names in (
    (unreal.StaticMeshEditorSubsystem, ["merge_static_mesh_actors"]),
    (unreal.MergeStaticMeshActorsOptions, None),
    (unreal.MeshMergingSettings, None),
    (unreal.MeshNaniteSettings, None),
):
    if names:
        for n in names:
            lines.append(f"== {obj.__name__}.{n}\n{getattr(obj, n).__doc__}")
    else:
        lines.append(f"== {obj.__name__}\n{obj.__doc__}")

path = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                    "TownBuilder", "probe.txt")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(lines))
