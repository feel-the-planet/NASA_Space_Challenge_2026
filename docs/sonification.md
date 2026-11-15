# Sonification: from NASA data to sound

The challenge asks for real-time sonification that is meaningful and pleasant, not chaotic. These are our rules and the reasons behind them.

## 1. One instrument per variable (timbre = *what* you hear)

| Variable | Instrument | Why |
|---|---|---|
| CO₂ | **Organ**: deep, dense, with slow beating between two slightly detuned voices | CO₂ is heavy and "thick" in the atmosphere, so the sound is thick too |
| Temperature | **Trumpet**: bright brass with vibrato | Warmth and energy; easy to tell apart from the others |
| Elevation | **Flute** with breath noise and a slow swell | Air and height, from the coast up to the mountain peaks |

Instruments are synthesized in real time from harmonics, so no recorded samples are used. Each one is a seamless loop with an exact whole number of cycles, so it can repeat forever without clicks.

## 2. Pitch follows the value (pitch = *how much*)

```text
normalized value (0-1)  ->  0 to 24 semitones above the base note (2 octaves)
```

| Variable | Value range | Lowest note | Highest note |
|---|---|---|---|
| CO₂ | 2nd–98th percentile of the layer (~391–404 ppm) | C2 (65 Hz) | C4 (262 Hz) |
| Temperature | −40 °C to 40 °C | F3 (175 Hz) | F5 (698 Hz) |
| Elevation | 0 m to 4500 m | C4 (262 Hz) | C6 (1047 Hz) |

**Low value = low pitch, high value = high pitch** for every variable. People understand this mapping intuitively.

## 3. Continuous and smooth

- The note is sustained while the finger is on the map. It does not beep.
- Pitch **glides**. The target value is smoothed every frame, and each step (a half-semitone) is cross-faded over 70 ms.
- If the camera loses the finger for a moment, the sound continues for 0.35 s, so it does not stutter.
- Where a variable has no data (for example, elevation over the ocean), the note keeps its last pitch at low volume instead of going silent.

## 4. The voice never interrupts the music

The place name ("Pacific Ocean", "South America") is spoken **on top of** the instrument. The instrument only drops to 45 % volume while the voice speaks.

## 5. Learning the direction

When you choose a variable, the voice says its name and then the instrument plays a **sweep from low to high**, so you learn which direction means "more".

## Tunable parameters (`feel_the_planet.py`)

`RANGO_SEMITONOS`, `PASOS_SEMITONO`, `SUAVIZADO`, `VOL_CON_VOZ`, `VOL_SIN_DATO`, `GRACIA_DEDO`, and the `base` note and `rango` of each entry in `VARIABLES`.
