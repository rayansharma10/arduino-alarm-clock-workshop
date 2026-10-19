// Alarm clock WIRING TEST  (Arduino Uno)
// Proves every connection in WIRING.md / pins.h works:
//   1. TM1637 shows the time from the RTC (colon blinks every second)
//   2. RGB LED cycles red -> green -> blue
//   3. Each button beeps the buzzer with its own pitch
//   4. Button states are printed to the Serial Monitor
// Not the finished alarm clock: no alarm logic, no time-setting.

#include <Wire.h>          // I2C, used by the RTC (A4 = SDA, A5 = SCL)
#include <RTClib.h>        // Adafruit RTClib: talks to the RTC chip
#include <TM1637Display.h> // library "TM1637" by Avishay Orpaz
#include "pins.h"          // the pin names (same file as the real clock)

// Wokwi only simulates a DS1307 (no DS3231 part). Both chips use I2C address
// 0x68 and RTClib reads them the same way, so the code is nearly identical.
// On the REAL clock (DS3231 module): comment out the next line.
#define SIMULATOR_DS1307
#ifdef SIMULATOR_DS1307
  RTC_DS1307 rtc;
#else
  RTC_DS3231 rtc;
#endif

TM1637Display display(PIN_TM_CLK, PIN_TM_DIO);

const uint8_t buttonPins[3]  = { PIN_BTN_HOUR, PIN_BTN_MINUTE, PIN_BTN_SNOOZE };
const int     buttonTones[3] = { 523, 659, 784 };   // C5, E5, G5 in Hz
bool          wasPressed[3]  = { false, false, false };

const uint8_t ledPins[3] = { PIN_LED_R, PIN_LED_G, PIN_LED_B };
uint8_t  ledStep = 0;                 // 0 = red, 1 = green, 2 = blue
uint32_t lastLedChange = 0;

void setup() {
  Serial.begin(9600);

  // Buttons: other leg goes to GND, so use the internal pull-up.
  // Released = HIGH, pressed = LOW (BTN_PRESSED in pins.h).
  for (uint8_t i = 0; i < 3; i++) pinMode(buttonPins[i], INPUT_PULLUP);

  for (uint8_t i = 0; i < 3; i++) pinMode(ledPins[i], OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  display.setBrightness(5);           // 0 (dim) to 7 (bright)

  if (!rtc.begin()) {
    Serial.println("RTC not found: check SDA/SCL (A4/A5) and power");
    display.showNumberDec(8888);      // visible error on the display
    while (true) {}                   // stop here
  }
  // Wokwi starts the DS1307 at your computer's current time. A real RTC that
  // lost power needs setting once, to the time this sketch was compiled:
#ifndef SIMULATOR_DS1307
  if (rtc.lostPower()) rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
#endif
  Serial.println("Wiring test running");
}

// Light exactly one colour of the RGB LED.
// RGB_LEVEL() flips the value if you set RGB_COMMON_ANODE in pins.h.
void showColour(uint8_t step) {
  for (uint8_t i = 0; i < 3; i++) {
    analogWrite(ledPins[i], RGB_LEVEL(i == step ? 255 : 0));
  }
}

void loop() {
  uint32_t now = millis();

  // 1. TIME on the display, HHMM with the colon blinking once per second.
  DateTime t = rtc.now();
  int hhmm = t.hour() * 100 + t.minute();
  uint8_t colon = (t.second() % 2 == 0) ? 0b01000000 : 0;   // bit 6 = colon
  display.showNumberDecEx(hhmm, colon, true);                // true = leading zeros

  // 2. RGB LED: next colour every 500 ms (millis, so nothing blocks).
  if (now - lastLedChange >= 500) {
    lastLedChange = now;
    ledStep = (ledStep + 1) % 3;
    showColour(ledStep);
  }

  // 3. BUTTONS: beep when a press STARTS (released -> pressed).
  for (uint8_t i = 0; i < 3; i++) {
    bool pressed = (digitalRead(buttonPins[i]) == BTN_PRESSED);
    if (pressed && !wasPressed[i]) {
      tone(PIN_BUZZER, buttonTones[i], 150);                 // pin, Hz, ms
      Serial.print("Button ");
      Serial.print(i + 1);
      Serial.println(" pressed");
    }
    wasPressed[i] = pressed;
  }
  delay(20);                                                 // crude debounce
}
