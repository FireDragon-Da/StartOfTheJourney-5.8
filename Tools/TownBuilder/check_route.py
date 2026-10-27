"""Sweeps a player-sized capsule along the gameplay route and reports anything blocking it.

Writes Saved/TownBuilder/route_check.json.
"""
import json

import unreal

OUT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/route_check.json"

RADIUS = 34.0
HALF_HEIGHT = 60.0
Z = 150.0  # capsule bottom at ~90, above kerbs and puddles so only real obstacles register

ROUTE = [
    ("WakeUp", -5500, -200),
    ("NewsCrosswalk", -5500, 1800),
    ("NewsStandFront", -4900, 2200),
    ("LinkN", -3800, 1800),
    ("LoopW", -2200, 1800),
    ("NorthRoad", -2200, 2200),
    ("AlleyMouth", 0, 2200),
    ("Evidence", 0, 3800),
    ("AlleyBack", 0, 2200),
    ("LoopNE", 2200, 2200),
    ("ExitJunction", 2200, 400),
    ("ExitMid", 4000, 400),
    ("QuestionerFront", 4000, 1100),
    ("ExitBack", 4000, 400),
    ("GateFront", 5800, 400),
    ("ExitReturn", 2200, 400),
    ("PlazaLoopS", 2200, -2200),
    ("PlazaLoopSW", -2200, -2200),
    ("LoopWBack", -2200, 1800),
]


SHOULD_BLOCK = [
    (("WestRoad", -5500, 1000), ("WestHouses", -7500, 1000)),
    (("NorthRoad", 0, 2200), ("NWBlock", -1000, 3200)),
    (("ExitMid", 3300, 400), ("ExitSouthRow", 3300, -1500)),
]


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    results = []
    for (name_a, xa, ya), (name_b, xb, yb) in list(zip(ROUTE, ROUTE[1:])) + SHOULD_BLOCK:
        start = unreal.Vector(xa, ya, Z)
        end = unreal.Vector(xb, yb, Z)
        hit = unreal.SystemLibrary.capsule_trace_single(
            world, start, end, RADIUS, HALF_HEIGHT,
            unreal.TraceTypeQuery.ECC_VISIBILITY, False, [],
            unreal.DrawDebugTrace.NONE, True)
        entry = {"from": name_a, "to": name_b, "blocked": False}
        if hit:
            t = hit.to_tuple()
            blocking = t[0]
            if blocking:
                actor = next((v for v in t if isinstance(v, unreal.Actor)), None)
                comp = next((v for v in t if isinstance(v, unreal.PrimitiveComponent)), None)
                loc = next((v for v in t if isinstance(v, unreal.Vector)), None)
                entry.update(
                    blocked=True,
                    location=[round(loc.x), round(loc.y), round(loc.z)] if loc else None,
                    actor=actor.get_actor_label() if actor else None,
                    component=comp.get_name() if comp else None,
                )
        results.append(entry)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)


main()
