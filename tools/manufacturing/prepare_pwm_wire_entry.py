"""Pin the terminal preparation and current underside constraints for T252.

No invented cavity coordinates or complete-route approval.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/fuse-layout-repair-r1'
REF=ROOT/'hardware/reference/power-distribution-2026-09-23'
BAT=ROOT/'hardware/cad/studies/battery-p0/current-cassette-service-r1/checks.json'


def main():
    old=json.loads(BAT.read_text())
    for path,digest in old['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    battery=next(r['swept_bbox_mm'] for r in old['pairs'] if r['moving']=='tray_pack_R2_envelope')
    plan=json.loads((OUT/'plan.json').read_text())
    gaps={name:r['bbox'][2]-battery[5] for name,r in plan['replacements'].items()}
    assert all(g>0 for g in gaps.values())
    sources=[BAT,OUT/'plan.json',REF/'WAGO-221-615.pdf',REF/'WAGO-221-615-page-1.png',REF/'WAGO-221-615-page-2.png',Path(__file__)]
    report={
        'status':'TERMINATION_DEFINED_ROUTE_NOT_COMPLETE',
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'wago':{'sku':'221-615','terminal_count':5,'potential_count':1,
                'manufacturer_stranded_copper_mm2':[0.5,6],
                'strip_mm':[12,14],'side_entry':True,
                'width_depth_height_mm':[36.7,21.1,10.1],
                'evidence':'Existing manufacturer PDF dated30Jun2022, pages1/2 visually read again. No cavity pitch/centre inferred from photo.'},
        'xp01_termination':{
            'wire':'Selected0.5mm2 copper stranded XP01, no change of wire family',
            'terminal':'One directly inserted stripped conductor in one WAGO lever cage; no new lug or ferrule added to BOM',
            'preparation':'Disconnect all supplies. Strip12-14mm without strand damage, open lever, insert all strands fully, close lever. No exposed copper outside housing; inspect and pull-check after assembly. Do not insert the fuse lead directly in WAGO or put two wires in one cage.',
            'logical_port':'P_REAR.4, same common potential as all five cavities',
            'physical_cavity':'Choose nearest available physical cage only after preserving P0 assignments; physical cage number is not established by the old logical label',
            'orientation_design_decision':'Width along worldX, lever up, wire openings toward world-Y. This is chosen installation orientation, not proof from an existing imported WAGO solid.',
            'unfused_budget':'Conservatively budget<=50mm for conductor from clamped end to fuse body including inserted copper, exit bend, soldered joint and bare fuse lead before body; no generic30mm service slack.'},
        'battery_saved_rigid_envelope':battery,
        'continuous_vertical_separation_to_battery_mm':gaps,
        'battery_scope':'Existing enlarged battery+tray downward envelope only. NOT all chassis, retainers, straps, electrical leads or full underside clearance.',
        'missing_geometric_interface':'P_REAR is above DeckZ109, fused pigtail belowZ105. The new eight4x2 tie slots are occupied by ties and are NOT a qualified wire feedthrough. Add one separate edge-protected passage/route before selecting this Deck.',
        'next_step':'Use the saved working Deck, resolve one dedicated wire passage and radiused path from the chosen near cage to pigtail; include installed insertion length and fuse lead in50mm, then inspect chassis and complete underside contents. Do not stretch cable through an occupied tie slot.',
        'new_stl_count':0,'route_qualified':False,'physical_pass':False,'energize_approved':False,
    }
    (OUT/'wire-entry.json').write_text(json.dumps(report,indent=2)+'\n')
    manifest={'status':'EVIDENCE_ONLY_NOT_ROUTE_APPROVAL','new_stl_count':0,
              'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources+[OUT/'wire-entry.json']]}
    (OUT/'wire-entry-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'battery_only_gaps_mm':gaps,'source_files':len(manifest['files']),'route_qualified':False}))


if __name__=='__main__':main()
