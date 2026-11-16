# Credits and licenses

## Source code
Feel the Planet! source code is released under the [MIT License](LICENSE).

## NASA data
Data accessed through **NASA GIBS** (Global Imagery Browse Services), the same imagery shown in **NASA Worldview**. NASA data are generally free of copyright restrictions; please cite each product:

- **AIRS** (Atmospheric Infrared Sounder, Aqua satellite), NASA JPL. Layer `AIRS_L3_Carbon_Dioxide_IR_Monthly`.
- **MERRA-2** (Modern-Era Retrospective analysis for Research and Applications, Version 2), NASA GMAO. Layer `MERRA2_2m_Air_Temperature_Monthly`.
- **ASTER GDEM** (ASTER Global Digital Elevation Model), NASA / METI, Terra satellite. Layer `ASTER_GDEM_Color_Index`.
- NASA GIBS: https://nasa-gibs.github.io/gibs-api-docs/ · NASA Worldview: https://worldview.earthdata.nasa.gov/

We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS).

NASA does not endorse this project. No NASA logos, flags or mission insignia are used.

## Libraries
- [OpenCV](https://opencv.org/) (Apache 2.0): camera capture and image processing
- [MediaPipe](https://developers.google.com/mediapipe) (Apache 2.0): Hand Landmarker model, downloaded at runtime from Google
- [NumPy](https://numpy.org/) (BSD)
- [pygame](https://www.pygame.org/) (LGPL): audio
- [edge-tts](https://github.com/rany2/edge-tts) (LGPL/GPL): neural voices (Microsoft online TTS service)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) (MPL 2.0): offline Windows voice
- [Pillow](https://python-pillow.org/) (HPND)
- [ESP32 BLE Keyboard](https://github.com/T-vK/ESP32-BLE-Keyboard) by T-vK: button panel firmware (Arduino)

## 3D relief map
_Team: document here the source of the elevation data and the author/license of the 3D map model (see `hardware/printable-maps/README.md`)._

## Reference map image
`app/mapa.jpg` is the flat world map used to define regions and calibration points. _Team: add its source and license here._
