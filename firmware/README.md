# Firmware — button panel (ESP32 as a Bluetooth keyboard)

A classic **ESP32 DevKit (ESP-WROOM-32)** acts as a **Bluetooth keyboard**. Each physical button sends the same key that the app already understands, so `feel_the_planet.py` needs no changes.

> The classic ESP32 cannot act as a USB keyboard (its USB port is only a serial converter). That is why it uses Bluetooth Low Energy.

## Wiring

Each button goes between its pin and **GND**. The firmware uses the internal pull-up resistors, so no external resistors are needed.

| Button | ESP32 pin | Key sent | Function |
|---|---|---|---|
| 1 | D13 | `1` | CO₂ (organ) |
| 2 | D14 | `2` | Temperature (trumpet) |
| 3 | D27 | `3` | Elevation (flute) |
| 4 | D26 | `l` | Language EN / ES |

The blue LED on the board (GPIO 2) turns on when the panel is connected to the computer.

Power: USB cable from the computer or a phone charger / power bank (5 V).

## Install

1. Arduino IDE → **Boards Manager** → install **esp32** (Espressif). If the library below does not compile with core 3.x, use version **2.0.17**.
2. Install the library **ESP32 BLE Keyboard** (T-vK).
3. Board: **ESP32 Dev Module**. Open `feel_the_planet_buttons/feel_the_planet_buttons.ino` and upload it. If it does not start uploading, hold **BOOT** while it says "Connecting…".
4. On Windows: **Settings → Bluetooth & devices → Add device → Bluetooth → "Feel the Planet Buttons"**.

## Notes

- Like any keyboard, keys go to the **active window**. Keep the Feel the Planet window in front.
- The serial monitor (115200 baud) prints every button press, which is useful for testing the wiring.
- To change a key or a pin, or to add more buttons (for example `i` = say value, `s` = mute), edit the `botones[]` table at the top of the sketch.
