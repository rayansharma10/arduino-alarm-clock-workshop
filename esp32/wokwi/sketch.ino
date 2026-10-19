// Alarm clock WIRING TEST  (classic ESP32 DevKit + SSD1306 OLED)
// Proves every connection in WIRING.md / pins.h works:
//   1. OLED shows the time from WiFi/NTP (big digits) and the date
//   2. RGB LED cycles red -> green -> blue
//   3. Each button beeps the buzzer with its own pitch and lights a box on the OLED
// Not the finished alarm clock: no alarm logic, no time-setting.
//
// Targets arduino-esp32 core 3.x (tone() and ledcAttach()/ledcWrite(pin, duty)).
// Libraries: Adafruit SSD1306 + Adafruit GFX Library (+ Adafruit BusIO).
//
// WOKWI SIMULATION LIMITS (the real board differs here):
//  - WiFi: the simulator offers an open network "Wokwi-GUEST" (used automatically when
//    there is no secrets.h). Real hardware needs secrets.h (copy secrets.example.h).
//  - Bluetooth/BLE is not simulated at all (this sketch does not use it anyway).
//  - The RGB LED part ignores the resistor values, so G and B look as bright as R.
//    On real hardware with 47 ohm they will be dimmer than red; see WIRING.md.
//  - The buzzer part plays tone() as a clean sound; a real piezo is quieter at 3.3 V.
//  - Boot/strapping pin behaviour, brownouts and USB power are not simulated.

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <time.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "pins.h"

#if __has_include("secrets.h")
  #include "secrets.h"             // real network (gitignored)
#else
  #define WIFI_SSID "Wokwi-GUEST"  // simulator network, open, no password
  #define WIFI_PASS ""
#endif

Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);  // -1 = no reset pin

const uint8_t buttonPins[3]  = { PIN_BTN_SET, PIN_BTN_NEXT, PIN_BTN_SNOOZE };
const char*   buttonNames[3] = { "SET", "NEXT", "SNZ" };
const int     buttonTones[3] = { 523, 659, 784 };   // C5, E5, G5 in Hz
bool          pressed[3]     = { false, false, false };

const uint8_t ledPins[3] = { PIN_LED_R, PIN_LED_G, PIN_LED_B };
uint8_t  ledStep = 0;                // 0 = red, 1 = green, 2 = blue
uint32_t lastLedChange = 0;

uint32_t toneOffAt = 0;              // millis() when the current beep ends (0 = silent)
uint32_t lastDraw  = 0;

// Light exactly one colour. RGB_LEVEL() flips the value if RGB_COMMON_ANODE is set in pins.h.
void showColour(uint8_t step) {
  for (uint8_t i = 0; i < 3; i++) {
    ledcWrite(ledPins[i], RGB_LEVEL(i == step ? 255 : 0));
  }
}

void beep(int hz, uint32_t ms) {
  tone(PIN_BUZZER, hz);
  toneOffAt = millis() + ms;
}

void drawScreen() {
  struct tm t;
  bool haveTime = getLocalTime(&t, 0);   // 0 = do not wait; false until NTP has answered
  char buf[24];

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Row 1 (y 0-7): date on the left, WiFi state on the right
  display.setTextSize(1);
  display.setCursor(0, 0);
  if (haveTime) {
    strftime(buf, sizeof(buf), "%a %d %b %Y", &t);
    display.print(buf);
  } else {
    display.print(F("no time yet"));
  }
  display.setCursor(OLED_WIDTH - 6 * 4, 0);
  display.print(WiFi.status() == WL_CONNECTED ? F("WiFi") : F("----"));

  // Rows 2-5 (y 12-43): big HH:MM, 4x font = 24 x 32 px per digit, 5 chars = 120 px
  display.setTextSize(4);
  display.setCursor(4, 12);
  if (haveTime) {
    strftime(buf, sizeof(buf), "%H:%M", &t);
    display.print(buf);
    // seconds as a thin bar under the digits (colon-blink replacement)
    display.fillRect(0, 46, (t.tm_sec * OLED_WIDTH) / 60, 2, SSD1306_WHITE);
  } else {
    display.print(F("--:--"));
  }

  // Bottom row (y 52-63): one box per button, filled while that button is held
  display.setTextSize(1);
  for (uint8_t i = 0; i < 3; i++) {
    int x = i * 43;
    if (pressed[i]) {
      display.fillRect(x, 52, 41, 12, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK);
    } else {
      display.drawRect(x, 52, 41, 12, SSD1306_WHITE);
      display.setTextColor(SSD1306_WHITE);
    }
    display.setCursor(x + (41 - 6 * strlen(buttonNames[i])) / 2, 54);
    display.print(buttonNames[i]);
  }
  display.display();
}

void setup() {
  Serial.begin(115200);

  // Buttons: other leg goes to GND, so use the internal pull-up. Released = HIGH.
  for (uint8_t i = 0; i < 3; i++) pinMode(buttonPins[i], INPUT_PULLUP);

  // RGB LED: core 3.x API, ledcAttach(pin, freq, bits) then ledcWrite(pin, duty)
  for (uint8_t i = 0; i < 3; i++) ledcAttach(ledPins[i], LED_PWM_FREQ, LED_PWM_BITS);
  showColour(0);

  pinMode(PIN_BUZZER, OUTPUT);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    // Nothing to show an error on, so use the LED: blink red forever, and tell the serial monitor
    Serial.println(F("OLED not found: check SDA/SCL/3V3/GND and the address (0x3C or 0x3D)"));
    while (true) {
      showColour(0); delay(200);
      for (uint8_t i = 0; i < 3; i++) ledcWrite(ledPins[i], RGB_LEVEL(0));
      delay(200);
    }
  }

  // WiFi is used for the time only. Start it without blocking: the screen shows "no time yet".
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  // NTP + Sydney time zone including daylight saving. Syncs by itself once WiFi is up.
  configTzTime(TZ_SYDNEY, "pool.ntp.org", "time.google.com");

  Serial.println(F("Wiring test running"));
}

void loop() {
  uint32_t now = millis();

  // 1. Buttons: beep with own pitch on the press edge, remember state for the screen
  for (uint8_t i = 0; i < 3; i++) {
    bool down = (digitalRead(buttonPins[i]) == BTN_PRESSED);
    if (down && !pressed[i]) {
      beep(buttonTones[i], 150);
      Serial.printf("button %s pressed\n", buttonNames[i]);
    }
    pressed[i] = down;
  }
  if (toneOffAt && (int32_t)(now - toneOffAt) >= 0) {
    noTone(PIN_BUZZER);
    toneOffAt = 0;
  }

  // 2. RGB LED: next colour every 500 ms (millis, so nothing blocks)
  if (now - lastLedChange >= 500) {
    lastLedChange = now;
    ledStep = (ledStep + 1) % 3;
    showColour(ledStep);
  }

  // 3. Screen: redraw 10 times a second
  if (now - lastDraw >= 100) {
    lastDraw = now;
    drawScreen();
  }
}
