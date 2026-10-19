# Arduino / ESP32 alarm clock workshop

Beginner workshop for the UNSW computer engineering society. The clocks are pre-built; attendees change the code (display content, LED colours, buzzer sounds) rather than wiring from scratch.

## Versions

| Folder | Status | Board | Display | Time source |
|---|---|---|---|---|
| [`esp32/`](esp32/) | **Main version** | ESP32 DevKit (30-pin) | 0.96 in SSD1306 OLED (I2C) | WiFi NTP, Sydney time zone |
| [`legacy-uno/`](legacy-uno/) | Legacy (first design) | Arduino Uno R3 | TM1637 4-digit | DS3231 RTC |

## ESP32 version (main)
- Parts: [esp32/PARTS.md](esp32/PARTS.md). Wiring, resistor calculations, test checklist, troubleshooting: [esp32/WIRING.md](esp32/WIRING.md). Pin names: [esp32/pins.h](esp32/pins.h). Picture: [esp32/pin-diagram.png](esp32/pin-diagram.png).
- Try it in your browser (no hardware needed): **ESP32 project on Wokwi: https://wokwi.com/projects/478312582920814593**
- Simulator project and the wiring-test sketch: [esp32/wokwi/](esp32/wokwi/WOKWI.md). The sketch needs a `secrets.h` with your WiFi name and password: copy `esp32/wokwi/secrets.example.h` to `secrets.h` (it is gitignored, never commit it).
- WiFi is 2.4 GHz only and used for the time only. Venue WiFi is not decided: plan on a phone hotspot or a travel router (eduroam does not work with plain `WiFi.begin`).
- Bluetooth is not built yet. No pins are reserved for it.
- Status: calculated and compiled (arduino-esp32 3.3.12) and running in the Wokwi simulator; **not yet tested on real hardware**.

## Legacy Uno version
- Try it in your browser (no hardware needed): **Legacy Uno project on Wokwi: https://wokwi.com/projects/478272657617380353**
- Files: [legacy-uno/README.md](legacy-uno/README.md), [legacy-uno/WIRING.md](legacy-uno/WIRING.md), [legacy-uno/pins.h](legacy-uno/pins.h), [legacy-uno/wokwi/](legacy-uno/wokwi/).
