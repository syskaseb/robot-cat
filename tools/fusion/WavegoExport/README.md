# WAVEGO export bridge

This one-shot Autodesk Fusion add-in opens the untouched local `robot-cat`
backup archive in a temporary document and exports its embedded `WAVEGO PRO
BETA v3` component.  It never activates or reads `robot-cat-lokiec-work` and
does not modify or save either Fusion design.

Output goes to `hardware/wavego/source/`:

- `WAVEGO_PRO_BETA_v3.step` — neutral B-Rep assembly for FreeCAD;
- `WAVEGO_PRO_BETA_v3.f3d` — component archive retained as the source backup;
- `WAVEGO_PRO_BETA_v3.json` — hierarchy, body counts and bounding boxes;
- `WAVEGO_PRO_BETA_v3.png` — Fusion viewport reference;
- `fusion-export.log` — success or traceback.

The manifest sets `runOnStartup: true`.  Copy the complete `WavegoExport`
directory to Fusion's `API/AddIns` directory and restart Fusion once.
