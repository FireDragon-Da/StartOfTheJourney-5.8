"""Fills Lvl_TownBlock's streets with continuous rows of the town house Blueprints.

Run inside the Unreal editor with Lvl_TownBlock open:
    py exec(open(r'D:/StartOfTheJourney 5.8/Tools/TownBuilder/build_town_layout.py', encoding='utf-8').read())

Removes every actor in the Buildings outliner folder, then walks each facade line placing houses
shoulder to shoulder. Footprints are checked against roads, keep-out zones and already placed
houses, so block corners resolve themselves. Seeded, so reruns give the same town.
"""
import json
import random

import unreal

BP_DIR = "/Game/Inarchived/Town/Blueprints/"
MAT_DIR = "/Game/Inarchived/Town/Materials/"
FOLDER = "Buildings"
SEED = 1958
HOUSE_Z = 20.0

# Body footprint of each design: D along local X (front faces +X), W along local Y.
TYPES = {
    "Row": {"D": 800, "W": 700, "weight": 4.0},
    "Tall": {"D": 600, "W": 800, "weight": 3.5},
    "Wide": {"D": 1400, "W": 900, "weight": 1.6},
    "Shed": {"D": 500, "W": 400, "weight": 0.35},
}

# Wall / roof / shutter recolours per design: (material in the baked mesh, alternatives).
VARIANTS = {
    "Row": [("MI_TownBrick", ["MI_TownBrick", "MI_TownBrick", "MI_TownPlaster_Rose", "MI_TownPlaster_Warm"]),
            ("MI_TownRoof_Terracotta", ["MI_TownRoof_Terracotta", "MI_TownRoof_Terracotta", "MI_TownRoof_Slate"]),
            ("MI_TownShutter_Green", ["MI_TownShutter_Green", "MI_TownShutter_Blue"])],
    "Tall": [("MI_TownPlaster_Warm", ["MI_TownPlaster_Warm", "MI_TownPlaster_Stone", "MI_TownPlaster_Cool",
                                      "MI_TownPlaster_Rose"]),
             ("MI_TownRoof_Slate", ["MI_TownRoof_Slate", "MI_TownRoof_Slate", "MI_TownRoof_Terracotta"]),
             ("MI_TownShutter_Green", ["MI_TownShutter_Green", "MI_TownShutter_Blue"])],
    "Wide": [("MI_TownPlaster_Stone", ["MI_TownPlaster_Stone", "MI_TownPlaster_Warm", "MI_TownPlaster_Rose"]),
             ("MI_TownShutter_Green", ["MI_TownShutter_Green", "MI_TownShutter_Blue"])],
    "Shed": [("MI_TownPlaster_Rose", ["MI_TownPlaster_Rose", "MI_TownPlaster_Warm", "MI_TownPlaster_Cool"])],
}

# Roads including sidewalks: (xmin, xmax, ymin, ymax). Houses may touch but not enter these.
ROADS = [
    (-6130, -4870, -3000, 3000),   # west road
    (-5300, -2300, 1170, 2430),    # north link
    (-5300, -2300, -2430, -1170),  # south link
    (-2830, -1570, -2830, 2830),   # loop west
    (1570, 2830, -2830, 2830),     # loop east
    (-2830, 2830, 1570, 2830),     # loop north
    (-2830, 2830, -2830, -1570),   # loop south
    (-1570, 1570, -1570, 1570),    # plaza square
    (2300, 5900, -230, 1030),      # exit road
]

KEEPOUT = [
    (-4870, -4150, 2430, 3000),    # news stand corner square
    (-400, 400, 2830, 4230),       # evidence alley
    (3650, 4350, 1030, 1750),      # questioner's nook
    (5900, 9000, -1400, 2200),     # gate and the open land beyond it
]

# Facade lines in placement order: (label, axis, coord, lo, hi, facing, max_depth, z_scale range).
# axis "y": facade runs along Y at x=coord; axis "x": runs along X at y=coord.
SEGMENTS = [
    ("WestStrip", "y", -6130, -3000, 3000, "+x", 9999, (0.95, 1.18)),
    ("WestEndN", "x", 3000, -6130, -4150, "-y", 9999, (1.0, 1.2)),
    ("WestEndS", "x", -3000, -6130, -4870, "+y", 9999, (1.0, 1.2)),
    ("MidW", "y", -4870, -1170, 1170, "-x", 800, (0.95, 1.15)),
    ("MidE", "y", -2830, -1170, 1170, "+x", 800, (0.95, 1.15)),
    ("MidN", "x", 1170, -4870, -2830, "+y", 600, (0.95, 1.1)),
    ("MidS", "x", -1170, -4870, -2830, "-y", 600, (0.95, 1.1)),
    ("NWBlock", "x", 2430, -4870, -2830, "-y", 9999, (0.95, 1.2)),
    ("SWBlock", "x", -2430, -4870, -2830, "+y", 9999, (0.95, 1.2)),
    ("SWBlockW", "y", -4870, -3000, -2430, "-x", 9999, (0.95, 1.1)),
    ("NorthStrip", "x", 2830, -2830, 2830, "-y", 9999, (0.95, 1.2)),
    ("SouthStrip", "x", -2830, -2830, 2830, "+y", 9999, (0.95, 1.2)),
    ("NEBlockW", "y", 2830, 1030, 2830, "-x", 9999, (0.95, 1.2)),
    ("ExitN", "x", 1030, 2830, 5900, "-y", 9999, (0.95, 1.2)),
    ("SEBlockW", "y", 2830, -2830, -230, "-x", 9999, (0.95, 1.2)),
    ("ExitS", "x", -230, 2830, 5900, "+y", 9999, (0.95, 1.2)),
    # Taller second rows so the skyline behind each street reads as more town, not empty land.
    ("BackWest", "y", -7700, -3600, 3600, "+x", 9999, (1.15, 1.4)),
    ("BackNorth", "x", 4300, -4200, 3000, "-y", 9999, (1.15, 1.4)),
    ("BackSouth", "x", -4300, -4200, 3000, "+y", 9999, (1.15, 1.4)),
    ("BackNE", "y", 4400, 1800, 3600, "-x", 9999, (1.15, 1.35)),
    ("BackSE", "y", 4400, -3400, -1000, "-x", 9999, (1.15, 1.35)),
]

