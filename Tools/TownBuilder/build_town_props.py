"""Street dressing for Lvl_TownBlock: surface materials, street furniture Blueprints and their placement.

    py exec(open(r'D:/StartOfTheJourney 5.8/Tools/TownBuilder/run.py').read()); run('build_town_props.py')

Everything this script spawns lives in the "Street" outliner folder and is replaced on every run.
Hand-placed props in "Props" are only moved.
"""
import json
import math
import random

import unreal

BP_DIR = "/Game/Inarchived/Town/Blueprints/"
MAT_DIR = "/Game/Inarchived/Town/Materials/"
CUBE = "/Engine/BasicShapes/Cube.Cube"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere.Sphere"
CONE = "/Engine/BasicShapes/Cone.Cone"
SMC = "/Script/Engine.StaticMeshComponent"
PLC = "/Script/Engine.PointLightComponent"
ROOT = "DefaultSceneRoot"
FOLDER = "Street"
SIDEWALK_Z = 30.0
SEED = 77

helper = unreal.MCPythonHelper
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
actors_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def mpath(name):
    return f"{MAT_DIR}{name}.{name}"


# ---------------------------------------------------------------- materials
def ensure_mi(name, parent, color=None, roughness=None, metallic=None):
    path = MAT_DIR + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        mi = tools.create_asset(name, MAT_DIR.rstrip("/"), unreal.MaterialInstanceConstant,
                                unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, unreal.load_asset(mpath(parent)))
    if color is not None:
        mel.set_material_instance_vector_parameter_value(mi, "BaseColor", unreal.LinearColor(*color, 1.0))
    if roughness is not None:
        mel.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    if metallic is not None:
        mel.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
    return mpath(name)


MATS = {
    "wet_road": ensure_mi("MI_TownRoad_Wet", "M_TownRoad", (0.028, 0.028, 0.032), 0.16, 0.0),
    "cobble": ensure_mi("MI_TownCobble", "M_TownRoad", (0.11, 0.09, 0.075), 0.45, 0.0),
    "sidewalk": ensure_mi("MI_TownSidewalk", "M_TownPlaster", (0.3, 0.26, 0.22), 0.3),
    "square": ensure_mi("MI_TownSquare", "M_TownPlaster", (0.34, 0.29, 0.24), 0.35),
    "square_line": ensure_mi("MI_TownSquareJoint", "M_TownRoad", (0.06, 0.05, 0.045), 0.3),
    "puddle": ensure_mi("MI_TownPuddle", "M_TownRoad", (0.006, 0.006, 0.008), 0.02, 0.0),
    "sign": ensure_mi("MI_TownSignPlate", "M_TownPlaster", (0.02, 0.05, 0.04), 0.4),
    "metal": mpath("M_TownMetal"),
    "lit": mpath("M_TownWindow"),
    "trim": mpath("MI_TownTrim"),
    "stone": mpath("MI_TownStoneBase"),
    "cream": mpath("MI_TownAwning_Cream"),
    "leaf": mpath("M_TownFoliage"),
}


# ---------------------------------------------------------------- blueprint authoring
def ensure_bp(name):
    path = BP_DIR + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        bp = unreal.load_asset(path)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.Actor)
        bp = tools.create_asset(name, BP_DIR.rstrip("/"), unreal.Blueprint, factory)
    listing = json.loads(helper.list_blueprint_components(bp))
    names = [c["variable_name"] for c in listing.get("components", [])]
    for n in names:
        if n != ROOT:
            helper.remove_component_from_blueprint(bp, n)
    return bp


def part(bp, name, mesh, loc, size, mat, rot=(0, 0, 0)):
    helper.add_component_to_blueprint(bp, SMC, name, loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], ROOT)
    helper.set_component_property(bp, name, "StaticMesh", mesh)
    helper.set_component_property(bp, name, "RelativeScale3D",
                                  f"(X={size[0] / 100:.4f},Y={size[1] / 100:.4f},Z={size[2] / 100:.4f})")
    helper.set_component_property(bp, name, "OverrideMaterials", f'("{mat}")')


def light(bp, name, loc, candela, radius, color="(R=255,G=170,B=90,A=255)"):
    helper.add_component_to_blueprint(bp, PLC, name, loc[0], loc[1], loc[2], 0, 0, 0, ROOT)
    for prop, value in (("IntensityUnits", "Candelas"), ("Intensity", str(candela)),
                        ("AttenuationRadius", str(radius)), ("LightColor", color),
                        ("CastShadows", "False"), ("SourceRadius", "6"),
                        ("VolumetricScatteringIntensity", "2.0")):
        helper.set_component_property(bp, name, prop, value)


