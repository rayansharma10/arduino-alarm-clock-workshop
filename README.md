# Arduino alarm clock workshop

Beginner Arduino workshop for the UNSW computer engineering society. The clocks are pre-built; attendees change the code (display, LED colours, buzzer sounds) rather than wiring from scratch.

**Try it in your browser (no hardware needed): https://wokwi.com/projects/478272657617380353**

## Parts (per clock)
- Arduino Uno R3 + USB cable
- Small breadboard
- TM1637 4-digit display
- DS3231 RTC module with CR2032 (Wokwi simulates a DS1307 instead, see the sketch)
- Passive buzzer (TDK PS1240 or KY-006)
- RGB LED (common cathode) + 3 x 220 ohm resistors
- 3 tactile buttons
- Jumper wires

## Pins
| Part | Pins |
|---|---|
| TM1637 | CLK D2, DIO D4 |
| DS3231 | SDA A4, SCL A5 |
| Buzzer | D8 |
| RGB LED | R D5, G D6, B D9 |
| Buttons | D10, D11, D12 (to GND, INPUT_PULLUP) |

Full wiring, resistor calculations and troubleshooting: [WIRING.md](WIRING.md). Pin names for code: [pins.h](pins.h).

## Folders
- `wokwi/` - the Wokwi project files (`sketch.ino`, `diagram.json`, `libraries.txt`). Libraries needed: TM1637 (Avishay Orpaz), RTClib (Adafruit).

## Status
Wiring is calculated and simulated, **not yet verified on real hardware**. The sketch is a wiring test, not the finished alarm clock.
