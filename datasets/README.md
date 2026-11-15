# Datasets | Feel the Planet! 🌍🔊

**Touch the Earth. Hear the Science.**

This folder documents the NASA Earth observation resources used by **Feel the Planet!**. **Dataset files are not stored in this GitHub repository.** Instead, users can download them from NASA or access supported services directly when running the application.

This approach keeps the repository lightweight, respects each source's access conditions, and makes it easier to use updated data.

## Official NASA data sources

| Source | What it provides | Access |
|---|---|---|
| [NASA Worldview](https://worldview.earthdata.nasa.gov/) | Interactive satellite imagery and Earth science visualization layers | Browse online; export an image or open the original dataset through Earthdata Search |
| [NASA Worldview Snapshots](https://wvs.earthdata.nasa.gov/) | Image snapshots for selected layers, dates, and geographic areas | Download a generated image; copy its download link for reproducibility |
| [NASA MERRA-2](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/) | Gridded atmospheric reanalysis variables | Select a collection and download a subset through NASA GES DISC |
| [NASA GES DISC](https://disc.gsfc.nasa.gov/) | Dataset discovery, subsetting, and download services for MERRA-2 | Free [NASA Earthdata Login](https://urs.earthdata.nasa.gov/) may be required |

> **Scientific note:** A Worldview image is a visual representation, not necessarily a numerical measurement. For data-driven sonification, use the underlying scientific product or explicitly document how image colors or intensities are interpreted. MERRA-2 values are model-based reanalysis estimates, not measurements from a sensor at the precise location touched by the user.

## How to obtain the data

### Option A — NASA Worldview: download imagery manually

1. Open [NASA Worldview](https://worldview.earthdata.nasa.gov/).
2. Choose a layer and the date or time to explore.
3. Select the geographic region and note the **layer/product name**, date, map projection, and geographic extent.
4. Use Worldview's image export, or use [Worldview Snapshots](https://wvs.earthdata.nasa.gov/) to generate a downloadable image in an available format.
5. Save the image locally in `datasets/local/worldview/` (not in Git).
6. Record the NASA source link and the layer settings. If your application needs physical values, follow the layer's link to its original data product via [Earthdata Search](https://search.earthdata.nasa.gov/).

**For repeatable downloads:** Save the exact image-download URL supplied by NASA or the Worldview configuration link. Do not assume that a Worldview share link is itself an image-file URL.

### Option B — MERRA-2: download numerical data

1. Create or sign in to a free [NASA Earthdata Login](https://urs.earthdata.nasa.gov/).
2. Open the [MERRA-2 information page](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/) or [GES DISC](https://disc.gsfc.nasa.gov/).
3. Search for the MERRA-2 collection relevant to your intended variable (for example, a near-surface meteorology collection).
4. On the product page, select **Subset/Get Data** and choose the variable(s), geographic region, and dates. Download a small subset rather than the complete global archive.
5. Choose an available format such as **netCDF**, follow the service's authentication and download steps, and save the result in `datasets/local/merra-2/`.
6. Record the exact **collection ID, variable names, units, spatial/temporal resolution, date range, and product URL or DOI**.

Some GES DISC data services require authorizing the GES DISC application in Earthdata Login. NASA provides [Python access and download tutorials](https://github.com/nasa/gesdisc-tutorials), including examples for authenticated access and subsetting.

## Direct access from the application (without adding files to Git)

The Python application can use either:

- **Remote access:** Read data through a NASA-supported HTTPS, OPeNDAP, or other documented endpoint, where the selected product supports it.
- **Local cache:** Download the selected file once from NASA and reuse the copy in `datasets/local/` for faster demonstrations and offline operation.

The exact download URL, collection, and variables must be selected before automatic retrieval can be fully configured. **No NASA download endpoint or working automatic downloader is implied by this README.**

### Example: download a public file from its direct NASA URL

Once you have obtained a **direct, downloadable file URL** (not the URL of an HTML page), you can download the file with Python:

```python
from pathlib import Path
import requests

# Replace with a direct public download URL provided by NASA.
file_url = "PASTE_DIRECT_NASA_FILE_URL_HERE"
destination = Path("datasets/local/worldview/downloaded-file.png")

if file_url.startswith("PASTE_"):
    raise ValueError("Insert the direct download URL supplied by NASA.")

destination.parent.mkdir(parents=True, exist_ok=True)
with requests.get(file_url, stream=True, timeout=120) as response:
    response.raise_for_status()
    with destination.open("wb") as output:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                output.write(chunk)

print(f"Saved to: {destination}")
```

Install the dependency with `pip install requests`. **This example is for public file URLs only.** MERRA-2 downloads that require Earthdata Login need NASA's authenticated download workflow; use the linked GES DISC tutorials rather than placing credentials in code or committing them to GitHub.

## Recommended repository layout

```text
datasets/
├── README.md                 # Sources and retrieval instructions (tracked)
├── sources.example.csv       # Optional inventory of NASA product links (tracked)
└── local/                    # Downloaded data (NOT tracked)
    ├── worldview/            # Exported imagery, when needed locally
    └── merra-2/              # netCDF or other NASA data subsets
```

The `local/` folders are created when needed; GitHub does not store empty directories.

### Add to `.gitignore`

Add the following lines to the **root** `.gitignore` file:

```gitignore
# Downloaded NASA data and local caches
datasets/local/

# Optional: Python caches
__pycache__/
*.pyc
```

If large datasets were already committed, adding `.gitignore` does **not** remove those files from Git's tracking. They must be untracked separately before committing the change.

## Dataset reference checklist

For each layer or product actually used, record the following in the project documentation:

- [ ] NASA source and direct product URL or DOI
- [ ] Exact Worldview layer name or MERRA-2 collection ID
- [ ] Scientific variable and units (or image color legend)
- [ ] Date/time range and geographic extent
- [ ] Spatial and temporal resolution
- [ ] Download, subset, or remote-access method
- [ ] Transformations or normalizations used for sonification
- [ ] Missing-data handling and known limitations

## How Feel the Planet! uses the data

1. The camera detects an index finger over the 3D map.
2. The application converts that position into geographic coordinates.
3. A selected NASA product supplies a value or a documented visual feature for the location and time.
4. A transparent mapping converts that information into sound (such as pitch, rhythm, volume, or timbre).
5. The interface displays the source, date, units, and any uncertainty or unavailable-data message.

**Sound is an interpretation of Earth data, not a literal sound recorded by Earth.**

## References and acknowledgment

- [NASA Worldview — Earthdata](https://worldview.earthdata.nasa.gov/)
- [NASA Worldview Snapshots](https://wvs.earthdata.nasa.gov/)
- [NASA GMAO — MERRA-2](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/)
- [NASA GES DISC — Data Portal](https://disc.gsfc.nasa.gov/)
- [NASA GES DISC — Python Tutorials](https://github.com/nasa/gesdisc-tutorials)

**Acknowledgment:** Feel the Planet! uses or references NASA Earth observation resources. Cite each individual dataset and its DOI where available. NASA does not endorse this independent project.

---

**Feel the Planet! — Touch the Earth. Hear the Science.**
