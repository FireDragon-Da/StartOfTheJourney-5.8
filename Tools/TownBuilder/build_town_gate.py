"""Rebuilds BP_TownGate as the lit wrought-iron gate at the top of a short flight of steps (reference street end).

    py exec(open(r'D:/StartOfTheJourney 5.8/Tools/TownBuilder/run.py').read()); run('build_town_gate.py')

Local frame: the town is on -X, the gate line is x=0, the opening spans local Y. Ground z=0, road top z=20.
Only components are replaced, so the placed FinalGate actor and the Blueprint's graphs are kept.
"""
import json
import math

import unreal

BP_PATH = "/Game/Inarchived/Town/Blueprints/BP_TownGate"
MAT_DIR = "/Game/Inarchived/Town/Materials/"
CUBE = "/Engine/BasicShapes/Cube.Cube"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere.Sphere"
CONE = "/Engine/BasicShapes/Cone.Cone"
SMC = "/Script/Engine.StaticMeshComponent"
PLC = "/Script/Engine.PointLightComponent"
SCENE = "/Script/Engine.SceneComponent"
BOX = "/Script/Engine.BoxComponent"
ROOT = "DefaultSceneRoot"

ROAD_Z = 20.0
STEP_RISE = 20.0
STEP_RUN = 60.0
STEPS = 4
LAND_Z = ROAD_Z + STEP_RISE * STEPS
STAIR_FRONT = -240.0
LANDING_BACK = 700.0
STAIR_HALF_W = 500.0

PILLAR_Y = 475.0
PILLAR_W = 120.0
OPENING_HALF = PILLAR_Y - PILLAR_W / 2  # 415: inner pillar face, where the leaves hinge
OPEN_DEG = 28.0

helper = unreal.MCPythonHelper


def mpath(name):
    return f"{MAT_DIR}{name}.{name}"


STONE = mpath("MI_TownStoneBase")
TRIM = mpath("MI_TownTrim")
IRON = mpath("M_TownMetal")
LIT = mpath("M_TownWindow")


def clear(bp):
    listing = json.loads(helper.list_blueprint_components(bp))
    for c in listing.get("components", []):
        if c["variable_name"] != ROOT:
            helper.remove_component_from_blueprint(bp, c["variable_name"])


def part(bp, name, mesh, loc, size, mat, rot=(0, 0, 0), parent=ROOT):
    helper.add_component_to_blueprint(bp, SMC, name, loc[0], loc[1], loc[2], rot[0], rot[1], rot[2], parent)
    helper.set_component_property(bp, name, "StaticMesh", mesh)
    helper.set_component_property(bp, name, "RelativeScale3D",
                                  f"(X={size[0] / 100:.4f},Y={size[1] / 100:.4f},Z={size[2] / 100:.4f})")
    helper.set_component_property(bp, name, "OverrideMaterials", f'("{mat}")')


def light(bp, name, loc, candela, radius, color="(R=255,G=170,B=90,A=255)", shadows=False, scatter=2.0,
          parent=ROOT):
    helper.add_component_to_blueprint(bp, PLC, name, loc[0], loc[1], loc[2], 0, 0, 0, parent)
    for prop, value in (("IntensityUnits", "Candelas"), ("Intensity", str(candela)),
                        ("AttenuationRadius", str(radius)), ("LightColor", color),
                        ("CastShadows", str(shadows)), ("CastVolumetricShadow", str(shadows)),
                        ("SourceRadius", "8"), ("VolumetricScatteringIntensity", str(scatter))):
        helper.set_component_property(bp, name, prop, value)


def roll_for(dy, dz):
    """Roll that lays a box's local Y along the (dy, dz) direction in the YZ plane."""
    a = math.degrees(math.atan2(dz, dy))
    r = unreal.Rotator()
    r.roll = a
    return a if r.get_right_vector().z * dz >= 0 else -a


