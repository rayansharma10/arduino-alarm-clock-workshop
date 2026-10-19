# Parts list (per clock)

No prices. Order spares: about 10% extra of everything cheap, and 1-2 spare ESP32 boards and OLEDs for the session.

| Qty | Part | Notes |
|---|---|---|
| 1 | ESP32 DevKit, 30-pin, ESP-WROOM-32 ("DOIT ESP32 DEVKIT V1" style) | Classic ESP32 only, not ESP8266, not C3/S2/S3. See "Board" below. |
| 1 | USB cable, **data** cable, matching the board's port | Micro-USB on most 30-pin DOIT-style boards, USB-C on some newer clones. Check the listing photo. Charge-only cables are the number one cause of "port does not show up". |
| 1 | 0.96 in SSD1306 OLED, 128x64, **I2C**, 4 pins | Not the 7-pin SPI version. Check the pin order printed on the module (GND/VCC/SCL/SDA or VCC/GND/SCL/SDA, they vary). Address 0x3C (some 0x3D). |
| 1 | Passive buzzer: TDK PS1240 or KY-006 module | Passive (needs tone()), not an "active" buzzer with a built-in oscillator. |
| 1 | RGB LED, 5 mm, **common cathode** (4 legs, longest leg = common) | Common anode will not work unless you flip `RGB_COMMON_ANODE` and rewire (WIRING.md). |
| 1 | Resistor 150 ohm, 1/4 W | Red channel |
| 2 | Resistor 47 ohm, 1/4 W | Green and blue channels. **Not 220 ohm**, see WIRING.md section 3. |
| 3 | Tactile push button, 6x6 mm, 4-leg | SET, NEXT, SNOOZE |
| 1 set | Breadboard + jumpers, see "Breadboard" below | Male-male Dupont jumpers, about 20. Add 4 female-male jumpers if the OLED has a header soldered on and you want to plug it in away from the breadboard. |

Not needed any more (Uno version only): Arduino Uno, TM1637 display, DS3231 RTC module, CR2032.

Workshop extras (not per clock): a phone hotspot or travel router on 2.4 GHz for NTP time, a multimeter, a spare USB charger/port, a printed copy of WIRING.md section 7 (the test checklist).

## Board: variant and pinout

- Target: **ESP32 DevKit V1 30-pin layout** (2 rows of 15 pins, silkscreen labels like D21, D22, TX0, RX0, VIN, 3V3, EN). This is the layout the Wokwi `board-esp32-devkit-v1` part and `pins.h` assume.
- Check before buying: the listing shows silkscreen labels D4, D18, D19, D21, D22, D23, D25, D26, D27 and 3V3 and two GND pins. These 9 GPIOs exist on the usual 30-pin and 38-pin boards, but the *physical order differs between variants*, so do not wire from a different board's pinout picture.
- Avoid boards sold as "ESP32-S3/C3/S2", "ESP32-CAM", "ESP32-WROVER with PSRAM" (the WROVER uses GPIO16/17 internally; we do not use those, but keep it simple), and 36-pin or smaller boards with missing pins.
- Fits Arduino IDE as "DOIT ESP32 DEVKIT V1" (`esp32:esp32:esp32doit-devkit-v1`) or generic "ESP32 Dev Module" (`esp32:esp32:esp32`). Both compile the test sketch.

## USB-serial chip and drivers

Most boards carry a CP2102 (Silicon Labs "CP210x") or CH340/CH340C/CH9102 (WCH) USB-UART chip. Look at the small chip next to the USB port.
- Windows 10/11 usually installs CP210x and CH340 drivers by itself through Windows Update; if the board is not listed under Device Manager > Ports (COM & LPT), install the driver from the chip maker (Silicon Labs for CP210x, WCH for CH340/CH9102).
- Buy one chip type for the whole class so the instructions are the same for everybody.
- Some boards need you to **hold BOOT** while the IDE says "Connecting........" (WIRING.md section 8).

## Headers: soldered or not

- Many listings ship the board **with pin headers loose in the bag**. Pre-built clocks need headers **soldered on**, so either buy "pre-soldered / headers attached" or solder them (15 pins x 2, short side down, board flat on the breadboard).
- Do not rely on pins just pushed through the holes: intermittent contact looks exactly like a software bug.

## Breadboard: it does not fit the way you would expect

The ESP32 DevKit is about 28 mm wide with the two pin rows about 25.4 mm (1.0 in) apart (the Wokwi model of the DOIT board uses 25.5 mm; **measure your board**). A breadboard has 2.54 mm hole pitch, a 7.62 mm centre channel, and 5 connected holes per strip on each side.

Calculated from those nominal dimensions (not tested with your parts):
- With 1.0 in row spacing the pins land on rows a and i, or b and j. Every other hole in those strips sits **under the board body**. Only one outer hole on one side stays free, so you cannot plug jumpers into most pins. This is true for a half-size (400 pt) and a full-size (830 pt) board alike: a bigger breadboard only gives more room for the other parts, not access to the ESP32 pins.
- With a narrower 0.9 in (22.9 mm) board the pins land on b and i (or a and h): the outer hole on each side is free (a and j), so each pin gets exactly one usable hole. Tight but works.

Recommendation, in order:
1. **ESP32 30-pin expansion board (breakout "shield" with screw terminals or header sockets that bring every pin out, and a screw-terminal or DC input for power)** plus a **half-size (400 pt) breadboard** for the LED, resistors and buttons, joined with Dupont jumpers. Most robust for a pre-built workshop kit: the ESP32 does not sit on the breadboard, so everything is reachable and labelled. This is what I would buy.
2. **Two half-size breadboards** with the ESP32 straddling the gap between them: place them so the two facing hole rows are 25.4 mm (10 hole-pitches) apart and fix both to a base plate. Each side then has 4 free holes per pin. Fiddly, and the boards slide apart in a bag.
3. A **full-size (830 pt) breadboard** only if your measured board is the narrow 0.9 in kind (see above). Otherwise it does not solve the access problem.

The static diagram `pin-diagram.png` and the Wokwi project show the electrical connections only (no breadboard holes), so they stay valid for all three options. Exact hole-by-hole layouts depend on the option chosen, so WIRING.md gives a placement plan for option 1 only.
