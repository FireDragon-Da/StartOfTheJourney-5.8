"""Writes component materials of prop Blueprints and the lighting actors' key settings to Saved/TownBuilder/props.json."""
import json

import unreal

out = {"props": {}, "lighting": {}}
seen = set()
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    cls = a.get_class().get_name()
    if cls.startswith("BP_Town") and not cls.startswith("BP_TownHouse") and cls not in seen:
        seen.add(cls)
        comps = {}
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            if isinstance(c, unreal.StaticMeshComponent):
                comps[c.get_name()] = [m.get_name() if m else None for m in c.get_materials()]
        for c in a.get_components_by_class(unreal.PointLightComponent):
            comps[c.get_name()] = {"intensity": c.intensity, "radius": c.attenuation_radius,
                                   "color": str(c.light_color), "shadows": c.cast_shadows,
                                   "units": str(c.intensity_units)}
        out["props"][cls] = comps

lab = {a.get_actor_label(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
sun = lab["Sun"].light_component
out["lighting"]["sun"] = {"rot": str(lab["Sun"].get_actor_rotation()), "intensity": sun.intensity,
                          "color": str(sun.light_color), "temp": sun.use_temperature}
sky = lab["SkyLight"].light_component
out["lighting"]["skylight"] = {"intensity": sky.intensity, "color": str(sky.light_color)}
fog = lab["Fog"].component
out["lighting"]["fog"] = {"density": fog.fog_density, "falloff": fog.fog_height_falloff,
                          "inscatter": str(fog.fog_inscattering_luminance),
                          "fog_props": [p for p in dir(fog) if "volumetric" in p or "inscatter" in p],
                          "start": fog.start_distance}
pp = lab["WarmGrade"].settings
out["lighting"]["pp"] = {k: str(pp.get_editor_property(k)) for k in (
    "override_auto_exposure_method", "auto_exposure_method", "auto_exposure_bias", "auto_exposure_min_brightness",
    "auto_exposure_max_brightness", "bloom_intensity", "white_temp", "color_saturation", "color_contrast",
    "color_gain", "vignette_intensity")}
out["lighting"]["pp_unbound"] = lab["WarmGrade"].unbound
out["lighting"]["has_clouds"] = any(a.get_class().get_name() == "VolumetricCloud" for a in lab.values())

path = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/props.json"
with open(path, "w") as f:
    json.dump(out, f, indent=1)
