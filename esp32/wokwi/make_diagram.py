"""Generates diagram.json and checks every wire against the real pin names.
Run: python make_diagram.py     (then optionally: wokwi-cli lint .)
Pin names come from docs.wokwi.com part pages and the wokwi-elements source
(board-esp32-devkit-v1: https://github.com/wokwi/wokwi-boards/blob/main/boards/esp32-devkit-v1/board.json)
"""
import json, re, sys

def P(i, t, l, tp, a=None, r=None):
    d = dict(id=i, type=t, top=tp, left=l, attrs=a or {})
    if r: d["rotate"] = r
    return d

ex, ey = 260, 40            # ESP32 position; its pins are at about x+5 (left) and x+101 (right)
parts = [
    P("esp", "board-esp32-devkit-v1", ex, ey),
    P("oled1", "board-ssd1306", 520, 110, {"i2cAddress": "0x3c"}),
    P("bz1", "wokwi-buzzer", 540, -10, {"volume": "0.5"}),
    P("led1", "wokwi-rgb-led", 580, 290, {"common": "cathode"}),
    P("r1", "wokwi-resistor", 440, 250, {"value": "150"}),   # red
    P("r2", "wokwi-resistor", 440, 285, {"value": "47"}),    # green
    P("r3", "wokwi-resistor", 440, 320, {"value": "47"}),    # blue
    P("btn1", "wokwi-pushbutton", 60, 60,  {"color": "green", "label": "SET",    "key": "1"}),
    P("btn2", "wokwi-pushbutton", 60, 140, {"color": "blue",  "label": "NEXT",   "key": "2"}),
    P("btn3", "wokwi-pushbutton", 60, 220, {"color": "red",   "label": "SNOOZE", "key": "3"}),
]
c = []
def w(a, b, col, route=None): c.append([a, b, col, route or []])

# serial monitor (standard Wokwi ESP32 wiring)
w("esp:TX0", "$serialMonitor:RX", "", [])
w("esp:RX0", "$serialMonitor:TX", "", [])
# OLED: 3V3 power, GND, I2C (SDA=GPIO21, SCL=GPIO22)
w("oled1:VCC", "esp:3V3", "red",    ["v30", "h-60"])
w("oled1:GND", "esp:GND.1", "black", ["v40", "h-70"])
w("oled1:SDA", "esp:D21", "purple", ["v20", "h-100"])
w("oled1:SCL", "esp:D22", "cyan",   ["v10", "h-110"])
# buzzer: pin 1 = negative to GND, pin 2 = positive to GPIO23
w("bz1:1", "esp:GND.1", "black", ["v200", "h-180"])
w("bz1:2", "esp:D23", "brown",   ["v10", "h-140"])
# RGB LED (common cathode): GPIO19/18/4 -> resistor -> LED pin; COM to GND
w("esp:D19", "r1:1", "orange", ["h40", "v100"])
w("esp:D18", "r2:1", "green",  ["h50", "v110"])
w("esp:D4",  "r3:1", "blue",   ["h60", "v120"])
w("r1:2", "led1:R", "orange", [])
w("r2:2", "led1:G", "green",  [])
w("r3:2", "led1:B", "blue",   [])
w("led1:COM", "esp:GND.1", "black", ["v40", "h-300"])
# buttons: terminal 1 to GPIO (INPUT_PULLUP), terminal 2 to GND
for n, pin in enumerate(["D25", "D26", "D27"], 1):
    w(f"btn{n}:1.r", f"esp:{pin}", "gray", [])
    w(f"btn{n}:2.r", "esp:GND.2", "black", [])

doc = dict(version=1, author="UNSW CES workshop", editor="wokwi", parts=parts, connections=c)
json.dump(doc, open("diagram.json", "w"), indent=2)

# ---- validation: every endpoint must be a real pin of a real part
ESP = ("VIN GND.2 D13 D12 D14 D27 D26 D25 D33 D32 D35 D34 VN VP EN 3V3 GND.1 D15 D2 D4 RX2 TX2 "
       "D5 D18 D19 D21 RX0 TX0 D22 D23").split()
PINS = {
    "board-esp32-devkit-v1": ESP,
    "board-ssd1306": "GND VCC SCL SDA".split(),
    "wokwi-buzzer": ["1", "2"],
    "wokwi-rgb-led": "R G B COM".split(),
    "wokwi-resistor": ["1", "2"],
    "wokwi-pushbutton": ["1.l", "1.r", "2.l", "2.r"],
}
byid = {p["id"]: p["type"] for p in parts}
bad = 0
for a, b, *_ in c:
    for end in (a, b):
        pid, pin = end.split(":", 1)
        if pid.startswith("$"):
            continue
        if pid not in byid or pin not in PINS[byid[pid]]:
            print("BAD ENDPOINT", end); bad += 1
# GPIO number sanity check against pins.h
h = open("pins.h").read()
gp = {k: int(v) for k, v in re.findall(r"#define (PIN_\w+)\s+(\d+)", h)}
want = {"PIN_I2C_SDA": "esp:D21", "PIN_I2C_SCL": "esp:D22", "PIN_BUZZER": "esp:D23",
        "PIN_LED_R": "esp:D19", "PIN_LED_G": "esp:D18", "PIN_LED_B": "esp:D4",
        "PIN_BTN_SET": "esp:D25", "PIN_BTN_NEXT": "esp:D26", "PIN_BTN_SNOOZE": "esp:D27"}
for k, pin in want.items():
    if f"esp:D{gp[k]}" != pin:
        print("pins.h mismatch", k, gp[k], pin); bad += 1
used = [e for a, b, *_ in c for e in (a, b) if e.startswith("esp:")]
print("endpoints checked:", sum(1 for a, b, *_ in c for e in (a, b)), "problems:", bad)
sys.exit(1 if bad else 0)
