"""One-shot Autodesk Fusion add-in: export WAVEGO for the FreeCAD workflow.

The add-in is deliberately read-only with respect to the design.  It exports
the first occurrence whose name or component name contains ``WAVEGO`` and
writes a machine-readable inventory beside the neutral CAD files.
"""

import json
import os
import traceback

import adsk.core
import adsk.fusion


OUT_DIR = r"C:\Users\Sysq\PycharmProjects\robot-cat\hardware\wavego\source"
LOG_FILE = os.path.join(OUT_DIR, "fusion-export.log")
BACKUP_ARCHIVE = os.path.join(OUT_DIR, "robot-cat-backup.f3d")
_handlers = []


def _log(message):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as stream:
        stream.write(str(message) + "\n")


def _bbox(box):
    if box is None:
        return None
    lo, hi = box.minPoint, box.maxPoint
    # Fusion's API works in centimetres.  Store millimetres for FreeCAD.
    return {
        "min_mm": [10 * lo.x, 10 * lo.y, 10 * lo.z],
        "max_mm": [10 * hi.x, 10 * hi.y, 10 * hi.z],
        "size_mm": [10 * (hi.x - lo.x), 10 * (hi.y - lo.y),
                    10 * (hi.z - lo.z)],
    }


def _component_record(component):
    bodies = []
    for body in component.bRepBodies:
        bodies.append({
            "name": body.name,
            "visible": body.isVisible,
            "bbox": _bbox(body.boundingBox),
        })
    return {
        "name": component.name,
        "part_number": component.partNumber,
        "body_count": component.bRepBodies.count,
        "occurrence_count": component.occurrences.count,
        "bodies": bodies,
    }


def _occurrence_record(occurrence):
    children = [_occurrence_record(child)
                for child in occurrence.childOccurrences]
    return {
        "name": occurrence.name,
        "component": occurrence.component.name,
        "visible": occurrence.isLightBulbOn,
        "bbox": _bbox(occurrence.boundingBox),
        "transform_cm": list(occurrence.transform.asArray()),
        "children": children,
    }


def _find_wavego(root):
    queue = list(root.occurrences)
    while queue:
        occurrence = queue.pop(0)
        haystack = (occurrence.name + " " + occurrence.component.name).lower()
        if "wavego" in haystack:
            return occurrence
        queue.extend(list(occurrence.childOccurrences))
    return None


def _export(_context=None):
    imported_document = None
    try:
        app = adsk.core.Application.get()
        if not os.path.isfile(BACKUP_ARCHIVE):
            raise RuntimeError("missing backup archive: " + BACKUP_ARCHIVE)

        # Import the untouched local backup into a temporary document.  Do not
        # activate, save or query robot-cat-lokiec-work: that is the user's
        # live edit and is intentionally outside this export path.
        import_manager = app.importManager
        import_options = import_manager.createFusionArchiveImportOptions(
            BACKUP_ARCHIVE
        )
        imported_document = import_manager.importToNewDocument(import_options)
        if imported_document is None:
            raise RuntimeError("Fusion could not open the backup F3D")
        imported_document.activate()
        target_document = imported_document
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            raise RuntimeError("active Fusion product is not a Design")

        wavego_occurrence = _find_wavego(design.rootComponent)
        if wavego_occurrence is None:
            raise RuntimeError(
                "no occurrence containing 'WAVEGO' in document "
                + target_document.name
            )
        wavego = wavego_occurrence.component

        os.makedirs(OUT_DIR, exist_ok=True)
        step_path = os.path.join(OUT_DIR, "WAVEGO_PRO_BETA_v3.step")
        f3d_path = os.path.join(OUT_DIR, "WAVEGO_PRO_BETA_v3.f3d")
        inventory_path = os.path.join(OUT_DIR, "WAVEGO_PRO_BETA_v3.json")
        preview_path = os.path.join(OUT_DIR, "WAVEGO_PRO_BETA_v3.png")

        export_manager = design.exportManager
        step_options = export_manager.createSTEPExportOptions(step_path, wavego)
        if step_options is None or not export_manager.execute(step_options):
            raise RuntimeError("Fusion STEP export failed")

        archive_options = export_manager.createFusionArchiveExportOptions(
            f3d_path, wavego
        )
        if archive_options is None or not export_manager.execute(archive_options):
            raise RuntimeError("Fusion F3D component export failed")

        inventory = {
            "source_document": target_document.name,
            "source_was_saved": target_document.isSaved,
            "exported_occurrence": wavego_occurrence.name,
            "exported_component": wavego.name,
            "component_count": design.allComponents.count,
            "component": _component_record(wavego),
            "tree": _occurrence_record(wavego_occurrence),
            "files": {
                "step": step_path,
                "f3d": f3d_path,
                "preview": preview_path,
            },
        }
        with open(inventory_path, "w", encoding="utf-8") as stream:
            json.dump(inventory, stream, ensure_ascii=False, indent=2)

        app.activeViewport.fit()
        app.activeViewport.saveAsImageFile(preview_path, 1600, 1200)
        _log("OK: exported " + wavego.name)
        _log(step_path)
        _log(f3d_path)
    except Exception:
        _log("ERROR\n" + traceback.format_exc())
    finally:
        # The document came from a local archive and is only a transient
        # conversion workspace.  Closing without saving cannot affect either
        # the cloud backup or the actively edited project.
        if imported_document is not None:
            imported_document.close(False)


def stop(_context):
    app = adsk.core.Application.get()
    for handler in _handlers:
        try:
            app.startupCompleted.remove(handler)
        except Exception:
            pass
    _handlers.clear()


class _StartupHandler(adsk.core.ApplicationEventHandler):
    def notify(self, args):
        _export(args)


def run(_context):
    app = adsk.core.Application.get()
    if app.isStartupComplete:
        _export(_context)
        return

    # A run-on-startup add-in is loaded before Fusion has finished creating
    # the design environment.  Importing an F3D at that moment is racy, so
    # defer the one-shot conversion to the documented startupCompleted event.
    handler = _StartupHandler()
    app.startupCompleted.add(handler)
    _handlers.append(handler)
