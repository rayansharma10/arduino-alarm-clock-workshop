# Wokwi project: alarm clock wiring test

Same pins as `../pins.h` / `../WIRING.md` (no pin changes). `pins.h` is copied here so Wokwi can `#include` it. Regenerate `diagram.json` with `python make_diagram.py`.

## Open it (3 steps)
1. wokwi.com > New Project > **Arduino Uno** (sign in with a free account to save).
2. Replace the contents of the `sketch.ino`, `diagram.json` and `libraries.txt` tabs with these files, and add a new file `pins.h` (the "+" next to the tabs) with the copy from this folder.
3. Press the green Play button. Buttons: click them, or press keys 1, 2, 3.

## PNG for slides
Wokwi has no export-image button that I could confirm in the docs. Reliable way: run the simulation, then take a screenshot of the diagram pane (Win+Shift+S). Or with the CLI: `wokwi-cli --screenshot-part uno --screenshot-time 2000 --screenshot-file out.png` (needs a free `WOKWI_CLI_TOKEN` and a compiled .hex/.elf, see `wokwi.toml`; not tried).

## DS3231 vs DS1307
Wokwi has a built-in `wokwi-ds1307` part, but I found no built-in DS3231 (only community "custom chip" projects). The diagram uses the DS1307 as a stand-in: both are I2C 0x68, same SDA/SCL wiring, and RTClib reads both the same way. Differences: the real DS3231 module is 3.3-5.5 V with temperature compensation and a CR2032 charge circuit to check (WIRING.md section 4); the sim just ticks. Set `SIMULATOR_DS1307` off in `sketch.ino` for the real clock.

## Simplifications vs the real build
- The simulated parts are not plugged into the breadboard holes; wires go from each part to the breadboard's power rails (`+` top row = 5 V, `-` = GND) or straight to the Uno. Electrically the same as WIRING.md.
- Buzzer: `wokwi-buzzer` plays `tone()` as sound, so it matches a passive buzzer.

## Docs used
- https://docs.wokwi.com/diagram-format
- https://docs.wokwi.com/parts/wokwi-arduino-uno, wokwi-tm1637-7segment, wokwi-rgb-led (attr `common`: "cathode"), wokwi-buzzer, wokwi-pushbutton, wokwi-resistor, wokwi-ds1307
- https://docs.wokwi.com/guides/libraries (libraries.txt), https://docs.wokwi.com/wokwi-ci/cli-usage (lint, screenshots)
