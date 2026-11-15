# Calibration

The software needs to know where the physical map is in the camera image. Calibrate once, and again if you move the camera or the map. The calibration is saved in `app/calibracion_mapa.json`.

## Option A — Auto-calibration with white dots (recommended)

![Calibration dots](images/calibration_dots_guide.png)

1. Paint a **white dot (5–8 mm)** on the physical map at each of the 17 locations shown above. The dots need to stand out against the map color.
2. Fix the camera above the map so that the whole map is visible.
3. Run the app, keep your hands out of the image, and press **`A`**.

The app then:
- finds the bright, small, round blobs (morphological top-hat + shape filter),
- recognizes **which dot is which** by testing several hypotheses (previous calibration, the map outline, and a 15° rotation sweep) and refining them step by step (similarity → affine → homography with RANSAC),
- computes the **4 corners of the map** by itself,
- uses every recognized dot as a fine-adjustment point, then saves.

It works with the map rotated in any direction and with a few dots hidden. It needs at least 6 recognized dots. In calibration mode (`c`), detected dots are circled in pink.

If it detects things that are not dots (reflections) or misses the dots, adjust `PUNTO_UMBRAL`, `PUNTO_BRILLO_MIN` and `PUNTO_AREA` in `feel_the_planet.py`.

| # | Reference point | # | Reference point |
|---|---|---|---|
| 1 | Western tip of Alaska | 10 | Southern tip of Kamchatka |
| 2 | Southern tip of Greenland | 11 | Cape York (northern Australia) |
| 3 | Tip of Florida | 12 | Southwest corner of Australia |
| 4 | Strait of Gibraltar | 13 | Los Angeles |
| 5 | Eastern tip of Brazil | 14 | Lima (Peru) |
| 6 | Cape Horn | 15 | Northern Greenland |
| 7 | Southern tip of Africa | 16 | North Cape (Norway) |
| 8 | Horn of Africa (Somalia) | 17 | Cape Chelyuskin (northern Asia) |
| 9 | Southern tip of India | | |

## Option B — Manual calibration

1. Press **`c`**. Click the 4 corners of the map in order: top-left, top-right, bottom-right, bottom-left (top = North Pole).
2. Drag the corners until the guide map overlaps the printed one (`1`–`4` select a corner, `i`/`j`/`k`/`l` move it 1 px, `m` shows or hides the guide).
3. Optional fine adjustment: press **`p`** and mark each requested point with a click, or with your fingertip and `Space` (`n`/`b` next/previous, `x` delete, `z` delete all).
4. Press **`Enter`** to save.