def finish(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(bp.get_path_name().split(".")[0], only_if_is_dirty=False)


def build_bollard():
    bp = ensure_bp("BP_TownBollard")
    m = MATS["metal"]
    part(bp, "Base", CYL, (0, 0, 5), (26, 26, 10), m)
    part(bp, "Post", CYL, (0, 0, 50), (16, 16, 90), m)
    part(bp, "Ring", CYL, (0, 0, 78), (21, 21, 5), m)
    part(bp, "Cap", SPHERE, (0, 0, 96), (19, 19, 19), m)
    finish(bp)


def build_signpost():
    """Cast-iron lamp post carrying two street name plates, as on the reference street corner."""
    bp = ensure_bp("BP_TownSignpost")
    m = MATS["metal"]
    part(bp, "Plinth", CYL, (0, 0, 30), (40, 40, 60), m)
    part(bp, "PlinthRing", CYL, (0, 0, 64), (30, 30, 8), m)
    part(bp, "Pole", CYL, (0, 0, 250), (14, 14, 380), m)
    part(bp, "Collar", CYL, (0, 0, 180), (22, 22, 10), m)
    part(bp, "CollarTop", CYL, (0, 0, 438), (24, 24, 8), m)
    part(bp, "LanternBase", CYL, (0, 0, 450), (34, 34, 10), m)
    part(bp, "LanternGlass", CUBE, (0, 0, 485), (26, 26, 52), MATS["lit"])
    for i, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        part(bp, f"LanternBar{i}", CUBE, (dx * 14, dy * 14, 485), (3, 3, 56), m)
    part(bp, "LanternRoof", CONE, (0, 0, 526), (42, 42, 28), m)
    part(bp, "Finial", SPHERE, (0, 0, 546), (10, 10, 10), m)
    light(bp, "LanternLight", (0, 0, 485), 35, 1200)
    # Two plates at right angles, each hanging out to one side like an arrow sign.
    part(bp, "PlateA", CUBE, (0, 68, 330), (4, 120, 26), MATS["sign"])
    part(bp, "PlateAText", CUBE, (0, 64, 330), (6, 96, 10), MATS["cream"])
    part(bp, "PlateATip", CUBE, (0, 132, 330), (4, 18, 18), MATS["sign"], (0, 0, 45))
    part(bp, "PlateB", CUBE, (68, 0, 296), (120, 4, 26), MATS["sign"])
    part(bp, "PlateBText", CUBE, (64, 0, 296), (96, 6, 10), MATS["cream"])
    part(bp, "PlateBTip", CUBE, (132, 0, 296), (18, 4, 18), MATS["sign"], (0, 45, 0))
    finish(bp)


def build_railing():
    """300 cm iron railing segment running along local Y."""
    bp = ensure_bp("BP_TownRailing")
    m = MATS["metal"]
    part(bp, "TopRail", CUBE, (0, 0, 92), (5, 300, 5), m)
    part(bp, "BottomRail", CUBE, (0, 0, 14), (4, 300, 4), m)
    for s in (-1, 1):
        part(bp, f"Post{'L' if s < 0 else 'R'}", CUBE, (0, s * 148, 50), (7, 7, 100), m)
        part(bp, f"PostFinial{'L' if s < 0 else 'R'}", SPHERE, (0, s * 148, 104), (10, 10, 10), m)
    for i in range(19):
        y = -135 + i * 15
        part(bp, f"Bar{i:02d}", CUBE, (0, y, 53), (2.5, 2.5, 78), m)
        part(bp, f"Spike{i:02d}", CONE, (0, y, 98), (5, 5, 8), m)
    finish(bp)


def build_wall():
    """300 cm stone boundary wall segment along local Y, with a pier at its +Y end."""
    bp = ensure_bp("BP_TownWall")
    part(bp, "Wall", CUBE, (0, 0, 140), (40, 300, 280), MATS["stone"])
    part(bp, "Coping", CUBE, (0, 0, 288), (56, 304, 14), MATS["trim"])
    part(bp, "Pier", CUBE, (0, 150, 160), (64, 64, 320), MATS["stone"])
    part(bp, "PierCap", CUBE, (0, 150, 326), (76, 76, 14), MATS["trim"])
    part(bp, "PierBall", SPHERE, (0, 150, 352), (38, 38, 38), MATS["trim"])
    finish(bp)


def build_puddle():
    bp = ensure_bp("BP_TownPuddle")
    part(bp, "Water", CYL, (0, 0, 0.4), (100, 100, 0.8), MATS["puddle"])
    finish(bp)


def build_square():
    """Paved town square filling the inside of the loop road, level with the sidewalks."""
    bp = ensure_bp("BP_TownSquare")
    half = 1570.0
    part(bp, "Paving", CUBE, (0, 0, SIDEWALK_Z / 2), (2 * half, 2 * half, SIDEWALK_Z), MATS["square"])
    for s in (-1, 1):
        part(bp, f"KerbX{'N' if s > 0 else 'S'}", CUBE, (s * (half - 20), 0, SIDEWALK_Z / 2 + 1),
             (40, 2 * half, SIDEWALK_Z + 2), MATS["trim"])
        part(bp, f"KerbY{'E' if s > 0 else 'W'}", CUBE, (0, s * (half - 20), SIDEWALK_Z / 2 + 1),
             (2 * half, 40, SIDEWALK_Z + 2), MATS["trim"])
    n = 0
    step = 314.0
    for i in range(1, 10):
        o = -half + i * step
        n += 1
        part(bp, f"JointX{n:02d}", CUBE, (o, 0, SIDEWALK_Z + 0.2), (5, 2 * half - 80, 1), MATS["square_line"])
        part(bp, f"JointY{n:02d}", CUBE, (0, o, SIDEWALK_Z + 0.2), (2 * half - 80, 5, 1), MATS["square_line"])
    finish(bp)


def restyle_existing():
    for name, comps in (("BP_TownRoad", {"Road": "wet_road", "SidewalkLeft": "sidewalk", "SidewalkRight": "sidewalk"}),
                        ("BP_TownRoadCurve", {"SegA": "wet_road", "SegB": "wet_road", "SegC": "wet_road"}),
                        ("BP_TownGround", {"Ground": "cobble"})):
        bp = unreal.load_asset(BP_DIR + name)
        for comp, key in comps.items():
            helper.set_component_property(bp, comp, "OverrideMaterials", f'("{MATS[key]}")')
        finish(bp)
    lamp = unreal.load_asset(BP_DIR + "BP_TownStreetLamp")
    for prop, value in (("IntensityUnits", "Candelas"), ("Intensity", "45"), ("AttenuationRadius", "1400"),
                        ("CastShadows", "False"), ("SourceRadius", "6"), ("VolumetricScatteringIntensity", "2.0"),
                        ("LightColor", "(R=255,G=168,B=86,A=255)")):
        helper.set_component_property(lamp, "LampLight", prop, value)
    finish(lamp)


# ---------------------------------------------------------------- placement
ROAD_RECTS = {
    "West": (-6130, -4870, -3000, 3000),
    "LinkN": (-5300, -2300, 1170, 2430),
    "LinkS": (-5300, -2300, -2430, -1170),
    "LoopW": (-2830, -1570, -2830, 2830),
    "LoopE": (1570, 2830, -2830, 2830),
    "North": (-2830, 2830, 1570, 2830),
    "South": (-2830, 2830, -2830, -1570),
    "Exit": (2300, 5900, -230, 1030),
}
# (road, axis the road runs along, centre line, start, end)
LAMP_RUNS = [
    ("West", "y", -5500, -2800, 2800),
    ("LinkN", "x", 1800, -4700, -2950),
    ("LinkS", "x", -1800, -4700, -2950),
    ("LoopW", "y", -2200, -2000, 2000),
    ("LoopE", "y", 2200, -2000, 2000),
    ("North", "x", 2200, -2000, 2000),
    ("South", "x", -2200, -2000, 2000),
    ("Exit", "x", 400, 2950, 5650),
]
CROSSWALKS = [(4500, 400), (-5500, 1800), (-5500, -200)]


def inside(pt, rect, margin=0.0):
    return rect[0] - margin <= pt[0] <= rect[1] + margin and rect[2] - margin <= pt[1] <= rect[3] + margin


def head_yaw(dx, dy):
    """Yaw that points the lamp arm (local -Y) along (dx, dy)."""
    return math.degrees(math.atan2(dx, -dy))


def spawn(cls_name, label, x, y, z=SIDEWALK_Z, yaw=0.0, scale=(1, 1, 1)):
    cls = unreal.EditorAssetLibrary.load_blueprint_class(BP_DIR + cls_name)
    rot = unreal.Rotator()
    rot.yaw = yaw
    a = actors_sub.spawn_actor_from_class(cls, unreal.Vector(x, y, z), rot)
    a.set_actor_label(label)
    a.set_folder_path(FOLDER)
    a.set_actor_scale3d(unreal.Vector(*scale))
    return a


def place():
    by_label = {a.get_actor_label(): a for a in actors_sub.get_all_level_actors()}
    for a in list(by_label.values()):
        folder = str(a.get_folder_path())
        if folder == FOLDER or (folder == "Props" and a.get_actor_label().startswith("Lamp_")):
            actors_sub.destroy_actor(a)

    def move(label, x, y, z=None, yaw=None):
        a = by_label.get(label)
        if not a:
            return
        loc = a.get_actor_location()
        a.set_actor_location(unreal.Vector(x, y, loc.z if z is None else z), False, False)
        if yaw is not None:
            r = a.get_actor_rotation()
            r.yaw = yaw
            a.set_actor_rotation(r, False)

    # Hand-placed props onto sidewalks / into the spaces the dense layout left for them.
    move("NewsStand", -4640, 2700, SIDEWALK_Z - 30, -90)
    move("Bench_News", -4350, 2930, SIDEWALK_Z - 30, 180)
    move("Tree_News", -4330, 2600)
    move("ParkedCar", -5840, -1350, 20, 90)
    move("Tree_W1", -5020, 700)
    move("Tree_W2", -5020, -800)
    move("Tree_East", 2680, 1650)
    move("Tree_Gate", 4150, 1450)
    move("Tree_South", -1000, -620)
    move("Bench_Plaza1", 400, 1000, SIDEWALK_Z, 180)
    move("Bench_Plaza2", -800, 600, SIDEWALK_Z)
    move("Bench_Plaza3", 200, -900, SIDEWALK_Z)

    spawn("BP_TownSquare", "PlazaSquare", 0, 0, 0)

    rng = random.Random(SEED)
    n = 0
    for road, axis, c, lo, hi in LAMP_RUNS:
        for side in (-1, 1):
            p = lo + (0 if side < 0 else 550)
            while p <= hi:
                x, y = (c + side * 500, p) if axis == "y" else (p, c + side * 500)
                blocked = any(inside((x, y), r, 60) for k, r in ROAD_RECTS.items() if k != road)
                blocked |= any(math.hypot(x - cx, y - cy) < 450 for cx, cy in CROSSWALKS)
                if not blocked:
                    dx, dy = (-side, 0) if axis == "y" else (0, -side)
                    n += 1
                    spawn("BP_TownStreetLamp", f"Lamp_{road}_{n:02d}", x, y, 0, head_yaw(dx, dy))
                p += 1100

    # Bollards flanking every crosswalk on both kerbs.
    b = 0
    for (cx, cy), along_x in zip(CROSSWALKS, (False, True, True)):
        for kerb in (-1, 1):
            for off in (-380, -250, 250, 380):
                if along_x:
                    x, y = cx + kerb * 480, cy + off
                else:
                    x, y = cx + off, cy + kerb * 480
                b += 1
                spawn("BP_TownBollard", f"Bollard_{b:02d}", x, y)

    # Each plaza opening between the corner houses: railings either side of a bollard-guarded gap.
    half = 1500.0
    r = 0
    for s in (-1, 1):
        for o in (-450, 450):
            r += 1
            spawn("BP_TownRailing", f"SquareRail_{r:02d}", s * half, o, SIDEWALK_Z, 0)
            r += 1
            spawn("BP_TownRailing", f"SquareRail_{r:02d}", o, s * half, SIDEWALK_Z, 90)
        for o in (-330, 330):
            b += 1
            spawn("BP_TownBollard", f"Bollard_{b:02d}", s * half, o)
            b += 1
            spawn("BP_TownBollard", f"Bollard_{b:02d}", o, s * half)

    spawn("BP_TownSignpost", "Signpost_News", -4960, 2340, SIDEWALK_Z, 0)
    spawn("BP_TownSignpost", "Signpost_Exit", 2950, 940, SIDEWALK_Z, 180)
    spawn("BP_TownSignpost", "Signpost_Square", 1480, -640, SIDEWALK_Z, 90)

    # Walls tie the gate pillars to the last houses so the gate is the only way out.
    spawn("BP_TownWall", "GateWall_N1", 5740, 1045, 0, 90)
    spawn("BP_TownWall", "GateWall_N2", 5960, 1045, 0, 90)
    spawn("BP_TownWall", "GateWall_N3", 6100, 960, 0, 0)
    spawn("BP_TownWall", "GateWall_S1", 5880, -245, 0, -90)
    spawn("BP_TownWall", "GateWall_S2", 6100, -160, 0, 180)

    # Puddles on the asphalt, kept off the crosswalks.
    p = 0
    tries = 0
    while p < 34 and tries < 500:
        tries += 1
        road, axis, c, lo, hi = rng.choice(LAMP_RUNS)
        t = rng.uniform(lo, hi)
        off = rng.uniform(-380, 380)
        x, y = (c + off, t) if axis == "y" else (t, c + off)
        if any(math.hypot(x - cx, y - cy) < 420 for cx, cy in CROSSWALKS):
            continue
        p += 1
        spawn("BP_TownPuddle", f"Puddle_{p:02d}", x, y, 20.2, rng.uniform(0, 180),
              (rng.uniform(1.0, 3.2), rng.uniform(0.6, 1.5), 1.0))
    return {"lamps": n, "bollards": b, "rails": r, "puddles": p}


build_bollard()
build_signpost()
build_railing()
build_wall()
build_puddle()
build_square()
restyle_existing()
result = place()
out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/props_result.json"
with open(out, "w") as f:
    json.dump(result, f)
