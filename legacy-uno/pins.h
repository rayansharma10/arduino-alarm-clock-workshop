// pins.h  -  pin map for the workshop alarm clock (Arduino Uno R3)
// Mirrors WIRING.md and wiring.png. If you change a pin here, change the wiring too.
#ifndef PINS_H
#define PINS_H

// ---- TM1637 4-digit display (2-wire serial, NOT I2C: any two digital pins work)
#define PIN_TM_CLK       2
#define PIN_TM_DIO       4

// ---- DS3231 real-time clock (I2C: the Uno's I2C pins are fixed in hardware)
#define PIN_I2C_SDA      A4     // informational only: Wire.h uses A4/A5 automatically
#define PIN_I2C_SCL      A5
#define RTC_I2C_ADDR     0x68   // DS3231 chip address (the EEPROM on some modules is at 0x57)

// ---- Passive buzzer (PS1240 piezo or KY-006 module), driven with tone()
// tone() takes over Timer2 on the Uno, which disables analogWrite() on D3 and D11.
// Nothing in this design needs PWM on D3 or D11, so keep it that way.
#define PIN_BUZZER       8

// ---- RGB LED (each colour through its own 220 ohm resistor). All three are PWM pins.
#define PIN_LED_R        5      // PWM (Timer0)
#define PIN_LED_G        6      // PWM (Timer0)
#define PIN_LED_B        9      // PWM (Timer1)

// 0 = common-cathode LED (long leg to GND)   -> analogWrite(pin, value) as normal
// 1 = common-anode LED   (long leg to 5V)    -> output is inverted
// If you set this to 1 you must also move the long-leg wire from the GND rail to the 5V rail.
#define RGB_COMMON_ANODE 0
// Use RGB_LEVEL() so the same code works for both LED types:  analogWrite(PIN_LED_R, RGB_LEVEL(255));
#define RGB_LEVEL(v)     (RGB_COMMON_ANODE ? (255 - (v)) : (v))

// ---- Buttons: other leg of each button goes to GND. Use pinMode(pin, INPUT_PULLUP).
// Pressed = LOW, released = HIGH. Debounce in software (about 20-50 ms).
#define PIN_BTN_HOUR     10     // BTN 1: set hour / mode
#define PIN_BTN_MINUTE   11     // BTN 2: set minute / next
#define PIN_BTN_SNOOZE   12     // BTN 3: snooze / stop alarm
#define BTN_PRESSED      LOW

// ---- Free pins, safe to use for extra experiments
// D7, D13 (D13 also drives the on-board LED), A0-A3.
// Avoid D0/D1 (USB serial), D3 and D11 as PWM while tone() is used.

#endif  // PINS_H
