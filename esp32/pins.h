// pins.h  -  pin map for the workshop alarm clock (classic ESP32 DevKit, 30-pin)
// Mirrors WIRING.md and the diagrams. If you change a pin here, change the wiring too.
// Target core: arduino-esp32 3.x (3.3.x tested to compile). The ledc*/tone() calls below
// use the 3.x API; on core 2.x they will NOT compile (see WIRING.md section 4).
// The ESP32 is a 3.3 V chip: every pin here is 3.3 V logic and is NOT 5 V tolerant.
#ifndef PINS_H
#define PINS_H

// ---- SSD1306 0.96" 128x64 OLED (I2C). These are the default Wire pins on the ESP32.
#define PIN_I2C_SDA      21
#define PIN_I2C_SCL      22
#define OLED_I2C_ADDR    0x3C   // most modules; some are 0x3D (see WIRING.md). Power the OLED from 3V3.
#define OLED_WIDTH       128
#define OLED_HEIGHT      64

// ---- Passive buzzer (PS1240 piezo or KY-006 module), driven with tone()/noTone()
#define PIN_BUZZER       23

// ---- RGB LED (common cathode). One resistor per colour, different values (3.3 V!).
//      R: 150 ohm, G: 47 ohm, B: 47 ohm  (calculation in WIRING.md section 3)
#define PIN_LED_R        19
#define PIN_LED_G        18
#define PIN_LED_B        4
#define LED_PWM_FREQ     5000   // Hz, flicker-free
#define LED_PWM_BITS     8      // duty 0..255

// 0 = common-cathode LED (long leg to GND)    -> duty as normal
// 1 = common-anode LED   (long leg to 3V3)    -> output is inverted
// If you set this to 1 you must also move the long-leg wire from GND to 3V3.
#define RGB_COMMON_ANODE 0
#define RGB_LEVEL(v)     (RGB_COMMON_ANODE ? (255 - (v)) : (v))

// ---- Buttons: other leg of each button goes to GND. pinMode(pin, INPUT_PULLUP).
// Pressed = LOW, released = HIGH. Debounce in software (about 20-50 ms).
#define PIN_BTN_SET      25     // BTN 1: set / mode
#define PIN_BTN_NEXT     26     // BTN 2: next / change value
#define PIN_BTN_SNOOZE   27     // BTN 3: snooze / stop alarm
#define BTN_PRESSED      LOW

// ---- Time zone (POSIX TZ string): Sydney, AEST (UTC+10), daylight saving AEDT (+11)
// DST starts first Sunday of October 02:00, ends first Sunday of April 03:00.
#define TZ_SYDNEY        "AEST-10AEDT,M10.1.0,M4.1.0/3"

// ---- Free pins, safe to use for extra experiments / future features
// Output-capable, no boot side-effects: GPIO 13, 32, 33 (16/17 too, unless your module is a WROVER with PSRAM).
// GPIO 14 is also usable but pulses a PWM signal at boot, so a LED on it flashes briefly.
// Bluetooth (BLE) needs NO pins: it is inside the ESP32. Nothing is reserved for it.
// Avoid: GPIO 6-11 (flash), 0/2/5/12/15 (strapping), 1/3 (USB serial),
//        34-39 (input only, no pull-up, so no use for buttons without an external resistor).

#endif  // PINS_H