# Houses placed by hand first: the evidence alley is flanked by deep Wide houses and closed by a Row,
# and the four corners of the square get a house each so the roundabout reads as a compact
# cross-shaped plaza with the loop road lined on both sides.
FIXED = [
    ("AlleyW", "Wide", (-850, 2830 + 700), -90, 1.0),
    ("AlleyE", "Wide", (850, 2830 + 700), -90, 1.05),
    ("AlleyEnd", "Row", (0, 4230 + 400), -90, 1.1),
    ("SquareNW", "Tall", (-1270, 1135), 180, 1.08),
    ("SquareNE", "Row", (1135, 1170), 90, 1.12),
    ("SquareSE", "Tall", (1270, -1135), 0, 1.0),
    ("SquareSW", "Row", (-1135, -1170), -90, 1.05),
]

YAW = {"+x": 0.0, "-x": 180.0, "+y": 90.0, "-y": -90.0}


def footprint(cx, cy, yaw, D, W):
    if abs(yaw) < 1 or abs(abs(yaw) - 180) < 1:
        return (cx - D / 2, cx + D / 2, cy - W / 2, cy + W / 2)
    return (cx - W / 2, cx + W / 2, cy - D / 2, cy + D / 2)


def overlaps(a, b, tol=4.0):
    return a[0] < b[1] - tol and a[1] > b[0] + tol and a[2] < b[3] - tol and a[3] > b[2] + tol


class Layout:
    def __init__(self):
        self.rng = random.Random(SEED)
        self.occupied = [r for r in ROADS] + [r for r in KEEPOUT]
        self.placements = []

    def free(self, rect):
        return not any(overlaps(rect, o) for o in self.occupied)

    def add(self, label, kind, cx, cy, yaw, zs):
        t = TYPES[kind]
        rect = footprint(cx, cy, yaw, t["D"], t["W"])
        self.occupied.append(rect)
        self.placements.append({"label": label, "kind": kind, "loc": (cx, cy), "yaw": yaw, "zs": round(zs, 3)})

    def pick_order(self, prev, max_depth):
        pool = [k for k, t in TYPES.items() if t["D"] <= max_depth]
        order = []
        while pool:
            weights = [TYPES[k]["weight"] * (0.25 if k == prev else 1.0) for k in pool]
            k = self.rng.choices(pool, weights)[0]
            order.append(k)
            pool.remove(k)
        return order

    def fill(self, seg):
        label, axis, coord, lo, hi, facing, max_depth, zr = seg
        sign = 1.0 if facing[0] == "+" else -1.0
        yaw = YAW[facing]
        pos, prev, n = float(lo), None, 0
        while hi - pos >= min(t["W"] for t in TYPES.values()):
            placed = False
            for kind in self.pick_order(prev, max_depth):
                t = TYPES[kind]
                if pos + t["W"] > hi + 10:
                    continue
                along = pos + t["W"] / 2
                depth_c = coord - sign * t["D"] / 2
                cx, cy = (depth_c, along) if axis == "y" else (along, depth_c)
                if not self.free(footprint(cx, cy, yaw, t["D"], t["W"])):
                    continue
                n += 1
                self.add(f"{label}_{n:02d}", kind, cx, cy, yaw, self.rng.uniform(*zr))
                pos += t["W"]
                prev, placed = kind, True
                break
            if not placed:
                pos += 50


def plan():
    lay = Layout()
    for label, kind, (cx, cy), yaw, zs in FIXED:
        lay.add(label, kind, cx, cy, yaw, zs)
    for seg in SEGMENTS:
        lay.fill(seg)
    return lay


def apply(lay):
    actors_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in actors_sub.get_all_level_actors():
        if str(a.get_folder_path()) == FOLDER:
            actors_sub.destroy_actor(a)

    classes = {k: unreal.EditorAssetLibrary.load_blueprint_class(f"{BP_DIR}BP_TownHouse_{k}") for k in TYPES}
    mats = {}

    def mat(name):
        if name not in mats:
            mats[name] = unreal.load_asset(f"{MAT_DIR}{name}.{name}")
        return mats[name]

    rng = random.Random(SEED + 1)
    for p in lay.placements:
        rot = unreal.Rotator()
        rot.yaw = p["yaw"]
        a = actors_sub.spawn_actor_from_class(classes[p["kind"]],
                                              unreal.Vector(p["loc"][0], p["loc"][1], HOUSE_Z), rot)
        a.set_actor_label(f"House_{p['label']}")
        a.set_folder_path(FOLDER)
        a.set_actor_scale3d(unreal.Vector(1.0, 1.0, p["zs"]))
        comp = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        comp.modify()
        slots = [m.get_name() if m else "" for m in comp.get_materials()]
        for source, choices in VARIANTS[p["kind"]]:
            pick = rng.choice(choices)
            if pick == source or source not in slots:
                continue
            comp.set_material(slots.index(source), mat(pick))


lay = plan()
apply(lay)
counts = {}
for p in lay.placements:
    counts[p["kind"]] = counts.get(p["kind"], 0) + 1
out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/layout_result.json"
with open(out, "w") as f:
    json.dump({"total": len(lay.placements), "counts": counts, "placements": lay.placements}, f, indent=0)
