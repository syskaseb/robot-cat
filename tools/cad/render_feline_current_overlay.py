"""Render current ordered CAD planning overlays, not a selected finished cat.

No stale full-harness curves, artificial filled skin, or rejected R1/R2 bays.
Every mesh triangle is retained. The blue outline is a reservation only.
"""
import json
import time
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from feline_current_scene import load
from build_feline_layout_envelope import STATIONS, NECK_STATIONS, section_coefficients
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT, sha


def color(name, row):
    role = row.get('role', '')
    if role == 'HeadMechanism':
        return [.38, .41, .44]
    if role.startswith('leg:') or role in ('P0_or_battery', 'TailMechanicalCore', 'BellyFeet'):
        return [.54, .58, .62]
    if role.startswith('Bank') or name.startswith(('Factory:', 'BankFullPrefix:')):
        return [.85, .47, .14]
    if role.startswith('WAGO'):
        return [.76, .77, .75]
    if role in ('Pi4', 'PWM9685', 'PWM1608_U1', 'AUX4092', 'BUS'):
        return [.23, .47, .35]
    if 'StructureReserve' in name or row.get('kind') in ('planning_reservation', 'project_mating_reservation'):
        return [.27, .48, .65]
    if 'Wire' in name or 'wire' in name or 'Prefix' in name:
        return [.82, .43, .15]
    return [.53, .57, .61]


def outlines():
    sections = []
    for x, width, height in STATIONS:
        y, z = section_coefficients(width, height)
        sections.append(np.column_stack((np.full(len(y), x), y*width/2, 32+z*height/2)))
    for x, width, low, high in NECK_STATIONS:
        y, z = section_coefficients(width, high-low)
        sections.append(np.column_stack((np.full(len(y), x), y*width/2, (low+high)/2+z*(high-low)/2)))
    return sections


def main():
    tick = time.monotonic()
    scene, meta, templates, data, pins, changes = load()
    assert not changes, 'Do not display rejected case relocations'
    triangles, colors = [], []
    light = np.array([-.3, -.5, 1.]); light /= np.linalg.norm(light)
    for i, (name, shape) in enumerate(scene.items()):
        points, faces = shape.tessellate(.7)
        if not faces:
            continue
        tri = np.asarray([list(v) for v in points])[np.asarray(faces)]
        normal = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
        normal /= np.maximum(np.linalg.norm(normal, axis=1), 1e-12)[:, None]
        shade = .55+.45*np.abs(normal@light)
        triangles.append(tri)
        colors.append(shade[:,None]*np.array(color(name, meta[name]))[None,:])
        if i % 200 == 0:
            print('Rendered source meshes', i, flush=True)
    tri = np.concatenate(triangles); rgb = np.concatenate(colors)
    eye = np.array([-4., -6., 3.]); eye /= np.linalg.norm(eye)
    right = np.cross(eye, [0,0,1]); right /= np.linalg.norm(right)
    up = np.array([0.,0.,1.])-eye*eye[2]; up /= np.linalg.norm(up)
    views = [('iso', np.column_stack((right,up,eye)), 'Bieżący plan CAD — widok ogólny'),
             ('front', np.array([[0,0,-1],[1,0,0],[0,1,0]]), 'Bieżący plan CAD — przód')]
    images = []
    for suffix, basis, title in views:
        projected = tri@basis; order = np.argsort(projected[:,:,2].mean(1))
        fig, ax = plt.subplots(figsize=(12,10), dpi=140)
        ax.add_collection(PolyCollection(projected[order,:,:2], facecolors=rgb[order],
            edgecolors='none', rasterized=True))
        for s in outlines():
            q = np.vstack((s, s[0]))@basis
            ax.plot(q[:,0],q[:,1], color='#1680b3', lw=.65, alpha=.65)
        ax.autoscale_view(); ax.set_aspect('equal'); ax.margins(.05); ax.axis('off')
        fig.suptitle(title+' | 18.10.2026', fontsize=17)
        fig.text(.5,.062,'NIE WYBRANY UKŁAD • nowy zakres 0/10 • nie jest gotową obudową',ha='center',fontsize=11)
        fig.text(.5,.038,'Niebieskie kontury: rezerwacja tułowia/szyi, NIE ścianki. Pokazano tylko istniejącą geometrię i częściowe przewody.',ha='center',fontsize=9)
        fig.text(.5,.018,'Poza alokacją: 3 FHAC, F_PWM, monitor. Pełne złącza Pi, lokalna elektryka ogona i nowy wspornik szyi nadal OPEN.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.08,1,.95))
        target = OUT/('current-overlay-20261018-'+suffix+'.png')
        fig.savefig(target, facecolor='white'); plt.close(fig)
        images.append(dict(path=target.relative_to(ROOT).as_posix(), sha256=sha(target)))
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    receipt = dict(status='CURRENT_ORDERED_CAD_OVERLAY_NOT_SELECTED_ASSEMBLY',
        selected=False, N01_complete=False, physical_pass=False,
        current_scene_shapes=len(scene), mesh_shapes=len(triangles), triangles=len(tri),
        unplaced_templates=sorted(templates), old_rejected_R1_R2_pose_changes_used=False,
        full_harness_or_full_selected_inventory_claimed=False, blue_outline_is_not_material=True,
        source_sha256=pins, images=images, worker_seconds=round(time.monotonic()-tick,3),
        recorded_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'current-overlay-20261018.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('status','current_scene_shapes','triangles','worker_seconds')}),flush=True)


if __name__ == '__main__':
    from pathlib import Path
    main()
