# Wokwi project: ESP32 alarm clock wiring test

Same pins as `../pins.h` / `../WIRING.md`. `pins.h` is copied here so Wokwi can `#include` it (keep the two copies identical; `make_diagram.py` checks the GPIO numbers against it). Regenerate `diagram.json` with `python make_diagram.py`.

## Open it (5 steps)
1. wokwi.com > New Project > **ESP32** (Arduino) and sign in to save.
2. Replace the contents of the `sketch.ino`, `diagram.json` and `libraries.txt` tabs with these three files.
3. Add a new file `pins.h` (the "+" next to the tabs) and paste the copy from this folder.
4. Do **not** add a `secrets.h`: without it the sketch falls back to the simulator's open network `Wokwi-GUEST`.
5. Press the green Play button. Buttons: click them, or press keys 1, 2, 3.

Expected: the OLED shows "no time yet" for a few seconds, then the time (Sydney zone) and date with "WiFi" top right; the LED cycles R/G/B; buttons beep and their box lights up.

`libraries.txt` holds only library names, one per line, no comments (a comment line broke an earlier import):
```
Adafruit SSD1306
Adafruit GFX Library
Adafruit BusIO
```

## Why Adafruit SSD1306 + GFX (and not U8g2)
- It is the most common SSD1306 library, so attendees find the most examples; Wokwi lists it for `board-ssd1306`.
- The built-in font scales with `setTextSize()`, which is all we need for big digits (size 4 = 24x32 px).
- U8g2 has nicer fonts, lower RAM use (page mode), and supports SH1106 too. Switch to it later if you want fancy fonts. Cost of Adafruit: 1 KB frame buffer in RAM, irrelevant on the ESP32.

## Part names (checked)
| Part | Wokwi type | Pins used |
|---|---|---|
| ESP32 DevKit V1 (30-pin) | `board-esp32-devkit-v1` | D4, D18, D19, D21, D22, D23, D25, D26, D27, 3V3, GND.1, GND.2, TX0, RX0 (names from wokwi-boards `esp32-devkit-v1/board.json`) |
| OLED | `board-ssd1306` | VCC, GND, SDA, SCL (attr `i2cAddress` "0x3c"/"0x3d") |
| RGB LED | `wokwi-rgb-led` | R, G, B, COM (attr `common`: "cathode") |
| Buzzer | `wokwi-buzzer` | 1 (negative), 2 (positive) |
| Buttons | `wokwi-pushbutton` | 1.l/1.r (one terminal), 2.l/2.r (other terminal) |
| Resistors | `wokwi-resistor` | 1, 2 |

`wokwi-cli lint` reports one info line: `board-esp32-devkit-v1` is "undocumented" (no docs page on docs.wokwi.com even though the Wokwi board list names "ESP32 DevKit v1"). It is the type the board definition `esp32-devkit-v1` uses and the lint raises no error. If it is ever removed, swap to `board-esp32-devkit-c-v4`, but check its pin names and layout first; they differ.

## What was and was not checked
- Checked: diagram.json is valid JSON; every one of the 42 connection endpoints names a real part and a real pin (own script, plus `wokwi-cli lint`: no errors); GPIO numbers match `pins.h`; the sketch compiles with arduino-esp32 3.3.12.
- **Not checked**: the project has not been run in the Wokwi simulator (no account/token on this machine), and I have not seen the layout rendered. Part positions and wire routes are estimates: expect to nudge parts and re-route a few wires in the editor.

## Simulation limits (what the simulator does differently from the real clock)
- WiFi works only to `Wokwi-GUEST` (open). NTP over UDP should work (UDP is supported; ICMP/ping is not). Not tried.
- Bluetooth is not simulated at all (not used yet anyway).
- The RGB LED part ignores the resistor values: it looks equally bright on all colours. On the real clock green/blue are dimmer (WIRING.md section 3).
- The buzzer part plays a clean tone. A real PS1240 is quieter at 3.3 V.
- Brownout, strapping pins, USB power and drivers are not simulated.
- No breadboard in the diagram: it shows electrical connections only. Common ground is wired to the ESP32 GND pins directly.

## PNG for slides
Wokwi has no export-image button I could confirm in the docs. Use `../pin-diagram.png` / `.svg` (plain connection diagram, made with `../make_diagrams.py`), or take a screenshot of the diagram pane (Win+Shift+S). `wokwi-cli` can take screenshots (`--screenshot-part`, `--screenshot-time`, `--screenshot-file`) but needs a free `WOKWI_CLI_TOKEN`; not tried.

## Running the sketch in the Arduino IDE / arduino-cli
The Arduino IDE needs the sketch folder to have the same name as the `.ino`. Copy `sketch.ino`, `pins.h` and your `secrets.h` into a folder called `sketch`, open it, board "DOIT ESP32 DEVKIT V1" (or "ESP32 Dev Module"), core: `esp32` by Espressif Systems **3.x**, libraries: Adafruit SSD1306, Adafruit GFX Library.

## Docs used
- https://docs.wokwi.com/parts/board-ssd1306 , wokwi-rgb-led , wokwi-buzzer
- https://docs.wokwi.com/guides/esp32 and https://docs.wokwi.com/guides/esp32-wifi (Wokwi-GUEST, limits)
- https://github.com/wokwi/wokwi-boards/blob/main/boards/esp32-devkit-v1/board.json (pin names, 28.2 x 53 mm board)
