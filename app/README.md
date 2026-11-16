# App — `feel_the_planet.py`

The whole application is a single Python file.

```bash
pip install -r ../requirements.txt
python feel_the_planet.py
```

## Main settings (top of the file)

| Setting | Default | Meaning |
|---|---|---|
| `CAMARA` | `1` | Camera: `0` laptop, `1`/`2` USB webcam or phone (DroidCam), or an IP camera URL |
| `ROTAR` | `90` | Rotates the image (0/90/180/270) so the map is landscape. Can also be changed live with `t` |
| `LLENAR` | `True` | `True` makes the camera image fill the map area (crops the edges a little); `False` shows the whole image |
| `IDIOMA` | `'en'` | `'en'` English or `'es'` Spanish (`L` switches live) |

## Files created at runtime (not in Git)

| File / folder | Content |
|---|---|
| `hand_landmarker.task` | MediaPipe hand model (downloaded once) |
| `datos_nasa/` | NASA GIBS layers (`.png`) and colormaps (`.xml`) |
| `voz/` | Cached voice clips (`.mp3`, English files start with `en_`) |
| `calibracion_mapa.json` | Calibration of your camera and map |

> Code comments and internal names are in Spanish (our team's working language). All documentation, the interface and the voice are in English by default.