# ---------------------------------------------------------------- pieces
def build_stairs(bp):
    for i in range(STEPS):
        top = ROAD_Z + STEP_RISE * (i + 1)
        x0 = STAIR_FRONT + STEP_RUN * i
        part(bp, f"Step{i}", CUBE, ((x0 + LANDING_BACK) / 2, 0, top / 2),
             (LANDING_BACK - x0, 2 * STAIR_HALF_W, top), STONE)
        part(bp, f"Nosing{i}", CUBE, (x0 + 5, 0, top + 0.5), (10, 2 * STAIR_HALF_W - 4, 1), TRIM)
    part(bp, "Threshold", CUBE, (0, 0, LAND_Z + 1), (44, 2 * OPENING_HALF, 2), TRIM)

    cheek_x0, cheek_x1 = STAIR_FRONT - 30, 60.0
    cheek_h = LAND_Z + 40
    cx = (cheek_x0 + cheek_x1) / 2
    for s, tag in ((-1, "L"), (1, "R")):
        y = s * (STAIR_HALF_W + 30)
        part(bp, f"Cheek{tag}", CUBE, (cx, y, cheek_h / 2), (cheek_x1 - cheek_x0, 60, cheek_h), STONE)
        part(bp, f"CheekCoping{tag}", CUBE, (cx, y, cheek_h + 6), (cheek_x1 - cheek_x0 + 10, 76, 12), TRIM)
        ux = cheek_x0 + 40
        part(bp, f"UrnPlinth{tag}", CUBE, (ux, y, cheek_h + 27), (60, 60, 30), TRIM)
        part(bp, f"UrnFoot{tag}", CYL, (ux, y, cheek_h + 50), (30, 30, 16), STONE)
        part(bp, f"UrnBowl{tag}", SPHERE, (ux, y, cheek_h + 78), (56, 56, 44), STONE)
        part(bp, f"UrnRim{tag}", CYL, (ux, y, cheek_h + 100), (50, 50, 6), TRIM)


def lantern(bp, tag, x, y, z, candela):
    """Cast-iron lantern whose base sits at z."""
    part(bp, f"{tag}Base", CYL, (x, y, z + 6), (40, 40, 12), IRON)
    part(bp, f"{tag}Glass", CUBE, (x, y, z + 40), (30, 30, 56), LIT)
    for i, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        part(bp, f"{tag}Bar{i}", CUBE, (x + dx * 16, y + dy * 16, z + 40), (3, 3, 60), IRON)
    part(bp, f"{tag}Roof", CONE, (x, y, z + 84), (50, 50, 30), IRON)
    part(bp, f"{tag}Finial", SPHERE, (x, y, z + 104), (12, 12, 12), IRON)
    light(bp, f"{tag}Light", (x, y, z + 40), candela, 1500)


def build_pillars(bp):
    z = LAND_Z
    for s, tag in ((-1, "L"), (1, "R")):
        y = s * PILLAR_Y
        part(bp, f"Pillar{tag}Plinth", CUBE, (0, y, z + 35), (150, 150, 70), STONE)
        part(bp, f"Pillar{tag}PlinthTrim", CUBE, (0, y, z + 72), (140, 140, 8), TRIM)
        part(bp, f"Pillar{tag}Shaft", CUBE, (0, y, z + 356), (PILLAR_W, PILLAR_W, 560), STONE)
        part(bp, f"Pillar{tag}Band", CUBE, (0, y, z + 300), (132, 132, 14), TRIM)
        part(bp, f"Pillar{tag}Panel", CUBE, (-61, y, z + 180), (4, 76, 160), TRIM)
        part(bp, f"Pillar{tag}Cornice", CUBE, (0, y, z + 648), (156, 156, 24), TRIM)
        part(bp, f"Pillar{tag}Cap", CUBE, (0, y, z + 675), (132, 132, 30), STONE)
        lantern(bp, f"Pillar{tag}Lantern", 0, y, z + 690, 40)


