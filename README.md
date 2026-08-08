# ASROCK 4x4 BOX-8840U Case

Parametric FreeCAD project for a custom enclosure and cooling concept for the ASROCK 4X4 BOX-8840U.

## Concept

- Preserve the original CPU heatsink.
- 170 x 170 x 10 mm base concept.
- 40 mm feet.
- 150 x 150 mm ventilation / lamella field.
- M3 mounting features with optional hex-head pockets.
- Designed around filtered intake and controlled exhaust airflow.
- FreeCAD is the CAD platform.

## Project layout

- `config.py` – central parameters
- `bottom.py` – base plate generation
- `lid.py` – lid / upper enclosure generation
- `export.py` – STEP/STL export helper
- `parts/` – reusable parametric parts
- `docs/` – design notes
- `stl/` and `step/` – generated output directories

The scripts are intended to be run from FreeCAD's Python console or as FreeCAD Python files.