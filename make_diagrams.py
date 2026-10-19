"""Generates wiring.svg/png (connection diagram) and breadboard.svg/png (breadboard layout).
Run:  uv run --with matplotlib python make_diagrams.py
Wire colours here MUST match the colour table in WIRING.md.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Circle, Arc

plt.rcParams["svg.fonttype"] = "none"      # keep text as text in the SVG
plt.rcParams["font.family"] = "DejaVu Sans"

C = dict(
    V5="#d62728", GND="#111111", CLK="#d4a900", DIO="#ffffff",
    SDA="#8e44ad", SCL="#17a2b8", BUZ="#8b5a2b",
    R="#f28e00", G="#2ca02c", B="#1f5fd6", BTN="#8c8c8c",
)
WHITE_OUTLINE = [pe.withStroke(linewidth=5.0, foreground="#333333")]


def wire(ax, pts, col, lw=3.4, z=3):
    xs, ys = zip(*pts)
    kw = dict(path_effects=WHITE_OUTLINE) if col == "#ffffff" else {}
    ax.plot(xs, ys, color=col, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=z, **kw)


def dot(ax, x, y, col="#111111", r=0.7, z=6):
    ax.add_patch(Circle((x, y), r, fc=col, ec="#111", lw=1, zorder=z))


def box(ax, x0, y0, x1, y1, title=None, fc="#f4f4f4", tsize=13.5):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="#222222", lw=2, zorder=2))
    if title:
        ax.text((x0 + x1) / 2, y1 + 0.8, title, ha="center", va="bottom", fontsize=tsize, fontweight="bold")


# ============================================================ 1. connection diagram
def schematic():
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")
    ax.text(80, 97.0, "Alarm clock wiring (Arduino Uno R3): connection diagram", ha="center",
            fontsize=22, fontweight="bold")

    box(ax, 6, 1, 34, 94.5, None, fc="#e8eef7")
    ax.text(14, 48, "Arduino Uno R3", rotation=90, ha="center", va="center", fontsize=20, fontweight="bold")
    ax.text(14, 22, "(pins grouped by job,\nnot physical order)", rotation=90, ha="center", va="center",
            fontsize=10, color="#444")
    pins = [("D2", 82), ("D4", 77), ("A4  (SDA)", 68), ("A5  (SCL)", 63), ("D8", 55),
            ("D5  (PWM)", 47), ("D6  (PWM)", 42), ("D9  (PWM)", 37),
            ("D10", 29), ("D11", 24), ("D12", 19), ("5V", 92.5), ("GND", 5)]
    for name, y in pins:
        ax.text(32.3, y, name, ha="right", va="center", fontsize=13, fontweight="bold")
        dot(ax, 34, y, C["V5"] if name == "5V" else ("#111" if name == "GND" else "#444"), 0.8)

    X0, X1 = 100, 124
    BUS5, BUSG = 148, 154

    # TM1637
    box(ax, X0, 75.2, X1, 87.5, "TM1637 4-digit display")
    for t, y in (("CLK", 82), ("DIO", 77)):
        ax.text(X0 + 1.5, y, t, va="center", fontsize=12.5)
    ax.text(X1 - 1.5, 84, "VCC", va="center", ha="right", fontsize=12.5)
    ax.text(X1 - 1.5, 77.5, "GND", va="center", ha="right", fontsize=12.5)
    wire(ax, [(34, 82), (X0, 82)], C["CLK"]); wire(ax, [(34, 77), (X0, 77)], C["DIO"])
    # DS3231
    box(ax, X0, 61, X1, 72, "DS3231 RTC module")
    for t, y in (("SDA", 68), ("SCL", 63)):
        ax.text(X0 + 1.5, y, t, va="center", fontsize=12.5)
    ax.text(X1 - 1.5, 69.0, "VCC", va="center", ha="right", fontsize=12.5)
    ax.text(X1 - 1.5, 63, "GND", va="center", ha="right", fontsize=12.5)
    wire(ax, [(34, 68), (X0, 68)], C["SDA"]); wire(ax, [(34, 63), (X0, 63)], C["SCL"])
    # Buzzer
    box(ax, X0, 51, X1, 59.5, None)
    ax.text((X0 + X1) / 2, 57.2, "Passive buzzer", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(X0 + 1.5, 54.6, "SIG", va="center", fontsize=12.5)
    ax.text(X1 - 1.5, 52.4, "GND", va="center", ha="right", fontsize=12.5)
    wire(ax, [(34, 55), (X0, 55)], C["BUZ"])
    # RGB LED + resistors
    for y, k in ((47, "R"), (42, "G"), (37, "B")):
        wire(ax, [(34, y), (X0, y)], C[k])
        ax.add_patch(Rectangle((X0, y - 1.6), 10, 3.2, fc="#e6d3a3", ec="#222", lw=1.8, zorder=4))
        ax.text(X0 + 5, y, "220 \u03a9", ha="center", va="center", fontsize=11.5, zorder=5)
        wire(ax, [(X0 + 10, y), (118, y)], C[k])
        ax.text(119.5, y, k, va="center", fontsize=12.5, fontweight="bold")
    box(ax, 118, 33, 140, 49.5, None)
    ax.text(130, 44.5, "RGB LED", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(130, 41, "common cathode", ha="center", va="center", fontsize=11)
    ax.text(130, 38, "K = longest leg", ha="center", va="center", fontsize=10.5, color="#444")
    ax.text(138.5, 35, "K", ha="right", va="center", fontsize=12.5, fontweight="bold")
    # Buttons
    for nm, y in (("BTN 1   hour / mode", 29), ("BTN 2   minute / next", 24), ("BTN 3   snooze / stop", 19)):
        wire(ax, [(34, y), (X0, y)], C["BTN"])
        ax.add_patch(Rectangle((X0, y - 2.2), X1 - X0, 4.4, fc="#f4f4f4", ec="#222", lw=2, zorder=2))
        ax.text((X0 + X1) / 2, y, nm, ha="center", va="center", fontsize=11.5, fontweight="bold")

    # ---- power buses
    wire(ax, [(34, 92.5), (BUS5, 92.5), (BUS5, 69.0)], C["V5"])
    wire(ax, [(X1, 84), (BUS5, 84)], C["V5"]); dot(ax, BUS5, 84, C["V5"])
    wire(ax, [(X1, 69.0), (BUS5, 69.0)], C["V5"]); dot(ax, BUS5, 69.0, C["V5"])
    wire(ax, [(34, 5), (BUSG, 5), (BUSG, 77.5)], C["GND"])
    gnd_taps = [(X1, 63), (X1, 52.4), (140, 35), (X1, 29), (X1, 24), (X1, 19)]
    for x, y in gnd_taps:
        wire(ax, [(x, y), (BUSG, y)], C["GND"]); dot(ax, BUSG, y, C["GND"])
    # TM1637 GND tap hops over the 5V bus
    wire(ax, [(X1, 77.5), (BUS5 - 2, 77.5)], C["GND"])
    ax.add_patch(Arc((BUS5, 77.5), 4, 4, theta1=0, theta2=180, color=C["GND"], lw=3.4, zorder=4))
    wire(ax, [(BUS5 + 2, 77.5), (BUSG, 77.5)], C["GND"]); dot(ax, BUSG, 77.5, C["GND"])
    ax.text(BUS5, 94.3, "5V", ha="center", fontsize=13, fontweight="bold", color=C["V5"])
    ax.text(BUSG + 1.0, 80.5, "GND", ha="left", fontsize=13, fontweight="bold")

    # ---- legend (sits in the free strip under the button wires)
    ax.add_patch(Rectangle((36, 5.9), 114, 10, fc="white", ec="#888", lw=1.2, zorder=1))
    ax.text(38, 14.6, "Wire colours (suggested)", fontsize=13, fontweight="bold", va="center")
    items = [("5V", "V5"), ("GND", "GND"), ("TM1637 CLK", "CLK"), ("TM1637 DIO", "DIO"),
             ("I2C SDA", "SDA"), ("I2C SCL", "SCL"), ("Buzzer", "BUZ"),
             ("LED R leg (orange)", "R"), ("LED G leg", "G"), ("LED B leg", "B"),
             ("Buttons (all 3)", "BTN")]
    for i, (lab, k) in enumerate(items):
        col, row = divmod(i, 3)
        x = 38 + col * 28
        y = 12.2 - row * 1.9
        wire(ax, [(x, y), (x + 5, y)], C[k], lw=4)
        ax.text(x + 6.5, y, lab, va="center", fontsize=10.5)
    ax.text(38, 6.8, "Red wire = 5V only.  A dot on a bus = joined.  A wire hopping over another = not joined.",
            fontsize=10.5, va="center", color="#333")
    fig.savefig("wiring.svg"); fig.savefig("wiring.png", dpi=120)
    plt.close(fig)


# ============================================================ 2. breadboard layout
def breadboard():
    fig, ax = plt.subplots(figsize=(16, 11.5))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(-18, 38); ax.set_ylim(29.5, -10.5); ax.axis("off")
    ax.text(10, -9.3, "Breadboard layout (400-point half-size board, top view)", ha="center",
            fontsize=21, fontweight="bold")
    RY5, RYG = 1.0, 2.2
    WIRE_COLS = {3, 5, 6, 10, 15, 20, 26}
    rowy = {"a": 4.2, "b": 5.2, "c": 6.2, "d": 7.2, "e": 8.2, "f": 11.2, "g": 12.2, "h": 13.2, "i": 14.2, "j": 15.2}
    ax.add_patch(Rectangle((-0.8, -0.4), 32, 17.4, fc="#f2efe6", ec="#555", lw=2, zorder=0))
    ax.add_patch(Rectangle((-0.8, 8.6), 32, 2.0, fc="#d8d4c8", ec="none", zorder=0))     # trench
    ax.plot([0, 30.6], [0.35, 0.35], color=C["V5"], lw=2, zorder=1)
    ax.plot([0, 30.6], [2.95, 2.95], color="#111", lw=2, zorder=1)
    for c in range(1, 31):
        for y in (RY5, RYG, *rowy.values()):
            ax.add_patch(Circle((c, y), 0.2, fc="#9a9a9a", ec="none", zorder=1))
        if c not in WIRE_COLS:
            ax.text(c, 16.15, str(c), ha="center", va="center", fontsize=8.5, zorder=9, color="#444")
    for r, y in rowy.items():
        ax.text(-0.3, y, r, ha="center", va="center", fontsize=9, color="#444")
    ax.text(31.7, RY5, "+ rail (5V)", va="center", fontsize=11, fontweight="bold", color=C["V5"])
    ax.text(31.7, RYG, "\u2212 rail (GND)", va="center", fontsize=11, fontweight="bold")
    def hole(c, r, col):
        y = RY5 if r == "+" else RYG if r == "-" else rowy[r]
        dot(ax, c, y, col, 0.38, z=7)

    # ---- RGB LED (legs c3..c6) + resistors (d -> g)
    ax.add_patch(Circle((4.5, 4.9), 1.65, fc="#dcdcdc", ec="#555", lw=1.5, alpha=0.4, zorder=4))
    for c, col in ((3, C["R"]), (4, "#111"), (5, C["G"]), (6, C["B"])):
        hole(c, "c", col)
    for c, col in ((3, C["R"]), (5, C["G"]), (6, C["B"])):
        ax.plot([c, c], [7.2, 8.7], color="#333", lw=1.6, zorder=4)
        ax.add_patch(Rectangle((c - 0.33, 8.7), 0.66, 2.0, fc="#e6d3a3", ec="#222", lw=1.3, zorder=5))
        ax.plot([c, c], [10.7, 12.2], color="#333", lw=1.6, zorder=4)
        hole(c, "d", "#333"); hole(c, "g", "#333")
    ax.text(2.35, 9.7, "220 \u03a9", rotation=90, ha="center", va="center", fontsize=9)
    ax.text(4.3, 9.7, "220 \u03a9", rotation=90, ha="center", va="center", fontsize=9)
    ax.text(6.7, 9.7, "220 \u03a9", rotation=90, ha="center", va="center", fontsize=9)
    wire(ax, [(4, 4.2), (4, RYG)], C["GND"], z=8); hole(4, "a", C["GND"]); hole(4, "-", C["GND"])
    ax.text(-1.2, 5.2, "RGB LED, flat side on the left.\nLegs left to right: R | K (longest) | G | B\n"
            "K goes to the \u2212 rail.", ha="right", va="center", fontsize=10.5)
    # bottom jumpers for LED
    for c, y_end, k, lab in ((3, 18.0, "R", "D5  (LED R via 220 \u03a9)   col 3"),
                             (5, 20.0, "G", "D6  (LED G via 220 \u03a9)   col 5"),
                             (6, 22.0, "B", "D9  (LED B via 220 \u03a9)   col 6")):
        wire(ax, [(c, rowy["j"]), (c, y_end)], C[k], z=8); hole(c, "j", C[k])
        ax.text(c - 0.35, y_end, lab, ha="right", va="center", fontsize=11, fontweight="bold")

    # ---- Buttons
    for c, lab, y_end in ((10, "D10  (col 10)\nBTN 1\nhour / mode", 18.0),
                          (15, "D11  (col 15)\nBTN 2\nminute / next", 18.0),
                          (20, "D12  (col 20)\nBTN 3\nsnooze / stop", 18.0)):
        ax.add_patch(Rectangle((c - 0.25, 8.45), 2.5, 2.5, fc="#3a3a3a", ec="#111", lw=1.5, zorder=4))
        ax.add_patch(Circle((c + 1, 9.7), 0.8, fc="#6b6b6b", ec="#111", zorder=5))
        for cc in (c, c + 2):
            hole(cc, "e", "#555"); hole(cc, "f", "#555")
        wire(ax, [(c, 4.2), (c, RYG)], C["GND"], z=8); hole(c, "a", C["GND"]); hole(c, "-", C["GND"])
        wire(ax, [(c, rowy["j"]), (c, y_end)], C["BTN"], z=8); hole(c, "j", C["BTN"])
        ax.text(c, y_end + 0.5, lab, ha="center", va="top", fontsize=11, fontweight="bold")
    # ---- Buzzer PS1240 straddling trench at col 26
    ax.add_patch(Circle((26, 9.7), 1.65, fc="#bdb3a4", ec="#333", lw=1.8, zorder=4))
    ax.text(26, 9.7, "PS1240\nbuzzer", ha="center", va="center", fontsize=8.5, zorder=6)
    hole(26, "e", "#555"); hole(26, "f", "#555")
    wire(ax, [(26, 4.2), (26, RYG)], C["GND"], z=8); hole(26, "a", C["GND"]); hole(26, "-", C["GND"])
    wire(ax, [(26, rowy["j"]), (26, 18.0)], C["BUZ"], z=8); hole(26, "j", C["BUZ"])
    ax.text(26, 18.5, "D8  (col 26)\nbuzzer", ha="center", va="top", fontsize=11, fontweight="bold")

    # ---- power wires leaving the rails
    for c, tag, h in ((19, "TM1637 VCC", -3.0), (22, "DS3231 VCC", -5.4)):
        wire(ax, [(c, RY5), (c, h)], C["V5"], z=8); hole(c, "+", C["V5"])
        ax.text(c, h - 0.3, tag + "\n(red)", ha="center", va="bottom", fontsize=10.5, fontweight="bold",
                color=C["V5"], linespacing=1.0)
    for c, tag, h in ((25, "TM1637 GND", -3.0), (28, "DS3231 GND", -5.4)):
        wire(ax, [(c, RYG), (c, h)], C["GND"], z=8); hole(c, "-", C["GND"])
        ax.text(c, h - 0.3, tag + "\n(black)", ha="center", va="bottom", fontsize=10.5, fontweight="bold",
                linespacing=1.0)
    wire(ax, [(1, RY5), (-3, RY5)], C["V5"], z=8); hole(1, "+", C["V5"])
    wire(ax, [(1, RYG), (-3, RYG)], C["GND"], z=8); hole(1, "-", C["GND"])
    ax.text(-3.4, RY5, "Uno 5V  (red)", ha="right", va="center", fontsize=11.5, fontweight="bold", color=C["V5"])
    ax.text(-3.4, RYG, "Uno GND  (black)", ha="right", va="center", fontsize=11.5, fontweight="bold")

    # ---- notes
    notes = ("Direct wires, NOT through the breadboard (female-to-male jumpers, module end female):\n"
             "   TM1637 CLK \u2192 Uno D2 (yellow)     TM1637 DIO \u2192 Uno D4 (white)\n"
             "   DS3231 SDA \u2192 Uno A4 (purple)     DS3231 SCL \u2192 Uno A5 (cyan)\n"
             "Bottom wires (labelled with Uno pin) go to the Uno header sockets.\n"
             "KY-006 module instead of PS1240: S \u2192 D8, \u2212 \u2192 GND rail, via jumpers (see WIRING.md).\n"
             "Rails: check yours are continuous end to end (some boards split them in the middle).\n"
             "Red/black wires from the rails to the modules hop over the other rail; they do not touch it.")
    ax.text(10.5, 23.6, notes, ha="left", va="top", fontsize=10.5, linespacing=1.5,
            bbox=dict(fc="white", ec="#888", pad=9))
    fig.savefig("breadboard.svg"); fig.savefig("breadboard.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    schematic()
    breadboard()
    print("ok")
