# Moon Visualizer

Calculates and visualizes the Moon's appearance (phase, illumination, and
Alt/Az sky position) for any date/time and observer location on Earth.

This is the same app as the original single-file `moon_visualizer1.py`,
now split into a proper **package** and rewritten so every class follows
clear **object-oriented design** (inheritance, polymorphism, abstraction,
encapsulation, composition). Every place an OOP concept is used has a
short `# OOP concept: ...` comment right next to it in the code.

## Running it

```bash
pip install skyfield matplotlib numpy PySide6
# Windows users may also need the IANA timezone database:
pip install tzdata

# Optional, but recommended: precise offline timezone lookup for the
# location map / Quick Settings popup. Without it, the app still works,
# just with a rougher longitude-only timezone guess.
pip install timezonefinder

python run.py
```

The first time you run it, the JPL planetary ephemeris (`de421.bsp`,
~17 MB) is downloaded and cached locally by Skyfield, so every later run
works fully offline.

## Picking a location

Both the first-time **setup wizard** and the **⚡ Quick settings** popup
now share the exact same location picker (`LocationPickerWidget`), so
finding a spot on Earth works identically everywhere in the app:

- **Search any country or city** by typing its name into the search box
  (e.g. "Nepal", "Tokyo") - matches from a bundled ~200-country gazetteer
  show up as you type (`geo/world_locations.py`), so you're not limited
  to the handful of places the map itself can draw.
- **Click or drag on the map** for a rough, visual pick - the map now
  outlines many more individual landmasses (Greenland, Madagascar,
  Japan, the British Isles, New Zealand, insular Southeast Asia, ...)
  instead of six giant blobs, though it's still a simplified silhouette,
  not survey data - search is the reliable way to land exactly on a
  small or oddly-shaped country.
- **Quick pick chips** jump straight to a handful of favourite cities.
- **Latitude / longitude / elevation** stay editable directly as exact
  numbers, always in sync with whatever the map/search just picked.
