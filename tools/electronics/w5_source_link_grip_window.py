"""Replace an impossible external back band by a supported rear window.

The whole station allocation proves that moving the external band along X
cannot clear all eight stages. Put its back segment inside the existing jaw
envelope, with two real side webs, instead. No P0 notch or wire movement.
"""
from pathlib import Path
import json
import w5_source_link_grips as L
from servo_fuse_inputs_r1 import save,sha
ROOT=L.ROOT;BASE=L.BASE;OUT=BASE/'w5-source-link-grips-r2'
ALLOCATION=BASE/'w5-source-link-band-space-r1/plan.json'
ORIGINAL_OUT=L.OUT;original_proposed=L.proposed


def proposed(A,Part):
    parts,spec=original_proposed(A,Part)
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    axis=-3.65;xmin,xmax=-7.5,-1.3
    additions=[]
    for name in ('TopJaw','BottomJaw','BackJaw'):
        b=spec['root_boxes_mm'][name]
        left=list(b);left[0],left[3]=xmin,b[0]
        right=list(b);right[0],right[3]=b[3],xmax
        additions += [box(left),box(right)]
        b[0],b[3]=xmin,xmax
    zi=spec['root_boxes_mm']['TopJaw'][2];zo=spec['root_boxes_mm']['TopJaw'][5]
    back=7.62602791928+.2
    slot=[axis-1.45,back-.2,-zo-.2,axis+1.45,9.62602791928,zo+.2]
    parts['Clip']=parts['Clip'].multiFuse(additions).cut(box(slot))
    assert parts['Clip'].isValid() and len(parts['Clip'].Solids)==1
    ymin=-29.9;ymax=back+1.2
    body_boxes=[[axis-1.25,ymin,zo,axis+1.25,ymax,zo+1.2],
        [axis-1.25,ymin,-zo-1.2,axis+1.25,ymax,-zo],
        [axis-1.25,ymin-1.2,-zo,axis+1.25,ymin,zo],
        [axis-1.25,back,-zo,axis+1.25,ymax,zo]]
    head=[axis-2.25,-12.4,zo+.6,axis+2.25,-7.6,zo+4.5]
    parts.update(BodyBand=Part.makeCompound([box(b) for b in body_boxes]),BodyHead=box(head))
    spec.update(body_band_boxes_mm=body_boxes,body_head_box_mm=head,
        body_band_axis_x_PCB_mm=axis,back_band_window_mm=slot,
        back_web_widths_mm=[slot[0]-xmin,xmax-slot[3]],
        front_band_to_offset_stem_gap_mm=axis-1.25-(-5),
        nominal_rectangular_body_band_perimeter_mm=2*(ymax-ymin+2*zo),
        body_aperture_diagonal_mm=((ymax-ymin)**2+(2*zo)**2)**.5,
        coupled_change_reason='External back band has no shared free station. A full rear window and widened jaws put the strap within the already clear root envelope. Axis solves >=0.1mm stem gap and >=0.9mm right web simultaneously.',
        geometry_only_not_load_strength_pass=True)
    assert min(spec['back_web_widths_mm'])>.899999
    return parts,spec


def main():
    plan=json.loads(ALLOCATION.read_text(encoding='utf-8'))
    assert plan['status']=='LINK_BAND_ALLOCATION_BLOCKED' and not plan['errors']
    assert plan['minimum_root_extension_x_mm']<-7.5
    L.OUT=OUT;L.proposed=proposed;L.main()
    p=OUT/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
    for src in (Path(__file__),ALLOCATION,ORIGINAL_OUT/'checks.json',ORIGINAL_OUT/'blueprint.json'):
        proof['source_sha256'][src.relative_to(ROOT).as_posix()]=sha(src)
    proof.update(status='EIGHT_LINK_WINDOW_GRIPS_REJECTED' if proof['hits'] or proof['errors'] else 'EIGHT_LINK_WINDOW_GRIPS_P0_STATIC_CLEAR_HARNESS_PENDING',
        band_window_clearance_not_strength_qualification=True)
    save(p,proof)


if __name__=='__main__':main()
