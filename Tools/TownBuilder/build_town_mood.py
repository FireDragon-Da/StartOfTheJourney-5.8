"""Sunset atmosphere for Lvl_TownBlock: low sun behind the exit gate, clouds, haze and grading.

    py exec(open(r'D:/StartOfTheJourney 5.8/Tools/TownBuilder/run.py').read()); run('build_town_mood.py')
"""
import unreal

actors_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by_label = {a.get_actor_label(): a for a in actors_sub.get_all_level_actors()}


def rot(pitch, yaw):
    r = unreal.Rotator()
    r.pitch, r.yaw, r.roll = pitch, yaw, 0.0
    return r


# The gate is due east of the square, so a sun low in the east backlights the street like the reference.
sun_actor = by_label["Sun"]
sun_actor.set_actor_rotation(rot(-9.0, 180.0), False)
sun = sun_actor.light_component
sun.set_editor_property("intensity", 11.0)
sun.set_editor_property("light_color", unreal.Color(r=255, g=150, b=82, a=255))
sun.set_editor_property("light_source_angle", 1.2)

sky = by_label["SkyLight"].light_component
sky.set_editor_property("intensity", 2.0)
sky.set_editor_property("light_color", unreal.Color(r=205, g=190, b=255, a=255))

if "Clouds" not in by_label:
    clouds = actors_sub.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
    clouds.set_actor_label("Clouds")
    clouds.set_folder_path("Lighting")

fog = by_label["Fog"].component
fog.set_editor_property("fog_density", 0.018)
fog.set_editor_property("fog_height_falloff", 0.16)
fog.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.30, 0.17, 0.24, 1.0))
fog.set_editor_property("directional_inscattering_luminance", unreal.LinearColor(1.2, 0.52, 0.2, 1.0))
fog.set_editor_property("directional_inscattering_exponent", 7.0)
fog.set_editor_property("start_distance", 400.0)
fog.set_editor_property("enable_volumetric_fog", True)
fog.set_editor_property("volumetric_fog_extinction_scale", 0.45)
fog.set_editor_property("volumetric_fog_distance", 7000.0)
fog.set_editor_property("volumetric_fog_albedo", unreal.Color(r=255, g=225, b=205, a=255))

pp_actor = by_label["WarmGrade"]
s = pp_actor.settings


def ov(name, value):
    s.set_editor_property("override_" + name, True)
    s.set_editor_property(name, value)


ov("auto_exposure_bias", 0.3)
ov("auto_exposure_min_brightness", -2.0)
ov("auto_exposure_max_brightness", 2.5)
ov("bloom_intensity", 1.1)
ov("bloom_threshold", 0.8)
ov("vignette_intensity", 0.55)
ov("white_temp", 5900.0)
ov("color_contrast", unreal.Vector4(1.12, 1.12, 1.12, 1.0))
ov("color_saturation", unreal.Vector4(1.08, 1.05, 1.02, 1.0))
ov("color_gain_shadows", unreal.Vector4(0.9, 0.9, 1.12, 1.0))
ov("color_saturation_highlights", unreal.Vector4(1.1, 1.05, 1.0, 1.0))
ov("scene_fringe_intensity", 0.3)
pp_actor.set_editor_property("settings", s)

sky_light_actor = by_label["SkyLight"]
sky_light_actor.light_component.recapture_sky()
