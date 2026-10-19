"""Generates pin-diagram.svg / pin-diagram.png: a plain connection diagram for slides.
Run:  uv run --with matplotlib python make_diagrams.py
Wire colours MUST match the table in WIRING.md.  Power/ground are shown as labels (net names)
instead of lines, like a normal schematic, so the signal wires stay readable.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "DejaVu Sans"

COL = dict(SDA="#8e44ad", SCL="#17a2b8", BUZ="#8b5a2b", R="#f28e00", G="#2ca02c", B="#1f5fd6", BTN="#7a7a7a")

fig, ax = plt.subplots(figsize=(14, 8.2))
ax.set_xlim(0, 140); ax.set_ylim(0, 96); ax.axis("off")

def box(x0, y0, x1, y1, title=None, fc="#f4f4f4"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="#222", lw=1.6, zorder=2))
    if title:
        ax.text((x0 + x1) / 2, y1 + 1, title, ha="center", va="bottom", fontsize=11, fontweight="bold")

def wire(pts, col):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=col, lw=3, solid_capstyle="round", zorder=3)

def net(x, y, text, side):   # short stub + net name for power/ground
    dx = 4 if side == "r" else -4
    ax.plot([x, x + dx], [y, y], color="#222", lw=1.6, zorder=3)
    ax.text(x + dx * 1.15, y, text, ha="left" if side == "r" else "right", va="center",
            fontsize=9.5, color="#b00000" if text == "3V3" else "#111")

# ESP32 board
box(52, 6, 88, 78, "ESP32 DevKit (30-pin)")
ax.text(70, 3, "3.3 V logic, USB at the bottom", ha="center", fontsize=9, color="#444")
left_pins  = [("GPIO25 (D25)", 58), ("GPIO26 (D26)", 50), ("GPIO27 (D27)", 42), ("GND (GND.2)", 22)]
right_pins = [("GPIO23 (D23)", 70), ("GPIO22 (D22)", 58), ("GPIO21 (D21)", 50), ("GPIO19 (D19)", 35),
              ("GPIO18 (D18)", 27), ("GPIO4 (D4)", 19), ("GND (GND.1)", 12), ("3V3", 6)]
for t, y in left_pins:
    ax.text(54, y, t, ha="left", va="center", fontsize=9.5); ax.plot([52], [y], "ks", ms=5, zorder=4)
for t, y in right_pins:
    ax.text(86, y, t, ha="right", va="center", fontsize=9.5); ax.plot([88], [y], "ks", ms=5, zorder=4)

# buttons (left)
for (name, gpio, y) in [("BTN1  SET / mode", 25, 58), ("BTN2  NEXT", 26, 50), ("BTN3  SNOOZE / stop", 27, 42)]:
    box(8, y - 3, 36, y + 3)
    ax.text(22, y, name, ha="center", va="center", fontsize=9.5)
    wire([(36, y), (52, y)], COL["BTN"])
    net(8, y, "GND", "l")
ax.text(22, 66, "Buttons: other leg to GND\n(INPUT_PULLUP, pressed = LOW)", ha="center", fontsize=9, color="#444")
net(52, 22, "GND (same net as the other GNDs)", "l")

# right-hand parts
box(104, 67.5, 132, 72.5, "Passive buzzer")
ax.text(118, 70, "+ pin", ha="center", va="center", fontsize=9.5); wire([(88, 70), (104, 70)], COL["BUZ"]); net(132, 70, "GND (- pin)", "r")
box(104, 44.5, 132, 61, "SSD1306 OLED, address 0x3C")
ax.text(106, 58, "SCL", va="center", fontsize=9.5); wire([(88, 58), (104, 58)], COL["SCL"])
ax.text(106, 50, "SDA", va="center", fontsize=9.5); wire([(88, 50), (104, 50)], COL["SDA"])
ax.text(130, 49, "VCC", ha="right", va="center", fontsize=9.5); net(132, 49, "3V3", "r")
ax.text(130, 46.5, "GND", ha="right", va="center", fontsize=9.5); net(132, 46.5, "GND", "r")

# RGB LED with resistors
for gpio_y, lab, col, res in [(35, "R", COL["R"], "150 \u03a9"), (27, "G", COL["G"], "47 \u03a9"), (19, "B", COL["B"], "47 \u03a9")]:
    wire([(88, gpio_y), (96, gpio_y)], col)
    ax.add_patch(Rectangle((96, gpio_y - 1.6), 8, 3.2, fc="white", ec="#222", lw=1.4, zorder=4))
    ax.text(100, gpio_y, res, ha="center", va="center", fontsize=8.5, zorder=5)
    wire([(104, gpio_y), (112, gpio_y)], col)
    ax.text(114, gpio_y, lab, va="center", fontsize=9.5)
box(112, 15.5, 132, 38.5, "RGB LED")
ax.text(122, 9.5, "common cathode:\nlong leg to GND", ha="center", va="center", fontsize=9)

ax.text(88, 15, "", fontsize=8)
net(88, 12, "GND", "r"); net(88, 6, "3V3", "r")
ax.text(70, 93, "Alarm clock, ESP32 version: signal wiring", ha="center", fontsize=14, fontweight="bold")
ax.text(70, 90, "wire colours as in WIRING.md; power and ground shown as net labels", ha="center", fontsize=9.5, color="#444")

fig.savefig("pin-diagram.svg", bbox_inches="tight"); fig.savefig("pin-diagram.png", dpi=150, bbox_inches="tight")
print("wrote pin-diagram.svg / .png")
