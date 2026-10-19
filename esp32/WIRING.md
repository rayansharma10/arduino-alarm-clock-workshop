# Wiring: ESP32 + OLED alarm clock

Status: everything below is **calculated and compiled, not tested on real hardware**. The test sketch compiles for the ESP32 (arduino-esp32 core 3.3.12). Nothing has been powered up yet. Use the checklist in section 7 on the first real board.

Pin names live in [pins.h](pins.h). Picture of the connections: [pin-diagram.png](pin-diagram.png) (`.svg` for slides). Simulator: [wokwi/](wokwi/WOKWI.md). Parts: [PARTS.md](PARTS.md).

## 1. Pin table

The ESP32 is a 3.3 V chip. Every pin below is 3.3 V logic and **not 5 V tolerant**.

| Part | Part pin | ESP32 GPIO (board label) | Wire colour | Why this pin |
|---|---|---|---|---|
| OLED | VCC | 3V3 | red | The module's pull-ups on SDA/SCL go to VCC, so VCC must be 3.3 V. Do NOT use VIN/5V (would put 5 V on the I2C pins). |
| OLED | GND | GND | black | |
| OLED | SDA | GPIO21 (D21) | purple | Default hardware I2C (`Wire`). |
| OLED | SCL | GPIO22 (D22) | cyan | Default hardware I2C (`Wire`). |
| Buzzer | + (KY-006: S pin; PS1240: either leg) | GPIO23 (D23) | brown | Output-capable, no boot behaviour, away from the I2C pins. |
| Buzzer | - | GND | black | |
| RGB LED | R, through 150 ohm | GPIO19 (D19) | orange | Output-capable, no boot behaviour, PWM-capable. |
| RGB LED | G, through 47 ohm | GPIO18 (D18) | green | same |
| RGB LED | B, through 47 ohm | GPIO4 (D4) | blue | same |
| RGB LED | common (longest leg) | GND | black | Common cathode. |
| Button 1 SET / mode | one leg | GPIO25 (D25) | grey | Has an internal pull-up, not a strapping pin. |
| Button 2 NEXT | one leg | GPIO26 (D26) | grey | same |
| Button 3 SNOOZE / stop | one leg | GPIO27 (D27) | grey | same |
| Buttons 1-3 | other leg | GND | black | Pressed = LOW (`INPUT_PULLUP`). |

All black wires are the same ground. The board has two GND pins (GND.1 on the right row, GND.2 on the left row); they are the same net.

### Pin checks (why not the other pins)

| Rule | Pins | What I did |
|---|---|---|
| GPIO6-11 are wired to the on-board flash | 6, 7, 8, 9, 10, 11 | Not used. Using them crashes the chip. |
| GPIO34-39 are input-only and have **no internal pull-up/pull-down** | 34, 35, 36 (VP), 39 (VN) | Not used for buttons (they would need an external 10 k resistor each). |
| Strapping pins are read at reset and select boot mode and flash voltage | 0, 2, 5, 12, 15 | Not used. GPIO12 is the dangerous one: if something pulls it high at boot the chip selects 1.8 V flash and boot-loops. GPIO0 held low = download mode. GPIO2 should be low/floating to flash. GPIO15 low silences boot messages. |
| UART0 is the USB serial | 1 (TX0), 3 (RX0) | Not used. Wiring to them breaks upload and the Serial Monitor. |
| GPIO14 outputs a PWM pulse at boot | 14 | Not used for the LED (it would flash briefly at every reset). |
| ADC2 pins cannot do `analogRead()` while WiFi is on | 0, 2, 4, 12-15, 25, 26, 27 | **Does not matter here**: pins 4, 25, 26, 27 only do digital read/write. If you add an analog sensor later, use ADC1: GPIO32-39. |
| GPIO16/17 | 16, 17 | Left free (used internally on WROVER/PSRAM modules). |

Free and safe for experiments: GPIO13, 32, 33 (and 16/17 on a WROOM-32 board). Bluetooth/BLE is inside the chip and needs **no pins**, so nothing is reserved for it.

## 2. I2C and the OLED

- SSD1306 128x64 modules answer at **0x3C** (this project) or **0x3D**. Many modules have a small resistor/solder pad on the back to choose. If the screen stays blank, run an I2C scanner sketch. The library wants the 7-bit address (`OLED_I2C_ADDR` in pins.h).
- Power from the **3V3** pin. Current is roughly 10-20 mA depending on how many pixels are lit (typical figure for these modules; check yours).
- I2C needs pull-up resistors. Nearly all OLED modules have them on board (typically 4.7-10 k to VCC). If the scanner finds nothing even though the wiring is right, the pull-ups are the next suspect.
- Pin order on the module varies (GND/VCC/SCL/SDA vs VCC/GND/SCL/SDA). Read the silkscreen, do not copy a picture.

## 3. RGB LED resistors (recalculated for 3.3 V)