- **Timezone** follows the location automatically ("Auto-detect
  timezone from location", on by default) using `timezonefinder` when
  it's installed, or a coarser longitude-only estimate otherwise. Typing
  a timezone in manually switches auto-detect off.

## Quick settings popup

Once the simulation is running, the **⚡ Quick settings** button (next to
**✎ Full setup**) opens a small, toggleable popup for fast one-off
changes, without stepping through the full "When → Where → Review"
wizard. **Date** and **time** each have their own picker (calendar
drop-down / spinner), and each applies the instant it's changed - you
can update just the date, or just the time, and nothing else is
touched; **location** uses the shared picker described above and also
applies live.

Click **⚡ Quick settings** again (or **Close**) to hide the popup; the
simulation keeps whatever was last applied. **Open full setup wizard →**
inside the popup jumps to the complete wizard when that's what you
actually need.

## Folder structure

```
run.py                          # tiny launcher: python run.py
moon_visualizer/                # the actual package
│
├── __init__.py                 # re-exports MainWindow
├── main.py                     # entry point: builds QApplication + MainWindow
├── main_window.py              # MainWindow — the app's "composition root"
├── theme.py                    # Theme (colours) + global Qt stylesheet
│
├── models/                     # plain data classes ("the nouns")
│   ├── __init__.py
│   └── domain.py                 ObserverLocation, ObservationMoment,
│                                  MoonObservationResult, DEFAULT_OBSERVATION_VALUES
│
├── astronomy/                  # Skyfield-facing calculations
│   ├── __init__.py
│   ├── phase_namer.py            MoonPhaseNamer
│   ├── ephemeris_provider.py     EphemerisProvider
│   └── calculator.py             MoonCalculator
│
├── geo/                         # non-astronomy geographic helpers
│   ├── __init__.py
│   ├── timezone_resolver.py      TimezoneResolver (lat/lon -> IANA tz name)
│   └── world_locations.py        WorldLocation, ALL_LOCATIONS / FAVORITE_LOCATIONS,
│                                  find_by_name() - the ~200-country search gazetteer
│
├── widgets/                     # small, reusable Qt widgets
│   ├── __init__.py
│   ├── world_map_widget.py       WorldMapWidget (click-to-pick-a-location map)
│   └── location_picker_widget.py LocationPickerWidget (search + map + coords +
│                                  timezone - the ONE location UI shared by the
│                                  wizard's LocationStepPage and QuickSettingsDialog)
│
├── popups/                      # floating dialogs on top of a screen
│   ├── __init__.py
│   └── quick_settings_dialog.py  QuickSettingsDialog
│
├── panels/                     # the 5 Matplotlib panels in the figure
│   ├── __init__.py
│   ├── base_panel.py             Panel (abstract base class)
│   ├── moon_disk_panel.py        MoonDiskPanel
│   ├── sky_position_panel.py     SkyPositionPanel
│   ├── calendar_panel.py         CalendarPanel
│   ├── clock_panel.py            AnalogClockPanel
│   ├── info_panel.py             InfoPanel
│   └── figure_builder.py         MoonFigureBuilder (composes all 5 panels)
│
├── wizard/                      # the guided "When -> Where -> Review" flow
│   ├── __init__.py
│   ├── base_step_page.py         WizardStepPage (shared base for input steps)
│   ├── step_indicator.py         StepIndicator
│   ├── datetime_step_page.py     DateTimeStepPage   (step 1)
│   ├── location_step_page.py     LocationStepPage    (step 2)
│   ├── review_step_page.py       ReviewStepPage      (step 3)
│   └── setup_wizard.py           SetupWizard (composes the 3 steps)
│
└── views/                       # top-level screens
    ├── __init__.py
    ├── feature_card.py           FeatureCard
    ├── home_page.py               HomePage
    └── moon_view.py               MoonView
```

## OOP concepts used, and where to see them

| Concept | Where |
|---|---|
| **Encapsulation** | `Theme` (all colours in one namespace); every dataclass in `models/domain.py`; `_` -prefixed private fields/methods in every panel and view |
| **Immutability** | `@dataclass(frozen=True)` on `ObserverLocation`, `ObservationMoment`, `MoonObservationResult` |
| **Properties** | `ObservationMoment.aware_local` / `.utc` in `models/domain.py` |
| **Class methods / class-level shared state** | `EphemerisProvider` (a load-once cache) and `MoonPhaseNamer` in `astronomy/`; `TimezoneResolver` in `geo/` loads its (optional) timezone data once per instance the same way |
| **Abstraction (ABC)** | `panels/base_panel.py` — `Panel` declares `draw()` as `@abstractmethod` |
| **Inheritance** | Every `*Panel` class inherits from `Panel`; `DateTimeStepPage` / `LocationStepPage` inherit from `WizardStepPage`; every widget inherits from a PySide6 `QtWidgets` base class |
| **Polymorphism** | `MoonFigureBuilder.update()` calls `.draw(ax, result)` on 5 different `Panel` subclasses without caring which; `SetupWizard._go_next()` calls `.validate()` on whichever step page is current |
| **Composition ("has-a")** | `MoonFigureBuilder` holds 5 panels; `MoonView` holds a `MoonCalculator` + `MoonFigureBuilder` + a `QuickSettingsDialog`; `QuickSettingsDialog` and `LocationStepPage` both hold a `LocationPickerWidget`; `LocationPickerWidget` holds a `WorldMapWidget` + `TimezoneResolver`; `MainWindow` holds `HomePage` + `SetupWizard` + `MoonView` (the app's composition root) |
| **Observer pattern (Qt Signals)** | `HomePage`, `SetupWizard`, `MoonView` all expose `Signal`s that `MainWindow` listens to, instead of calling each other directly; `QuickSettingsDialog`, `LocationStepPage`, `LocationPickerWidget` and `WorldMapWidget` follow the same pattern (`values_changed`, `timezone_suggested`, `location_picked`, `preset_picked`) |

Every one of these is also called out with an inline comment at the exact
spot it appears in the code, so you can read the source top to bottom and
see the concept explained right where it's used.
