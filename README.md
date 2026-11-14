# Feel the Planet! 🌍

**Touch the Earth. Hear the Science.**

*An interactive, open-source way to explore Earth science through touch, sight, and sound.*

**NASA Space Apps Challenge 2026**  
**Challenge:** The Earth Information Jukebox

## What is Feel the Planet?

Feel the Planet! is an educational project that turns Earth science data into an interactive experience.

Users point to a location on a **3D-printed relief map of Earth**. A camera above the map tracks their index finger, and a computer responds with sound. The goal is to make those sounds represent real environmental data from NASA, helping people explore how conditions vary around the world.

Imagine pointing to two different places on Earth and **hearing the difference** between their environmental conditions.

## Why are we building it?

NASA provides valuable information about our planet, but scientific maps, graphs, and datasets can be difficult to explore without specialized knowledge.

We want to make Earth data more approachable through a hands-on learning experience. Feel the Planet! combines **a physical map, computer vision, visual information, and data sonification** to invite people to discover science in a new way.

**Data sonification** means using sound to represent information. For example, a measured value can control a sound's pitch, rhythm, or intensity. These relationships should be documented so the sounds are meaningful, not random.

## How does it work?

1. **Point** — The user points to a place on the 3D Earth map.
2. **Detect** — An overhead camera detects the index finger.
3. **Locate** — The software maps the finger position to a geographic location.
4. **Select** — The user chooses an environmental variable using buttons or the interface.
5. **Explore** — The application looks up the relevant scientific value and translates it into sound while displaying the information on screen.

```text
3D-printed Earth map
        |
Overhead camera -> Finger tracking
        |
Geographic location + Selected variable
        |
NASA Earth data -> Sonification rules
        |
   Sound + On-screen information
```

## Project status

Feel the Planet! is a **work in progress**.

**Already prototyped**
- [x] A 3D relief model of Earth.
- [x] Index-finger detection through an overhead camera.
- [x] Sound playback that changes with the selected mode or variable.

**Next steps**
- [ ] Calibrate the camera and convert finger positions into geographic coordinates.
- [ ] Connect a documented NASA Earth dataset to the sound engine.
- [ ] Define and explain the sound mapping for each variable.
- [ ] Integrate physical variable-selection buttons.
- [ ] Show the location, selected variable, measured value, units, and data source on screen.
- [ ] Publish printable files, assembly instructions, and a reproducible software setup.
- [ ] Test the complete experience with users.

> **Important:** The current sound prototype should not be interpreted as a scientifically validated representation of NASA data until the dataset integration and sound mapping have been completed and tested.

## What can people explore?

The system is designed to support environmental variables such as:

- **Temperature** — Explore warmer and cooler conditions.
- **Precipitation** — Compare rainfall across regions.
- **Vegetation** — Discover differences in plant coverage or activity.

The exact variables, datasets, dates, and geographic resolution will be listed as they are implemented. Not every NASA dataset provides a value for every point or time period.

We also plan to share **interchangeable 3D maps** that use different textures or relief patterns to represent environmental variables.

## What do we use?

| Component | Role |
| --- | --- |
| 3D-printed relief map | Physical exploration surface |
| Overhead camera | Captures hand movements |
| Python and OpenCV | Camera processing and interaction |
| Hand-tracking software | Detects the index finger |
| NASA Earth science data | Scientific information for sonification |
| Audio engine | Turns data into sounds |
| Physical buttons / controller | Selects variables (planned) |
| Computer screen and speakers | Displays information and plays sound |

Some components are still being integrated. Exact hardware models and software dependencies will be documented after testing.

## Repository guide

As the project grows, this repository is intended to include:

```text
feel-the-planet/
├── README.md              # Project overview
├── app/                   # Python application
│   ├── vision/            # Finger tracking and map calibration
│   ├── data/              # NASA data loading and processing
│   ├── audio/             # Sound generation
│   └── interface/         # User interface
├── hardware/
│   ├── 3d-models/         # Editable 3D designs
│   ├── printable-maps/    # Files for 3D printing
│   ├── button-panel/      # Button enclosure and layout
│   └── assembly-guide/    # Build instructions
├── firmware/              # Code for physical controls
├── datasets/              # Metadata and sample data
├── docs/                  # Installation and educational guides
├── tests/                 # Validation and tests
└── demo/                  # Photos and demonstration video
```

*This is the planned structure. Some folders may not exist yet.*

## Build your own (coming soon)

We want students, teachers, makers, and researchers to be able to recreate Feel the Planet! using commonly available tools.

The full build guide will explain:

1. How to download and print the Earth map.
2. How to position and calibrate the overhead camera.
3. How to assemble and connect the selection buttons.
4. How to install the Python application and its dependencies.
5. How to download or load the supported NASA datasets.
6. How to start the software, test the interaction, and troubleshoot common issues.

**Installation commands will be added once the software and dependency versions have been verified.**

## Open science and accessibility

Our long-term goal is to make Feel the Planet! a reusable **open-source educational resource**. We plan to share code, 3D models, assembly documentation, and learning activities.

We are exploring ways to improve accessibility, including clear on-screen labels, explanations of sounds, and different ways to interact with the system. Accessibility features will be documented as they become available and are tested.

## Scientific transparency

We will identify the NASA dataset used for each variable, including its source, units, time period, and spatial resolution. We will also explain how numerical values are mapped to audio parameters.

This project is for **science education and exploration**. It is not a forecasting tool, and it should not be used to make safety-critical or scientific decisions without consulting the original datasets and their limitations.

## Contributing

Ideas, bug reports, documentation improvements, 3D design contributions, and educational activities are welcome. As the repository develops, we will add contribution guidelines and a process for reporting issues.

## License and credits

The team intends to release its original work openly. **License details for the software and 3D designs will be published after review.** Please check the repository's license files before reusing materials.

Created for **NASA Space Apps Challenge 2026** — *The Earth Information Jukebox*.

This is an independent team project and is **not an official NASA product**. NASA datasets and third-party assets remain subject to their respective terms and attribution requirements.

**Feel the Planet! — Touch the Earth. Hear the Science.**
