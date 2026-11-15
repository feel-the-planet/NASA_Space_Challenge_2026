# Datasets

**No data files are stored in this repository.** The app downloads the NASA layers it needs on the first run and caches them in `app/datos_nasa/`, which is ignored by Git.

| Variable | NASA product | GIBS layer | Date | Units |
|---|---|---|---|---|
| CO₂ | AIRS (Aqua) | `AIRS_L3_Carbon_Dioxide_IR_Monthly` | 2017-02-01 | ppm |
| Air temperature (2 m) | MERRA-2 (GMAO) | `MERRA2_2m_Air_Temperature_Monthly` | 2026-08-01 | K → °C |
| Terrain elevation | ASTER GDEM (Terra) | `ASTER_GDEM_Color_Index` | static | m |

- Endpoint: `https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi` (WMS 1.3.0, EPSG:4326, global, 720 × 360 px)
- Colormaps: `https://gibs.earthdata.nasa.gov/colormaps/v1.3/`
- Explore the same layers in [NASA Worldview](https://worldview.earthdata.nasa.gov/) using "Add layers".

How the colors are converted back into values, and the limitations of this method: **[../docs/nasa-data.md](../docs/nasa-data.md)**.

## Adding another variable

Add an entry to `VARIABLES` in `app/feel_the_planet.py` with the GIBS layer name, its colormap, the date, a unit conversion, a value range, an instrument and a base note. The app downloads and decodes it automatically.

NASA does not endorse this project. Please cite each NASA product when reusing the data.
