// secrets.example.h  -  COPY this file to secrets.h and edit it. secrets.h is in .gitignore.
// NEVER commit secrets.h or put real credentials in this example file.
//
// Use a 2.4 GHz network: a phone hotspot (set "Maximise compatibility" on iPhone) or a
// travel router. The ESP32 cannot join 5 GHz-only networks. eduroam (WPA2-Enterprise)
// will not work with plain WiFi.begin(ssid, password).
#define WIFI_SSID "YourHotspotName"
#define WIFI_PASS "YourHotspotPassword"
