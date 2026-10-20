"""One5-grip/3-body prototype restraint layout, before nativeN03 detail.

All wires keep existing geometry. Five independent T18I,3case-only selected
4905 patches. Low roots go to the current rear floor, upper roots to the
positive foundation. No borrowed cavity, new hole or guessed U1 pad.
"""
import hashlib,json,zipfile
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_saddles import build as saddle,segment
from receive_feline_global_case_candidates import placement


def box(lo,hi):return Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))


def joined(items):
    s=items[0].multiFuse(items[1:]) if len(items)>1 else items[0]
    assert s.isValid() and len(s.Solids)==1
    return s


def source():
    sf=OUT/'n01-F0-access-stack.json';r=json.loads(sf.read_text());assert not r['failures']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    mf=OUT/'n01-F0-access-stack-motion.json';motion=json.loads(mf.read_text())
    assert motion['status']=='ACCESS_STACK_SEVEN_ACTORS36MOTION_RECEIVED_FULL_RESTRAINTS_AND_SHARED123_OPEN' and not motion['failures']
    assert motion['source_sha256'][sf.relative_to(ROOT).as_posix()]==sha(sf)
    assert sha(ROOT/r['bundle'])==r['bundle_sha256'];actors={}
    with zipfile.ZipFile(ROOT/r['bundle']) as z:
        for n,row in r['geometry'].items():
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[n]=s
    return actors,r,sf,mf