The Uno values (220 ohm at 5 V) do **not** carry over. Method: `R = (V_gpio - Vf) / I`, with V_gpio about 3.3 V (an unloaded GPIO; it droops a little under load, so real currents come out a bit lower than below).

Typical forward voltages for a 5 mm RGB LED (check your LED's datasheet): red 1.8-2.2 V (use 2.0), green and blue 2.8-3.3 V (use 3.1). Target about 5-10 mA per channel. I use a working limit of about 12 mA per pin; check the ESP32 datasheet "Absolute Maximum Ratings" and "DC characteristics" tables for the exact per-pin figures (I did not re-check them for this note).

| Channel | R | I at typical Vf | I over the Vf range | Resistor power |
|---|---|---|---|---|
| Red | 150 ohm | (3.3 - 2.0) / 150 = **8.7 mA** | Vf 2.2 V: 7.3 mA; Vf 1.8 V: 10 mA | 1.3 V x 8.7 mA = 11 mW |
| Green | 47 ohm | (3.3 - 3.1) / 47 = **4.3 mA** | Vf 2.8 V: 10.6 mA; Vf 3.2 V: 2.1 mA; Vf 3.3 V: 0 mA | 0.2 V x 4.3 mA = 1 mW |
| Blue | 47 ohm | same as green | same as green | same |

Why not 220 ohm on green/blue: (3.3 - 3.1) / 220 = 0.9 mA typical, and 0 mA if the LED's Vf is 3.3 V, so the channel is very dim or off. Why not below 47 ohm: at the low end of the Vf range (2.8 V) a 33 ohm resistor would pass 15 mA, over the working limit.

What to expect (calculated, **not measured**): red clearly bright; green and blue noticeably dimmer, and varying a lot from one LED to the next, because only a few hundred mV is left across the resistor. All three on at full duty is about 17 mA typical, 31 mA worst case.
Workshop tip: set brightness in code (scale the duty, e.g. `ledcWrite(pin, 100)` instead of 255) rather than swapping resistors. If one LED is too dim, measure its Vf with a multimeter in diode mode and recompute.

Common cathode vs common anode:
- Common cathode (this build): longest leg to GND, higher duty = brighter.
- Common anode: longest leg to **3V3**, the output is inverted (LOW = on). Set `RGB_COMMON_ANODE 1` in pins.h (`RGB_LEVEL()` flips the duty). The resistors stay in the same place. In Wokwi the LED part has a `common` attribute for this.

## 4. Buzzer, tone() and core versions

- Passive buzzer on GPIO23. The PS1240 piezo is driven straight from the GPIO (3.3 V, a few mA, it is a capacitive load). It is quieter than at 5 V; that is normal. Do not drive a magnetic (coil) buzzer directly from a GPIO.
- **I target the arduino-esp32 3.x core** (the `esp32` package by Espressif in Boards Manager; compiled here with 3.3.12). In 3.x:
  - `tone(pin, freq)` and `noTone(pin)` work (they use the LEDC PWM peripheral internally).
  - LED PWM: `ledcAttach(pin, freq, bits)` once in `setup()`, then `ledcWrite(pin, duty)`. No channel numbers.
- The 2.x core is different: `ledcSetup(channel, freq, bits)` + `ledcAttachPin(pin, channel)` + `ledcWrite(channel, duty)`, and, as far as I know, no `tone()` (use `ledcWriteTone(channel, freq)`). This sketch does **not** compile on 2.x. I did not install 2.x to check the exact differences. If someone has an old core, update it in Boards Manager.
- The core version Wokwi uses is whatever Wokwi ships; I could not check it. If Wokwi's compile complains about `ledcAttach`, that is the reason.

## 5. USB power budget

The board is powered from USB (a USB 2.0 port gives up to 500 mA once enumerated). Calculated worst case, not measured:

| Load | Current |
|---|---|
| ESP32 with WiFi transmitting | roughly 240 mA average, short peaks higher (check "Power consumption" in the ESP32 datasheet) |
| USB-UART chip + power LED | about 20 mA |
| OLED | 10-20 mA |
| RGB LED, all on | 17-31 mA |
| Buzzer (piezo) | a few mA |
| Total | about 320 mA worst case, so fine on a normal port |

Use a short, good-quality cable (thin cheap cables drop voltage and cause resets when WiFi transmits), a laptop port or a phone charger, and no unpowered hubs. "Brownout detector was triggered" in the serial log means a power problem, not a code problem.

## 6. Layout plan (expansion board + half-size breadboard, see PARTS.md)

Why not plug the ESP32 straight into a breadboard: a 1.0 in wide board covers nearly every hole next to its own pins (calculation in PARTS.md). So the plan is: ESP32 on a 30-pin expansion board, jumpers to a half-size breadboard that carries the small parts. This is a **plan, not a tested layout** (hole numbers will depend on your breadboard).

| Parts | Where on the breadboard | Notes |
|---|---|---|
| Rails | top rail = GND (one jumper to GND), bottom rail = 3V3 (one jumper to 3V3) | Keep the same colours as the table: black for GND, red for 3V3. |
| BTN1, BTN2, BTN3 | each straddles the centre channel, about 4 columns apart, left end | One side to the GND rail, the other side by a grey jumper to GPIO25/26/27. |
| RGB LED + 3 resistors | middle | Long leg to the GND rail. Each colour leg goes through its resistor (150 / 47 / 47) to GPIO19 / 18 / 4. |
| Buzzer | right of the LED | Negative to GND rail, positive to GPIO23. |
| OLED | plugged into 4 female-male jumpers, or its header in the right-hand columns | VCC=3V3, GND, SDA=GPIO21, SCL=GPIO22. |

Take a photo of the first finished clock and add it to this folder.

## 7. Pre-session test checklist (every clock)

1. Visual: no loose header pins, LED long leg on GND, resistors 150 / 47 / 47 ohm (colour bands: 150 = brown-green-brown, 47 = yellow-violet-black).
2. Plug in the USB cable. The power LED on the ESP32 lights and nothing gets hot.
3. The board appears as a COM port (Windows Device Manager > Ports).
4. Copy `wokwi/secrets.example.h` to `wokwi/secrets.h` and put in the hotspot name and password (2.4 GHz). Never commit this file; it is in .gitignore.
5. Upload `wokwi/sketch.ino` (board: DOIT ESP32 DEVKIT V1, or ESP32 Dev Module). See WOKWI.md for the folder-name rule in the Arduino IDE.
6. OLED shows "no time yet", then the time and date a few seconds after WiFi connects, top-right says "WiFi". Check the time against your phone (Sydney time).
7. RGB LED cycles red, green, blue every half second. Green and blue dimmer than red is expected.
8. Each of the 3 buttons beeps with a different pitch (low, middle, high) and its box on the OLED turns white while held.
9. Serial Monitor at 115200 prints "button SET pressed" etc.
10. Turn the hotspot off and reset the board: it shows "no time yet" (there is no battery-backed clock). An already-synced clock keeps counting on the ESP32's own timer until power-off.

## 8. Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| OLED blank, Serial says "OLED not found", LED blinks red | Wrong address, SDA/SCL swapped, no power | Swap SDA/SCL. Try address 0x3D in pins.h. Run an I2C scanner. Check VCC is on 3V3 and GND is connected. |
| OLED garbled or shifted | The module is a 1.3 in SH1106 sold as "SSD1306" | Use an SH1106-capable library (U8g2) or buy a true SSD1306. |
| Boot loop (repeating "rst:..." lines) or "Brownout detector was triggered" | A strapping pin (0, 2, 5, 12, 15) wired to something, or weak USB power | Unplug everything from those pins. Try another cable and port. |
| Upload fails: "Failed to connect to ESP32: Timed out waiting for packet header" | Board not entering download mode, bad cable | Hold **BOOT**, tap **EN**, release BOOT when "Connecting........" appears. Some boards need a 10 uF capacitor between EN and GND. Use a data cable. |
| No COM port | Charge-only cable or missing CP210x/CH340 driver | Try another cable first, then install the driver (PARTS.md). |
| Never gets the time | WiFi not connecting | The ESP32 is **2.4 GHz only**. Phone hotspot: turn on "Maximise Compatibility" (iPhone) or select the 2.4 GHz band (Android). eduroam (WPA2-Enterprise) does not work with `WiFi.begin(ssid, password)`. Check secrets.h exists and has no typos. |
| Time wrong by 1 hour or more | TZ string | `TZ_SYDNEY` in pins.h must be `AEST-10AEDT,M10.1.0,M4.1.0/3`. |
| Button always reads pressed | 4-leg button turned the wrong way (two legs of a pair are always connected) | Turn it 90 degrees. |
| LED shows the wrong colour | R/G/B legs swapped | Swap the wires, or check the LED datasheet for the leg order. |
| Green/blue very dim or off | Resistor too large | 47 ohm, not 220 ohm (section 3). |
| Random resets when WiFi connects | USB cable or port too weak | Section 5. |

## 9. Offline fallback and Bluetooth (design notes, not implemented)

The clock needs WiFi only to fetch the time. Once synced, the ESP32 keeps counting on its own timer (drift of a few seconds per day) until power is removed. If the venue has no usable WiFi: (a) use a phone hotspot or travel router (best); (b) add a time-setting mode on the SET/NEXT buttons as in the Uno version; or (c) add a DS3231 module back on the I2C bus (SDA 21, SCL 22, address 0x68, shares the bus with the OLED). The DS3231 is dropped from the main design.

Bluetooth: not built. A possible later use is BLE to set alarms from a phone. It needs no extra pins. BLE and WiFi share the one radio and need flash/RAM; the test sketch uses about 73% of the default app partition with WiFi alone, so BLE would probably need a larger partition scheme (not checked).