def build_leaf(bp, tag, side):
    """One gate leaf on its own hinge pivot. side=+1 hangs on the -Y pillar and reaches toward +Y."""
    pivot = f"Leaf{tag}"
    yaw = -side * OPEN_DEG  # swings away from the town (+X)
    helper.add_component_to_blueprint(bp, SCENE, pivot, 0, -side * OPENING_HALF, LAND_Z, 0, yaw, 0, ROOT)

    w = OPENING_HALF - 3
    base, rise = 300.0, 70.0

    def top(u):
        return base + rise * math.sin(math.pi / 2 * u / w)

    def at(u, z):
        return (0, side * u, z)

    p = pivot
    part(bp, f"{tag}HingeStile", CUBE, at(5, 195), (8, 8, 390), IRON, parent=p)
    part(bp, f"{tag}MeetStile", CUBE, at(w - 4, (base + rise + 16) / 2), (8, 8, base + rise + 16), IRON, parent=p)
    for rail, z, t in (("Bottom", 14, 8), ("Mid", 90, 6), ("Upper", 240, 6)):
        part(bp, f"{tag}{rail}Rail", CUBE, at(w / 2, z), (6, w, t), IRON, parent=p)

    spacing = 18.0
    n = int((w - 2 * spacing) // spacing) + 1
    for i in range(n):
        u = spacing + i * spacing
        h = top(u)
        part(bp, f"{tag}Bar{i:02d}", CUBE, at(u, (14 + h) / 2), (3, 3, h - 14), IRON, parent=p)
        part(bp, f"{tag}Spike{i:02d}", CONE, at(u, h), (8, 8, 14), IRON, parent=p)
        part(bp, f"{tag}Arch{i:02d}", CUBE, at(u, h - 26), (5, spacing + 1, 5), IRON, parent=p)
        if i < n - 1:
            part(bp, f"{tag}Rosette{i:02d}", CYL, at(u + spacing / 2, 215), (14, 14, 3), IRON, (90, 0, 0), parent=p)
            part(bp, f"{tag}Dog{i:02d}", CUBE, at(u + spacing / 2, 52), (2.5, 2.5, 76), IRON, parent=p)


def arc(bp, tag, half, base_z, rise, thick, segments):
    pts = [(-half * math.cos(math.pi * k / segments), base_z + rise * math.sin(math.pi * k / segments))
           for k in range(segments + 1)]
    for k in range(segments):
        (y0, z0), (y1, z1) = pts[k], pts[k + 1]
        dy, dz = y1 - y0, z1 - z0
        length = math.hypot(dy, dz) + 2
        part(bp, f"{tag}{k:02d}", CUBE, (0, (y0 + y1) / 2, (z0 + z1) / 2), (thick, length, thick), IRON,
             (0, 0, roll_for(dy, dz)))
    return pts


def build_overthrow(bp):
    """Wrought-iron arch spanning the pillar tops with a hanging lantern at its crown."""
    base = LAND_Z + 620
    part(bp, "OverRail", CUBE, (0, 0, base), (8, 2 * OPENING_HALF + 20, 8), IRON)
    part(bp, "OverRailLow", CUBE, (0, 0, base - 40), (6, 2 * OPENING_HALF + 20, 6), IRON)
    outer = arc(bp, "OverArc", OPENING_HALF, base, 170, 8, 16)
    arc(bp, "OverArcIn", OPENING_HALF - 60, base, 110, 5, 12)
    for k in range(1, 16):
        y, z = outer[k]
        if abs(y) < 30:
            continue
        part(bp, f"OverBar{k:02d}", CUBE, (0, y, (base + z) / 2), (3, 3, z - base), IRON)
    for i in range(-5, 6):
        part(bp, f"OverDog{i + 5:02d}", CUBE, (0, i * 70, base - 20), (2.5, 2.5, 40), IRON)
    crown = base + 170
    part(bp, "CrestDisc", CYL, (0, 0, crown + 28), (46, 46, 5), IRON, (90, 0, 0))
    part(bp, "CrestRing", CYL, (0, 0, crown + 28), (30, 30, 7), TRIM, (90, 0, 0))
    part(bp, "CrestSpike", CONE, (0, 0, crown + 66), (12, 12, 30), IRON)
    part(bp, "Chain", CUBE, (0, 0, base - 70), (3, 3, 60), IRON)
    lantern(bp, "HangLantern", 0, 0, base - 210, 45)


def build_backlight(bp):
    light(bp, "GateGlow", (380, 0, LAND_Z + 320), 160, 2800, "(R=255,G=186,B=120,A=255)",
          shadows=True, scatter=4.0)


def build_trigger(bp):
    helper.add_component_to_blueprint(bp, BOX, "DoorTrigger", -120, 0, LAND_Z + 150, 0, 0, 0, ROOT)
    helper.set_component_property(bp, "DoorTrigger", "BoxExtent", f"(X=140,Y={OPENING_HALF - 15},Z=150)")


def main():
    bp = unreal.load_asset(BP_PATH)
    clear(bp)
    build_stairs(bp)
    build_pillars(bp)
    build_leaf(bp, "LeafL", 1)
    build_leaf(bp, "LeafR", -1)
    build_overthrow(bp)
    build_backlight(bp)
    build_trigger(bp)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(BP_PATH, only_if_is_dirty=False)
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/gate_result.json"
    listing = json.loads(helper.list_blueprint_components(bp))
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"components": len(listing.get("components", []))}, f)


main()
