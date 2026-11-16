/*
  Feel the Planet! - Button panel as a Bluetooth keyboard (ESP32 classic / ESP-WROOM-32)

  Each button sends the same key the app already uses, so the Python app
  needs no changes. Wire every button between its GPIO and GND
  (internal pull-up, no resistors needed).

  Library: "ESP32 BLE Keyboard" by T-vK  (Arduino Library Manager or GitHub)
  Board:   "ESP32 Dev Module"
  Note:    if it does not compile with esp32 core 3.x, install esp32 core 2.0.17
           (Tools > Board > Boards Manager > esp32).

  First use: Windows Settings > Bluetooth & devices > Add device > Bluetooth >
             "Feel the Planet Buttons". The blue LED (GPIO 2) turns on when connected.
*/
#include <BleKeyboard.h>

BleKeyboard teclado("Feel the Planet Buttons", "Feel the Planet", 100);

struct Boton { uint8_t pin; char tecla; const char *funcion; };

Boton botones[] = {
  {13, '1', "CO2 (organ)"},
  {14, '2', "Temperature (trumpet)"},
  {27, '3', "Elevation (flute)"},
  {26, 'l', "Language EN / ES"},
};
const int N = sizeof(botones) / sizeof(botones[0]);
const uint8_t LED = 2;              // blue LED on the board
const unsigned long REBOTE_MS = 40; // debounce

bool estable[N];
bool lectura_ant[N];
unsigned long t_cambio[N];

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  for (int k = 0; k < N; k++) {
    pinMode(botones[k].pin, INPUT_PULLUP);
    estable[k] = lectura_ant[k] = HIGH;
    t_cambio[k] = 0;
  }
  teclado.begin();
  Serial.println("Feel the Planet buttons ready. Pair 'Feel the Planet Buttons' via Bluetooth.");
}

void loop() {
  bool conectado = teclado.isConnected();
  digitalWrite(LED, conectado ? HIGH : LOW);

  for (int k = 0; k < N; k++) {
    bool lectura = digitalRead(botones[k].pin);
    if (lectura != lectura_ant[k]) {       // something changed: restart debounce timer
      t_cambio[k] = millis();
      lectura_ant[k] = lectura;
    }
    if (millis() - t_cambio[k] > REBOTE_MS && lectura != estable[k]) {
      estable[k] = lectura;
      if (estable[k] == LOW) {             // button pressed
        Serial.printf("Button GPIO %d -> '%c' (%s)%s\n", botones[k].pin, botones[k].tecla,
                      botones[k].funcion, conectado ? "" : "  [not connected]");
        if (conectado) teclado.write(botones[k].tecla);
      }
    }
  }
  delay(2);
}
