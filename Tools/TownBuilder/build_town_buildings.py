"""Rebuilds the Unarchived town house Blueprints from engine primitives.

Run inside the Unreal editor:
    py "D:/StartOfTheJourney 5.8/Tools/TownBuilder/build_town_buildings.py" [Shed Row Tall Wide]

Every house keeps its footprint and faces local +X (front facade width runs along Y),
so the instances already placed in Lvl_TownBlock update in place.
"""
import json
import math
import sys

import unreal

BP_DIR = "/Game/Inarchived/Town/Blueprints/"
MAT_DIR = "/Game/Inarchived/Town/Materials/"
CUBE = "/Engine/BasicShapes/Cube.Cube"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere.Sphere"
SMC = "/Script/Engine.StaticMeshComponent"
ROOT = "DefaultSceneRoot"
SQRT2 = math.sqrt(2.0)


def _m(name):
    return f"{MAT_DIR}{name}.{name}"


M = {
    "warm": _m("MI_TownPlaster_Warm"),
    "cool": _m("MI_TownPlaster_Cool"),
    "stone": _m("MI_TownPlaster_Stone"),
    "rose": _m("MI_TownPlaster_Rose"),
    "trim": _m("MI_TownTrim"),
    "base": _m("MI_TownStoneBase"),
    "brick": _m("MI_TownBrick"),
    "terracotta": _m("MI_TownRoof_Terracotta"),
    "slate": _m("MI_TownRoof_Slate"),
    "wood": _m("MI_TownWood"),
    "green": _m("MI_TownShutter_Green"),
    "blue": _m("MI_TownShutter_Blue"),
    "awning_red": _m("MI_TownAwning_Red"),
    "awning_cream": _m("MI_TownAwning_Cream"),
    "lit": _m("M_TownWindow"),
    "dark": _m("M_TownGlassDark"),
    "metal": _m("M_TownMetal"),
    "leaf": _m("M_TownFoliage"),
}

# Deterministic mix of lit and unlit panes so facades read as lived-in at dusk.
LIT_PATTERN = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1]


