// Feel the Planet! - Button panel as a Bluetooth keyboard (NASA Space Apps 2026)
// Board: ESP32 DevKit (ESP-WROOM-32). Buttons on GPIO 32, 25, 26 and 27.
//
//   GPIO 32  Temperature button -> key '2'  (trumpet)
//   GPIO 25  CO2 button         -> key '1'  (organ)
//   GPIO 26  Elevation button   -> key '3'  (flute)
//   GPIO 27  Language button    -> key 'l'  (English / Spanish)
// The keys match the app: 1 = CO2, 2 = Temperature, 3 = Elevation, l = language.
//
// Wiring: each button between its GPIO and GND (internal pull-up, pressed = LOW).
// Library: "ESP32 BLE Keyboard" by T-vK - https://github.com/T-vK/ESP32-BLE-Keyboard

#include <BleKeyboard.h>

// Name shown in the Bluetooth list of the computer / phone
BleKeyboard bleKeyboard("Feel the Planet", "Hackatec", 100);

struct Boton {
  uint8_t pin;
  const char* nombre;
  char tecla;
  bool estadoEstable;
  bool lecturaAnterior;
  unsigned long ultimoCambio;
};

Boton botones[] = {
  {32, "Temperature", '2', HIGH, HIGH, 0},
  {25, "CO2",         '1', HIGH, HIGH, 0},
  {26, "Elevation",   '3', HIGH, HIGH, 0},
  {27, "Language",    'l', HIGH, HIGH, 0},
};

const int NUM_BOTONES = sizeof(botones) / sizeof(botones[0]);
const unsigned long DEBOUNCE_MS = 30;

bool estabaConectado = false;

void setup() {
  Serial.begin(115200);
  delay(500);

  for (int i = 0; i < NUM_BOTONES; i++) {
    pinMode(botones[i].pin, INPUT_PULLUP);
  }

  bleKeyboard.begin();

  Serial.println();
  Serial.println("=== Feel the Planet button panel (BLE) ===");
  Serial.println("Pair 'Feel the Planet' in the Bluetooth settings of your computer.");
}

void loop() {
  // Report connection changes on the serial monitor
  bool conectado = bleKeyboard.isConnected();
  if (conectado != estabaConectado) {
    estabaConectado = conectado;
    Serial.println(conectado ? ">> Bluetooth connected" : ">> Bluetooth disconnected");
  }

  unsigned long ahora = millis();

  for (int i = 0; i < NUM_BOTONES; i++) {
    Boton &b = botones[i];
    bool lectura = digitalRead(b.pin);

    if (lectura != b.lecturaAnterior) {          // debounce
      b.ultimoCambio = ahora;
      b.lecturaAnterior = lectura;
    }

    if ((ahora - b.ultimoCambio) > DEBOUNCE_MS && lectura != b.estadoEstable) {
      b.estadoEstable = lectura;

      if (b.estadoEstable == LOW) {              // pressed
        Serial.print("Pressed: ");
        Serial.print(b.nombre);
        Serial.print(" -> '");
        Serial.print(b.tecla);
        Serial.print("'");

        if (conectado) {
          bleKeyboard.write(b.tecla);            // press and release the key
          Serial.println("  [sent]");
        } else {
          Serial.println("  [not connected, not sent]");
        }
      }
    }
  }

  delay(1);
}