def construct(revision='r1'):
    assert revision in ('r1','r2')
    base,r,sf,mf=source();new={};meta={};groups={'lower':[],'upper':[]};proof={};specs={}
    add=lambda n,s,kind,group: (new.__setitem__(n,s),meta.__setitem__(n,dict(kind=kind,print_group=group)),groups[group].append(n) if kind=='PETG' else None)
    rr=r['recipes'];u=A.Vector(2**-.5,2**-.5,0);b=A.Vector(-u.y,u.x,0)
    configurations=(('W075','W075_factory',rr['W075_factory']['parts'][0],3.,[0,0,-1],7.5,'lower',3.1),
        ('GROUND','W001_ground_prefix',rr['W001_ground_prefix']['parts'][0],3.,[0,0,-1],9.,'lower',4.),
        ('F0OUT','W076_factory',rr['W076_factory']['parts'][0],.3,[0,0,-1],7.,'lower',3. if revision=='r2' else 1.5),
        ('POSTIN','W076_factory',rr['W076_factory']['parts'][-1],1.25,[1,0,0] if revision=='r2' else [0,1,0],5.75,'upper',None),
        ('POSTOUT','W076_custom_prefix',rr['W076_custom_prefix']['parts'][0],3.,[-.5,3**.5/2,0],9.,'upper',None))
    for key,wire,row,start,side,band_at,group,foot_at in configurations:
        kit,rec=saddle(row,start,side,band_at)
        for suffix,s in kit.items():add('SourceGrip:'+key+':'+suffix,s,'PETG' if suffix=='pad' else 'T18I',group)
        if group=='lower':
            e=segment(row);p=e.valueAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*foot_at/e.Length)
            root=box([p.x-1,p.y-1,-43.3],[p.x+1,p.y+1,p.z-3.])
            add('SourceGrip:'+key+':root',root,'PETG',group)
            overlap=root.common(kit['pad']);assert overlap.isValid() and overlap.Volume>1e-5,(key,'No root-to-full-pad material')
            rec['root_pad_common_mm3']=overlap.Volume
        specs[key]=dict(rec,wire=wire,side=side,print_group=group)
    # F0 opposite the side-access face. Root goes BEYOND the MTA case and
    # its first source arc, at u30/b16 instead of blindly below the case.
    # Lead GUIDE midpoints carry a few micrometres of imported rounding.
    # Bond lands come from the real planar case, never from that midpoint.
    case=base['Ref_Material_F0_CP2_0_0'];assert len(case.Solids)==1
    centre=case.Solids[0].CenterOfMass
    frame=placement(np.column_stack((list(u),list(b),[0,0,1])),list(centre))
    def local(lo,hi):s=box(lo,hi);s.Placement=frame*s.Placement;return s
    patch=local([-9,11,-4],[9,11.5,4]);spine=joined([local([-10,11.5,-4],[31,13.5,4]),local([28,11.5,-4],[31,16.5,4])])
    foot=frame.multVec(A.Vector(30,16,0));root=box([foot.x-1,foot.y-1,-43.3],[foot.x+1,foot.y+1,centre.z-3])
    spine=joined([spine,root]);add('SourceBody:F0:spine',spine,'PETG','lower');add('SourceBody:F0:patch',patch,'VHB4905','lower')
    proof['F0']=dict(case='Ref_Material_F0_CP2_0_0',patch='SourceBody:F0:patch',spine='SourceBody:F0:spine',
        case_coupon=local([-9,10.99,-4],[9,11,4]),print_coupon=local([-9,11.5,-4],[9,11.51,4]))
    # Entire mated connector casing on its own selected case-only patch.
    case=base['Ref_Material_XT60_CP2_0_0'];assert len(case.Solids)==1
    c=case.Solids[0].CenterOfMass;low=case.BoundBox.ZMin
    frameXT=placement(np.column_stack((list(u),list(b),[0,0,1])),[c.x,c.y,0])
    def xt(lo,hi):s=box(lo,hi);s.Placement=frameXT*s.Placement;return s
    patch=xt([-9,-4,low-.5],[9,4,low]);bed=xt([-9,-4,low-2.5],[9,4,low-.5])
    foot=frameXT.multVec(A.Vector(7,2,0));root=box([foot.x-1,foot.y-1,-43.3],[foot.x+1,foot.y+1,low-1.5])
    bed=joined([bed,root]);add('SourceBody:XT60:bed',bed,'PETG','lower');add('SourceBody:XT60:patch',patch,'VHB4905','lower')
    proof['XT60']=dict(case='Ref_Material_XT60_CP2_0_0',patch='SourceBody:XT60:patch',spine='SourceBody:XT60:bed',
        case_coupon=xt([-9,-4,low],[9,4,low+.01]),print_coupon=xt([-9,-4,low-.51],[9,4,low-.5]))
    # Whole POST body opposite its lever side; positive foundation takes the
    # load. It is not an adhesive wire relief or pressure on an unknown pad.
    case=base['Ref_Material_PostF0Splice_CP2_0_0'];bb=case.BoundBox;x=bb.XMin;y=bb.Center.y;z=bb.ZMin
    patch=box([x-.5,y-4,z+.5],[x,y+4,z+18.5]);spine=box([x-2.5,y-4,z+.5],[x-.5,y+4,32.52])
    add('SourceBody:POST:spine',spine,'PETG','upper');add('SourceBody:POST:patch',patch,'VHB4905','upper')
    proof['POST']=dict(case='Ref_Material_PostF0Splice_CP2_0_0',patch='SourceBody:POST:patch',spine='SourceBody:POST:spine',
        case_coupon=box([x,y-4,z+.5],[x+.01,y+4,z+18.5]),print_coupon=box([x-.51,y-4,z+.5],[x-.5,y+4,z+18.5]))
    xf=r['current_nominal_datums']['POST1'][0];sx=x-1.5
    if revision=='r2':xf+=3.5
    arm=joined([box([xf-1,55.1 if revision=='r2' else 59.6,7.5],[xf+1,63,9.5]),box([sx-1,61,7.5],[xf+1,63,9.5]),
        box([sx-1,61,7.5],[sx+1,63,28.75]),box([sx-1,59.1,26.75],[sx+1,63,28.75])])
    add('SourceGrip:POSTIN:root',arm,'PETG','upper')
    add('SourceGrip:POSTOUT:root',box([x-2.5,58.5,5.75],[x-.5,60.5,12.75]),'PETG','upper')
    for key in ('POSTIN','POSTOUT'):
        root=new['SourceGrip:'+key+':root'];pad=new['SourceGrip:'+key+':pad'];overlap=root.common(pad)
        assert overlap.isValid() and overlap.Volume>1e-5,(key,'Missing full pad root',overlap.Volume)
        specs[key]['root_pad_common_mm3']=overlap.Volume
        assert root.common(spine).Volume>1e-5,(key,'Missing common POST spine')
    bonds={}
    for key,p in proof.items():
        case=base[p['case']];patch=new[p['patch']];sp=new[p['spine']]
        overlap=case.common(patch);assert overlap.isNull() or overlap.isValid();assert overlap.Volume<1e-5
        area=case.common(p['case_coupon']).Volume/.01;land=sp.common(p['print_coupon']).Volume/.01
        assert abs(area-144)<1e-3 and abs(land-144)<1e-3,(key,area,land)
        bonds[key]={k:v for k,v in p.items() if k not in ('case_coupon','print_coupon')}
        bonds[key].update(actual_nominal_case_land_mm2=area,actual_print_land_mm2=land,selected_patch_mm=[8,18,.5],
            actual_case_plastic_adhesion_peel_and_tightening_fit_phase2_gate=True,body_only_NOT_wire_relief=True)
    if revision=='r2':
        # Both floating feet lie in the same REAL floor cutout, not above
        # parent material. One bottom fork connects them to the witnessed
        # Floor boundary steps from x46 to x49.167 at y-36.6. The foot
        # extends to x52 across BOTH actual regions, not only their bbox.
        bridge=joined([box([32.387120903,-38.734195125,-43.3],[52.,-34.734195125,-41.3]),
                       box([37.01867032,-36.734195125,-43.3],[39.01867032,-28.981325364,-41.3])])
        add('SourceRoot:lowerSharedFork',bridge,'PETG','lower')
        import json
        from receive_feline_rrp_shared_height import load
        parent=load(json.loads((OUT/'n01-MTA-low-stop-cradles.json').read_text()))['LowerBay:RearPanel']
        for n in ('SourceGrip:W075:root','SourceBody:XT60:bed'):
            assert bridge.common(new[n]).Volume>1.,('Fork misses source foot',n)
        assert bridge.common(parent).Volume>10.,'Fork misses real parent material'
        assert new['SourceGrip:F0OUT:root'].distToShape(base['Ref_Material_F0_CP2_0_0'])[0]>=.2
    for n,s in new.items():assert s.isValid() and len(s.Solids)==1,n
    return base,new,meta,groups,specs,bonds,r,sf,mf