class House:
    def __init__(self, depth, width):
        self.D = float(depth)
        self.W = float(width)
        self.parts = []
        self._counts = {}
        self._lit = 0

    # ---------------------------------------------------------------- primitives
    def _name(self, base):
        n = self._counts.get(base, 0) + 1
        self._counts[base] = n
        return f"{base}_{n:02d}"

    def add(self, base, mesh, loc, scale, mat, rot=(0.0, 0.0, 0.0)):
        self.parts.append((self._name(base), mesh, tuple(loc), tuple(rot), tuple(scale), mat))

    def box(self, base, center, size, mat, rot=(0.0, 0.0, 0.0)):
        self.add(base, CUBE, center, [s / 100.0 for s in size], mat, rot)

    def cyl(self, base, center, dia, length, mat, rot=(0.0, 0.0, 0.0)):
        self.add(base, CYL, center, (dia / 100.0, dia / 100.0, length / 100.0), mat, rot)

    def sphere(self, base, center, dia, mat):
        self.add(base, SPHERE, center, (dia / 100.0,) * 3, mat)

    def glass(self, force=None):
        if force is not None:
            return M["lit"] if force else M["dark"]
        lit = LIT_PATTERN[self._lit % len(LIT_PATTERN)]
        self._lit += 1
        return M["lit"] if lit else M["dark"]

    # ---------------------------------------------------------------- facade space
    # face: F = +X (street front), B = -X, R = +Y, L = -Y.
    # u runs along the facade, z is height, out is distance in front of the wall plane.
    def fpos(self, face, u, z, out):
        d2, w2 = self.D / 2.0, self.W / 2.0
        if face == "F":
            return (d2 + out, u, z)
        if face == "B":
            return (-d2 - out, -u, z)
        if face == "R":
            return (-u, w2 + out, z)
        return (u, -w2 - out, z)

    def fbox(self, base, face, u, z, proud, w, h, mat, embed=4.0):
        """Box on a facade spanning from `embed` cm inside the wall to `proud` cm in front of it."""
        t = proud + embed
        loc = self.fpos(face, u, z, (proud - embed) / 2.0)
        size = (t, w, h) if face in "FB" else (w, t, h)
        self.box(base, loc, size, mat)

    def fsphere(self, base, face, u, z, out, dia, mat):
        self.sphere(base, self.fpos(face, u, z, out), dia, mat)

    def fdisc(self, base, face, u, z, proud, dia, mat, embed=4.0):
        """Cylinder whose axis follows the facade normal (round windows, medallions)."""
        t = proud + embed
        rot = (90.0, 0.0, 0.0) if face in "FB" else (0.0, 0.0, 90.0)
        self.cyl(base, self.fpos(face, u, z, (proud - embed) / 2.0), dia, t, mat, rot)

    # ---------------------------------------------------------------- body & trim
    def body(self, height, wall, plinth_h=70.0):
        # Houses sit at sidewalk height in the level; the footing hides the step down to bare ground.
        self.box("Footing", (0, 0, -30), (self.D + 16, self.W + 16, 60), M["base"])
        self.box("Walls", (0, 0, height / 2.0), (self.D, self.W, height), M[wall])
        if plinth_h > 0:
            self.box("Plinth", (0, 0, plinth_h / 2.0), (self.D + 16, self.W + 16, plinth_h), M["base"])
            self.box("PlinthCap", (0, 0, plinth_h + 4), (self.D + 22, self.W + 22, 8), M["trim"])

    def band(self, z, h=14.0, grow=18.0, mat="trim"):
        self.box("StringCourse", (0, 0, z), (self.D + grow, self.W + grow, h), M[mat])

    def cornice(self, top):
        D, W = self.D, self.W
        self.box("CorniceFrieze", (0, 0, top - 34), (D + 10, W + 10, 14), M["trim"])
        self.box("Cornice", (0, 0, top - 12), (D + 28, W + 28, 24), M["trim"])
        self.box("CorniceCap", (0, 0, top + 5), (D + 48, W + 48, 12), M["trim"])

    def quoins(self, top, bottom=0.0, mat="trim", block=36.0, gap=8.0, proud=5.0, long=54.0, short=32.0):
        D, W = self.D, self.W
        n = int((top - bottom) // (block + gap))
        for i in range(n):
            z = bottom + gap + i * (block + gap) + block / 2.0
            sx_len, sy_len = (long, short) if i % 2 == 0 else (short, long)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    self.box(
                        "Quoin",
                        (sx * (D / 2 - sx_len / 2 + proud), sy * (W / 2 - sy_len / 2 + proud), z),
                        (sx_len, sy_len, block),
                        M[mat],
                    )

    def pilasters_front(self, us, bottom, top, w=36.0, proud=10.0, mat="trim"):
        for u in us:
            self.fbox("Pilaster", "F", u, (bottom + top) / 2.0, proud, w, top - bottom, M[mat])
            self.fbox("PilasterCap", "F", u, top - 8, proud + 6, w + 14, 16, M[mat])
            self.fbox("PilasterBase", "F", u, bottom + 12, proud + 5, w + 12, 24, M[mat])

    def downpipe(self, face, u, top):
        x, y, _ = self.fpos(face, u, 0, 12)
        self.cyl("Downpipe", (x, y, top / 2.0 + 10), 12, top - 20, M["metal"])
        for z in (top * 0.3, top * 0.7):
            self.fbox("PipeClamp", face, u, z, 16, 18, 6, M["metal"])
        self.fbox("PipeShoe", face, u, 20, 26, 14, 14, M["metal"])

    # ---------------------------------------------------------------- openings
    def window(self, face, u, z0, w, h, shutters=None, flowers=False, head="cap",
               bars=True, sill=True, lit=None):
        zc = z0 + h / 2.0
        self.fbox("WinSurround", face, u, zc, 5, w + 24, h + 24, M["trim"])
        self.fbox("WinReveal", face, u, zc, 6, w + 4, h + 4, M["wood"])
        self.fbox("WinGlass", face, u, zc, 7, w, h, self.glass(lit))
        if bars:
            self.fbox("WinMullion", face, u, zc, 9, 5, h, M["wood"])
            self.fbox("WinTransom", face, u, z0 + h * 0.66, 9, w, 5, M["wood"])
        if sill:
            self.fbox("WinSill", face, u, z0 - 18, 16, w + 44, 10, M["trim"])
            for s in (-1, 1):
                self.fbox("SillBracket", face, u + s * (w / 2 + 12), z0 - 30, 10, 10, 16, M["trim"])
        if head == "cap":
            self.fbox("WinCap", face, u, z0 + h + 20, 13, w + 50, 12, M["trim"])
            self.fbox("WinFrieze", face, u, z0 + h + 10, 8, w + 30, 10, M["trim"])
        elif head == "key":
            self.fbox("WinLintel", face, u, z0 + h + 14, 8, w + 30, 12, M["trim"])
            self.fbox("WinKeystone", face, u, z0 + h + 18, 12, 22, 30, M["trim"])
        elif head == "pediment":
            self.fbox("WinCap", face, u, z0 + h + 20, 13, w + 50, 12, M["trim"])
            self.fbox("WinPediment", face, u, z0 + h + 36, 11, w + 20, 20, M["trim"])
            self.fbox("WinPediment", face, u, z0 + h + 52, 9, w * 0.55, 14, M["trim"])
        if shutters:
            sw = w * 0.5
            for s in (-1, 1):
                su = u + s * (w / 2 + 13 + sw / 2)
                self.fbox("Shutter", face, su, zc, 6, sw, h + 8, M[shutters])
                for k in range(1, 4):
                    self.fbox("ShutterRail", face, su, z0 + h * k / 4.0, 8, sw - 6, 4, M[shutters])
        if flowers:
            self.fbox("FlowerBox", face, u, z0 - 44, 30, w + 6, 22, M["wood"])
            n = max(3, int(w // 30))
            for i in range(n):
                fu = u - w / 2 + 15 + i * (w - 30) / max(1, n - 1)
                self.fsphere("Flowers", face, fu, z0 - 28, 16, 30, M["leaf"])

    def french_window(self, face, u, z0, w, h, shutters=None):
        self.window(face, u, z0, w, h, shutters=shutters, head="pediment", sill=False)

    def door(self, face, u, w=120.0, h=240.0, z0=0.0, canopy=True, lamp=True, lamp_side=1):
        zc = z0 + h / 2.0
        self.fbox("DoorSurround", face, u, zc + 8, 7, w + 40, h + 16, M["trim"])
        self.fbox("DoorKeystone", face, u, z0 + h + 10, 12, 26, 34, M["trim"])
        self.fbox("DoorLeaf", face, u, z0 + (h - 44) / 2.0, 9, w, h - 44, M["wood"])
        self.fbox("DoorTransom", face, u, z0 + h - 20, 9, w, 36, self.glass(True))
        self.fbox("DoorTransomBar", face, u, z0 + h - 20, 11, 5, 36, M["wood"])
        for s in (-1, 1):
            pu = u + s * w / 4.0
            self.fbox("DoorPanel", face, pu, z0 + (h - 44) * 0.28, 12, w / 2 - 20, (h - 44) * 0.34, M["wood"])
            self.fbox("DoorPanel", face, pu, z0 + (h - 44) * 0.72, 12, w / 2 - 20, (h - 44) * 0.36, M["wood"])
        self.fsphere("DoorKnob", face, u + w / 2 - 14, z0 + h * 0.45, 13, 8, M["metal"])
        self.fbox("DoorStep", face, u, z0 + 8, 46, w + 70, 16, M["base"])
        if canopy:
            self.fbox("Canopy", face, u, z0 + h + 50, 76, w + 100, 10, M["metal"])
            self.fbox("CanopyFascia", face, u, z0 + h + 42, 80, w + 100, 16, M["metal"], embed=-72)
            for s in (-1, 1):
                self.fbox("CanopyBracket", face, u + s * (w / 2 + 40), z0 + h + 26, 64, 6, 42, M["metal"])
        if lamp:
            lu = u + lamp_side * (w / 2 + 62)
            self.fbox("WallLampPlate", face, lu, z0 + h - 30, 4, 16, 26, M["metal"])
            self.fbox("WallLampArm", face, lu, z0 + h - 20, 34, 5, 5, M["metal"])
            self.fsphere("WallLampGlobe", face, lu, z0 + h - 38, 34, 22, M["lit"])

    def balcony(self, face, u, z_floor, w, depth=70.0):
        self.fbox("BalconySlab", face, u, z_floor - 7, depth, w, 14, M["trim"])
        self.fbox("BalconySlabEdge", face, u, z_floor - 18, depth + 4, w + 8, 8, M["trim"])
        for s in (-1, 1):
            self.fbox("BalconyCorbel", face, u + s * (w / 2 - 18), z_floor - 40, depth - 18, 14, 36, M["trim"])
        rail_h = 95.0
        edge = -(depth - 5)
        self.fbox("BalconyRail", face, u, z_floor + rail_h, depth, w, 6, M["metal"], embed=edge)
        self.fbox("BalconyRail", face, u, z_floor + 10, depth, w, 5, M["metal"], embed=edge)
        n = int(w // 18)
        for i in range(n + 1):
            bu = u - w / 2 + 3 + i * (w - 6) / n
            self.fbox("Baluster", face, bu, z_floor + rail_h / 2, depth - 1, 3, rail_h, M["metal"], embed=edge + 3)
        for s in (-1, 1):
            su = u + s * (w / 2 - 3)
            self.fbox("BalconySideRail", face, su, z_floor + rail_h, depth, 5, 6, M["metal"])
            for k in range(1, 4):
                self.fbox("BalconySideBar", face, su, z_floor + rail_h / 2, depth * k / 4.0 + 2, 3, rail_h, M["metal"],
                          embed=-(depth * k / 4.0 - 2))

    # ---------------------------------------------------------------- roofs
    def gable(self, cx, cy, eave_z, span, length, along, mat, overhang=35.0, t=16.0,
              fill_mat=None, ridge=True):
        """45-degree gable roof. `span` is crossed by the slopes, `length` runs along the ridge."""
        a = math.radians(45.0)
        rise = span / 2.0
        run = span / 2.0 + overhang
        slab_len = run / math.cos(a) + t
        h = run / 2.0 - (t / 2.0) * math.cos(a)
        hc = h - math.sin(a) * t / 2.0
        zc = eave_z + rise - h - math.cos(a) * t / 2.0
        roof_len = length + 2 * overhang
        for s in (1, -1):
            if along == "Y":
                self.box("RoofSlope", (cx + s * hc, cy, zc), (slab_len, roof_len, t), mat, (-45.0 * s, 0.0, 0.0))
            else:
                self.box("RoofSlope", (cx, cy + s * hc, zc), (slab_len, roof_len, t), mat, (-45.0, 90.0 * s, 0.0))
        if fill_mat:
            # Shrunk so its faces sit under the roof slabs instead of z-fighting with them.
            d = span / SQRT2 - t * 0.9
            if along == "Y":
                self.box("GableFill", (cx, cy, eave_z), (d, length, d), fill_mat, (45.0, 0.0, 0.0))
            else:
                self.box("GableFill", (cx, cy, eave_z), (length, d, d), fill_mat, (0.0, 0.0, 45.0))
        if ridge:
            rot = (0.0, 0.0, 90.0) if along == "Y" else (90.0, 0.0, 0.0)
            self.cyl("RidgeCap", (cx, cy, eave_z + rise + t * 0.45), t * 1.4, roof_len + 6, mat, rot)
        return rise

    def gutter_y(self, x, eave_z, overhang, length):
        self.cyl("Gutter", (x, 0, eave_z - overhang - 6), 14, length, M["metal"], (0.0, 0.0, 90.0))

    def chimney(self, x, y, z_bottom, top, w=70.0, d=90.0, mat="brick"):
        hgt = top - z_bottom
        self.box("Chimney", (x, y, z_bottom + hgt / 2.0), (d, w, hgt), M[mat])
        self.box("ChimneyBand", (x, y, top - 30), (d + 10, w + 10, 10), M["trim"])
        self.box("ChimneyCap", (x, y, top + 6), (d + 18, w + 18, 12), M["trim"])
        for k in (-1, 1):
            self.cyl("ChimneyPot", (x + k * d / 5.0, y, top + 30), 20, 36, M["terracotta"])

    def dormer(self, sx, y, eave_z, w=130.0, h=150.0, wall="warm", roof="slate"):
        """Gabled dormer on a 45-degree ridge-along-Y roof, facing sx*X."""
        D = self.D
        xf = D / 2.0 - 70.0
        z0 = eave_z + 50.0
        x_back = 20.0
        body_len = xf - x_back
        bx = sx * (x_back + body_len / 2.0)
        self.box("DormerBody", (bx, y, z0 + h / 2.0), (body_len, w, h), M[wall])
        for s in (-1, 1):
            self.box("DormerCheek", (bx, y + s * (w / 2.0 + 4), z0 + h / 2.0), (body_len, 8, h), M["trim"])
        face_x = sx * xf
        self.box("DormerFrame", (face_x + sx * 3, y, z0 + h / 2.0 + 5), (10, w - 26, h - 30), M["trim"])
        self.box("DormerGlass", (face_x + sx * 6, y, z0 + h / 2.0 + 5), (6, w - 50, h - 54), self.glass())
        self.box("DormerMullion", (face_x + sx * 9, y, z0 + h / 2.0 + 5), (4, 5, h - 54), M["wood"])
        self.box("DormerSill", (face_x + sx * 10, y, z0 + 16), (22, w - 10, 8), M["trim"])
        self.gable(sx * (x_back + (xf - x_back) / 2.0 + 10), y, z0 + h, w, xf - x_back + 10, "X",
                   M[roof], overhang=15.0, t=10.0, fill_mat=M["trim"], ridge=False)


# ======================================================================== designs
def design_shed():
    h = House(500, 400)
    top = 300.0
    h.body(top, "rose", plinth_h=50)
    h.quoins(top, bottom=58, block=30, gap=8, long=40, short=26)
    h.box("EaveBand", (0, 0, top - 8), (h.D + 20, h.W + 20, 16), M["trim"])
    h.door("F", -85, w=95, h=205, canopy=False, lamp=True, lamp_side=1)
    h.window("F", 95, 115, 90, 105, flowers=True, head="key")
    h.window("R", 0, 120, 80, 100, shutters="blue", head="key")
    h.window("L", 0, 120, 80, 100, shutters="blue", head="key")
    h.window("B", 0, 130, 70, 90, head="key", bars=False)
    h.gable(0, 0, top, h.D, h.W, "Y", M["terracotta"], overhang=35, t=14, fill_mat=M["rose"])
    h.gutter_y(h.D / 2 + 29, top, 35, h.W + 70)
    h.downpipe("F", h.W / 2 - 22, top - 30)
    h.chimney(-120, 110, top, top + 310, w=55, d=70, mat="brick")
    h.fbox("WoodPile", "L", 150, 45, 60, 120, 90, M["wood"])
    h.fbox("WoodPileRoof", "L", 150, 96, 70, 140, 8, M["terracotta"])
    return h


def design_row():
    h = House(800, 700)
    top = 720.0
    h.body(top, "brick", plinth_h=60)
    h.quoins(top, bottom=70)
    h.band(360, h=16)
    h.box("EaveBand", (0, 0, top - 10), (h.D + 24, h.W + 24, 20), M["trim"])
    h.box("EaveDentils", (0, 0, top - 28), (h.D + 12, h.W + 12, 10), M["trim"])
    h.door("F", -190, w=120, h=235, canopy=True, lamp=True, lamp_side=1)
    h.window("F", 150, 100, 130, 170, shutters="green", flowers=True, head="cap")
    for u in (-170, 170):
        h.window("F", u, 440, 110, 180, shutters="green", flowers=True, head="cap")
    for face in ("R", "L", "B"):
        for u in (-200, 200) if face != "B" else (-170, 170):
            h.window(face, u, 110, 100, 160, head="key")
            h.window(face, u, 450, 100, 170, head="key")
    rise = h.gable(0, 0, top, h.W, h.D, "X", M["terracotta"], overhang=35, t=16, fill_mat=M["brick"])
    # Street-facing gable: round attic window and raking trim.
    oz = top + rise * 0.42
    h.fdisc("OculusFrame", "F", 0, oz, 6, 124, M["trim"])
    h.fdisc("OculusGlass", "F", 0, oz, 9, 90, h.glass(True))
    h.fbox("OculusBar", "F", 0, oz, 11, 5, 90, M["wood"])
    h.fbox("OculusBar", "F", 0, oz, 11, 90, 5, M["wood"])
    h.fdisc("OculusFrame", "B", 0, oz, 6, 110, M["trim"])
    h.fdisc("OculusGlass", "B", 0, oz, 9, 76, h.glass(False))
    h.fbox("GableBase", "F", 0, top + 8, 12, h.W + 10, 14, M["trim"])
    h.chimney(-220, 0, top + 100, top + rise + 130, w=80, d=80, mat="brick")
    for s in (-1, 1):
        h.cyl("Gutter", (0, s * (h.W / 2 + 29), top - 41), 14, h.D + 70, M["metal"], (90.0, 0.0, 0.0))
        h.downpipe("F", s * (h.W / 2 - 24), top - 40)
    return h


def design_tall():
    h = House(600, 800)
    top = 1020.0
    h.body(top, "warm", plinth_h=70)
    h.quoins(top, bottom=80)
    h.band(340, h=18)
    h.band(680, h=14)
    h.cornice(top)
    h.door("F", 0, w=130, h=245, canopy=True, lamp=False)
    for u in (-235, 235):
        h.window("F", u, 100, 100, 180, shutters="green", flowers=True, head="cap")
        h.window("F", u, 440, 100, 180, shutters="green", flowers=True, head="pediment")
        h.window("F", u, 780, 100, 165, shutters="green", head="key")
    h.french_window("F", 0, 435, 110, 205, shutters="green")
    h.balcony("F", 0, 430, 230, depth=72)
    h.window("F", 0, 780, 100, 165, shutters="green", flowers=True, head="key")
    for face in ("R", "L"):
        for z0 in (110, 450, 790):
            h.window(face, 0, z0, 100, 160, head="key")
    for u in (-235, 0, 235):
        for z0 in (110, 450, 790):
            h.window("B", u, z0, 90, 160, head="key", bars=False)
    rise = h.gable(0, 0, top + 12, h.D, h.W, "Y", M["slate"], overhang=40, t=16, fill_mat=M["warm"])
    for y in (-200, 200):
        h.dormer(1, y, top + 12, w=130, h=150, wall="warm", roof="slate")
    h.dormer(-1, 0, top + 12, w=130, h=150, wall="warm", roof="slate")
    for y in (-(h.W / 2 - 60), h.W / 2 - 60):
        h.chimney(0, y, top, top + 12 + rise + 110, w=70, d=100, mat="brick")
    h.gutter_y(h.D / 2 + 32, top + 12, 40, h.W + 80)
    h.gutter_y(-(h.D / 2 + 32), top + 12, 40, h.W + 80)
    for s in (-1, 1):
        h.downpipe("F", s * (h.W / 2 - 24), top - 40)
    return h


def design_wide():
    h = House(1400, 900)
    top = 1100.0
    h.body(top, "stone", plinth_h=0)
    h.quoins(top, bottom=430, mat="trim")
    # Shop ground floor.
    h.fbox("ShopBase", "F", 0, 30, 6, h.W - 20, 60, M["base"])
    h.pilasters_front((-430, -150, 150, 430), 0, 420, w=40, proud=12, mat="base")
    for u in (-290, 290):
        h.fbox("DisplayFrame", "F", u, 225, 8, 250, 290, M["wood"])
        h.fbox("DisplayGlass", "F", u, 230, 10, 226, 250, M["lit"])
        for k in (-1, 1):
            h.fbox("DisplayMullion", "F", u + k * 76, 230, 12, 6, 250, M["wood"])
        h.fbox("DisplayTransom", "F", u, 300, 12, 226, 6, M["wood"])
        h.fbox("DisplayStall", "F", u, 52, 12, 250, 70, M["wood"])
        h.fbox("DisplaySill", "F", u, 92, 16, 262, 8, M["trim"])
    h.fbox("ShopDoorFrame", "F", 0, 150, 8, 170, 300, M["wood"])
    h.fbox("ShopDoorGlass", "F", 0, 140, 10, 110, 250, M["lit"])
    h.fbox("ShopDoorBar", "F", 0, 140, 12, 6, 250, M["wood"])
    h.fbox("ShopDoorTransom", "F", 0, 290, 12, 150, 20, M["wood"])
    h.fbox("DoorStep", "F", 0, 8, 46, 200, 16, M["base"])
    # Sign fascia and cornice over the shop.
    h.fbox("Fascia", "F", 0, 372, 16, h.W - 40, 62, M["wood"])
    h.fbox("FasciaTrim", "F", 0, 404, 20, h.W - 30, 8, M["trim"])
    h.fbox("FasciaTrim", "F", 0, 340, 20, h.W - 30, 6, M["trim"])
    h.fbox("SignLetters", "F", 0, 372, 18, 320, 24, M["awning_cream"])
    h.band(430, h=24, grow=30)
    # Striped awnings over the display windows.
    a = math.radians(25.0)
    proj = 150.0
    slope_len = proj / math.cos(a)
    stripes = 7
    for u in (-290, 290):
        sw = 260.0 / stripes
        for i in range(stripes):
            su = u - 130 + sw / 2 + i * sw
            mat = M["awning_red"] if i % 2 == 0 else M["awning_cream"]
            h.box("AwningStripe", (h.D / 2 + proj / 2, su, 330 - proj * math.tan(a) / 2), (slope_len, sw, 5),
                  mat, (-25.0, 0.0, 0.0))
            h.box("AwningValance", (h.D / 2 + proj - 2, su, 330 - proj * math.tan(a) - 14), (4, sw, 28), mat)
        h.box("AwningBar", (h.D / 2 + 4, u, 334), (10, 270, 8), M["metal"])
        for k in (-1, 1):
            h.box("AwningArm", (h.D / 2 + proj / 2, u + k * 128, 330 - proj * math.tan(a) / 2 - 4),
                  (slope_len, 4, 4), M["metal"], (-25.0, 0.0, 0.0))
    # Upper floors, street front.
    h.band(760, h=14)
    for u in (-280, 0, 280):
        h.french_window("F", u, 450, 100, 215, shutters="green")
        h.balcony("F", u, 445, 180, depth=62)
        h.window("F", u, 795, 100, 195, shutters="green", flowers=True, head="cap")
    for u in (-150, 150):
        h.fbox("Medallion", "F", u, 610, 8, 40, 40, M["trim"])
    # Side and back facades.
    for face in ("R", "L"):
        for u in (-520, -260, 0, 260, 520):
            h.window(face, u, 130, 100, 190, head="key")
            h.window(face, u, 470, 100, 200, head="cap")
            h.window(face, u, 800, 100, 185, head="key")
    for u in (-300, 0, 300):
        h.window("B", u, 130, 100, 190, head="key", bars=False)
        h.window("B", u, 470, 100, 200, head="key")
        h.window("B", u, 800, 100, 185, head="key")
    h.cornice(top)
    # Parapet: balustrade to the street, solid on the other three sides.
    pz = top + 11
    D, W = h.D, h.W
    for s in (-1, 1):
        h.box("Parapet", (0, s * (W / 2 - 2), pz + 45), (D - 4, 24, 90), M["stone"])
        h.box("ParapetCoping", (0, s * (W / 2 - 2), pz + 94), (D + 4, 34, 10), M["trim"])
    h.box("Parapet", (-(D / 2 - 2), 0, pz + 45), (24, W - 4, 90), M["stone"])
    h.box("ParapetCoping", (-(D / 2 - 2), 0, pz + 94), (34, W + 4, 10), M["trim"])
    fx = D / 2 - 12
    h.box("BalustradeBase", (fx, 0, pz + 8), (30, W - 4, 16), M["trim"])
    h.box("BalustradeRail", (fx, 0, pz + 84), (34, W + 4, 12), M["trim"])
    for y in (-W / 2 + 18, -150, 150, W / 2 - 18):
        h.box("BalustradePost", (fx, y, pz + 45), (34, 34, 78), M["trim"])
    n = 26
    for i in range(n):
        y = -W / 2 + 40 + i * (W - 80) / (n - 1)
        if any(abs(y - p) < 26 for p in (-150, 150)):
            continue
        h.cyl("Baluster", (fx, y, pz + 46), 14, 62, M["trim"])
    # Roof furniture.
    h.box("RoofSlab", (0, 0, pz + 2), (D - 20, W - 20, 4), M["slate"])
    h.box("StairHut", (-350, -200, pz + 120), (260, 300, 240), M["stone"])
    h.box("StairHutCap", (-350, -200, pz + 246), (290, 330, 12), M["trim"])
    h.box("StairHutDoor", (-219, -200, pz + 95), (6, 90, 190), M["wood"])
    for x, y in ((-500, 330), (200, -330), (450, 330)):
        h.chimney(x, y, pz, pz + 230, w=70, d=110, mat="brick")
    for s in (-1, 1):
        h.downpipe("F", s * (W / 2 - 24), top - 40)
    return h


DESIGNS = {
    "Shed": design_shed,
    "Row": design_row,
    "Tall": design_tall,
    "Wide": design_wide,
}


# ======================================================================== apply
def _vec(v):
    return f"(X={v[0]:.4f},Y={v[1]:.4f},Z={v[2]:.4f})"


MESH_DIR = "/Game/Inarchived/Town/Meshes/"
BAKE_OFFSET = unreal.Vector(0.0, 0.0, -50000.0)


def _rot(p, y, r):
    rot = unreal.Rotator()
    rot.pitch, rot.yaw, rot.roll = p, y, r
    return rot


def bake_mesh(key, house):
    """Spawns every part as a StaticMeshActor below the map and merges them into one Nanite mesh."""
    actors_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    meshes = {p: unreal.load_asset(p) for p in (CUBE, CYL, SPHERE)}
    mats = {}
    temp = []
    for _name, mesh, loc, rot, scale, mat in house.parts:
        a = actors_sub.spawn_actor_from_class(
            unreal.StaticMeshActor, BAKE_OFFSET + unreal.Vector(*loc), _rot(*rot), transient=True)
        a.set_actor_scale3d(unreal.Vector(*scale))
        c = a.static_mesh_component
        c.set_static_mesh(meshes[mesh])
        if mat not in mats:
            mats[mat] = unreal.load_asset(mat)
        c.set_material(0, mats[mat])
        temp.append(a)

    asset_path = f"{MESH_DIR}SM_TownHouse_{key}"
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.EditorAssetLibrary.delete_asset(asset_path)

    settings = unreal.MeshMergingSettings()
    settings.set_editor_property("pivot_type", unreal.MeshMergePivotType.CUSTOM)
    settings.set_editor_property("custom_pivot_location", BAKE_OFFSET)
    settings.set_editor_property("merge_physics_data", True)
    settings.set_editor_property("merge_equivalent_materials", True)
    settings.set_editor_property("generate_light_map_uv", False)
    nanite = settings.get_editor_property("nanite_settings")
    nanite.set_editor_property("enabled", True)
    settings.set_editor_property("nanite_settings", nanite)

    opts = unreal.MergeStaticMeshActorsOptions()
    # The merge utility prefixes the asset name with "SM_" itself.
    opts.set_editor_property("base_package_name", f"{MESH_DIR}TownHouse_{key}")
    opts.set_editor_property("destroy_source_actors", True)
    opts.set_editor_property("spawn_merged_actor", False)
    opts.set_editor_property("mesh_merging_settings", settings)
    unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).merge_static_mesh_actors(temp, opts)
    for a in temp:
        if a and not a.is_actor_being_destroyed():
            actors_sub.destroy_actor(a)

    sm = unreal.load_asset(asset_path)
    if sm is not None:
        unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)
    return sm, asset_path


def rebuild(key):
    helper = unreal.MCPythonHelper
    path = f"{BP_DIR}BP_TownHouse_{key}"
    bp = unreal.load_asset(path)
    if bp is None:
        return {"house": key, "error": f"missing {path}"}

    listing = json.loads(helper.list_blueprint_components(bp))
    for comp in listing.get("components", []):
        name = comp["variable_name"]
        if name != ROOT:
            helper.remove_component_from_blueprint(bp, name)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)

    house = DESIGNS[key]()
    sm, sm_path = bake_mesh(key, house)
    if sm is None:
        return {"house": key, "error": f"merge produced no asset at {sm_path}"}

    helper.add_component_to_blueprint(bp, SMC, "HouseMesh", 0, 0, 0, 0, 0, 0, ROOT)
    r = json.loads(helper.set_component_property(bp, "HouseMesh", "StaticMesh", sm.get_path_name()))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    saved = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
    return {"house": key, "parts": len(house.parts), "mesh": sm.get_path_name(),
            "sections": len(sm.get_editor_property("static_materials")), "mesh_set": r.get("success"),
            "saved": saved}


def main(argv):
    keys = [a for a in argv if a in DESIGNS] or list(DESIGNS)
    results = [rebuild(key) for key in keys]
    out = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/build_result.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=1)


main(sys.argv[1:])
