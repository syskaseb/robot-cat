"""Audit supplier STEP solids and candidate fit. No generated print geometry."""
from pathlib import Path
import json, hashlib, sys, xml.etree.ElementTree as ET
import FreeCAD as A
import Part
from probe26 import bbox

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v26'
SOURCE=ROOT/'hardware/skorupa/v25/Kot_v25_DOMOWA_OSLONA.FCStd'

def main():
    path=ROOT/'hardware/reference/waveshare-bus-servo-adapter-a/Bus Servo Adapter (A).step'
    s=Part.Shape();s.read(str(path))
    rows=[{'index':i,'valid':t.isValid(),'bbox':bbox(t),'volume':t.Volume} for i,t in enumerate(s.Solids)]
    print('Supplier solids audited',len(rows),flush=True)
    report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'solids':rows,'fit_samples':[]}
    def save():
        (OUT/'supplier-fit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    save()
    cache=OUT/'shape-cache'
    index=json.loads((cache/'index.json').read_text(encoding='utf-8'))
    assert index['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert len(index['objects'])==238
    shapes={}
    for n in index['objects']:
        if n=='BusAdapter':continue
        shape=Part.Shape();shape.read(str(cache/(n+'.brep')));shapes[n]=shape
    print('Cached source shapes read',len(shapes),flush=True)
    shifts=[] if '--metadata-only' in sys.argv else [(-61,-3,49.6),(-61,-3,51),(-60,-3,51)]
    # Compute translated bounds from previously audited local bounds. Asking
    # OCC to bound the translated vendor BSplines can take several minutes.
    local_bounds=json.loads((OUT/'supplier-service-probe.json').read_text(encoding='utf-8'))['supplier_step']['bounds']
    for shift in shifts:
        moved=s.copy();moved.Placement=A.Placement(A.Vector(*shift),A.Rotation())*s.Placement
        bb=[v+shift[i//2] for i,v in enumerate(local_bounds)]
        envelope=Part.makeBox(bb[1]-bb[0],bb[3]-bb[2],bb[5]-bb[4],A.Vector(bb[0],bb[2],bb[4]))
        hits=[]
        for n,t in shapes.items():
            if not envelope.BoundBox.intersect(t.BoundBox):continue
            print('Envelope',shift,n,flush=True)
            envelope_overlap=envelope.common(t).Volume
            if envelope_overlap<=.001:continue
            # Invalid vendor microgeometry is never used for trusted booleans.
            # For it, use a conservative axis-aligned solid envelope instead.
            vv=0.;conservative=False
            for i,solid in enumerate(moved.Solids):
                sb=[v+shift[j//2] for j,v in enumerate(rows[i]['bbox'])]
                solid_box=A.BoundBox(sb[0],sb[2],sb[4],sb[1],sb[3],sb[5])
                if not solid_box.intersect(t.BoundBox):continue
                check=solid
                if not rows[i]['valid']:
                    b=solid_box
                    check=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin));conservative=True
                vv+=check.common(t).Volume
            if vv>.001:hits.append({'part':n,'volume_mm3':vv,'includes_invalid_solid_envelopes':conservative})
        report['fit_samples'].append({'translation':shift,'bbox':bb,'hits':hits})
        save()
        print('Fit',shift,hits,flush=True)
    pcb=s.Solids[0]
    holes=[]
    for f in pcb.Faces:
        if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.25)<1e-5:
            holes.append(list(f.Surface.Center))
    report['pcb_mount_holes_step_mm']=holes
    board=ET.parse(ROOT/'hardware/reference/grove-pca9685/16-Channel PWM Driver(PCA9685).brd').getroot()
    template=board.find(".//library[@name='twig_template1']/packages/package[@name='U2*3N']")
    # U$1 is R180: coordinates below are in the board's actual world frame.
    report['grove_mount_holes_mm']=[{'x':-float(h.get('x')),'y':-float(h.get('y')),'diameter':float(h.get('drill'))} for h in template.findall('hole')]
    report['grove_outline_extents_mm']=[-32.1,32.1,-22.1,22.1]
    report['grove_height_mm']=18
    report['fit_status']='not_run' if not shifts else 'completed_sampled_test'
    report['scope']='Supplier STEP is partly invalid; keep reference, not printable CAD. Fit excludes cable plugs and physical fasteners. Grove outline includes mounting tabs.'
    (OUT/'supplier-fit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    pcb.exportBrep(str(OUT/'adapter-pcb.brep'))
    print('Saved supplier-fit.json',flush=True)

if __name__=='__main__':main()
