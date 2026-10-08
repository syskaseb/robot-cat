"""One native four-MTA mount set from ab267e2 shared preflight.

Preserve previous modules; integrate front seats in source platform and rear
seats in existing paired rails. No extra rear screws or moved bought casings.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time
import FreeCAD as A
import Part
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect,circle
from open_prototype_common_source_platform import MODEL as SOURCES
from open_prototype_shared_distribution_carriers import MODEL as RAILS,planned_shapes,validate
from open_prototype_fhac_supports import ring
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint';MODEL=OUT/'CommonMtaMounts.FCStd';PROOF=OUT/'common-mta-mount-checks.json'


def main():
    assert not MODEL.exists() and not PROOF.exists(),'Receive existing native MTA worker before rebuilding'
    tick=time.monotonic();plan=read(OUT/'common-mta-support-plan.json')
    assert plan['status']=='COMMON4MTA_LOAD_PATH_PREFLIGHT_CLEAR_NATIVE_AND8TAILS_OPEN'
    for n,v in plan['source_sha256'].items():assert sha(ROOT/n)==v,n
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (SOURCES,RAILS,MOUNTS,CONTEXT,OUT/'common-mta-support-plan.json',OUT/'shared-allocation-plan.json',Path(__file__))}
    doc=A.openDocument(str(SOURCES));rail=A.openDocument(str(RAILS));mount=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT))
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,source_sha256=pins,
        contacts=[],errors=[],outside_torso=[],tested_pairs=0,
        source_case_and_route_allocation_preserved='337b6c6',source_platform_base='57afce2',
        new_hardware_candidate={'rear_M3x10':0,'rear_washers':0,'rear_nuts':0,'body_T18I':8},
        load_path='Front source floor; rear paired rail integral overhead roots,retained rail bolt stack; not low posts through S1 tool',
        assembly=plan['assembly'],remaining=['All8fullMTA leads/extensions/joints/restraints and stock','Actual delivered factory lead/L140/body/ATO motion','Whole fanouts/head/tail/S1/PWM/body/legs/service'],
        physical_gates=['PETG column/bridge/cantilever/creep/profile/support removal','T18I delivered fit/casing no-crush/locking and pull'],
        nominal_strip_or_factory_lengths_are_NOT_manufacturer_guarantee=True)
    try:
        source=doc.CommonSourcePlatform;old={source.Name:source.Shape.copy()}
        sides=[]
        for name in ('LeftDistributionCarrier','RightDistributionCarrier'):
            b=doc.copyObject(rail.getObject(name),True);doc.recompute()
            assert abs(b.Shape.Volume-rail.getObject(name).Shape.Volume)<1e-6
            sides.append(b);old[b.Name]=b.Shape.copy()
        p=doc.addObject('App::VarSet','MTAParameters');p.addProperty('App::PropertyLength','RearPostDiameter');p.RearPostDiameter=8
        def pad(body,name,z,loops,height):
            sk=sketch(body,name+'Plan',z)
            for q in loops:rect(sk,*q)
            body.Tip=feature(body,'Pad',name,sk,height)
        pad(source,'FrontMtaFeet',113,[(x-3,y,6,8) for x in (-29,-1) for y in (-33.5,25.5)],2)
        sk=sketch(source,'FrontMtaPostPlan',115)
        for x in (-29,-1):
            for y in (-30.5,30.5):circle(sk,x,y,6)
        source.Tip=feature(source,'Pad','FrontMtaPosts',sk,15.6)
        pad(source,'FrontMtaSeats',130.6,[(-32.5,y,35,22) for y in (-51.5,29.5)],2)
        for b,y in zip(sides,(18,-18)):
            sk=sketch(b,b.Name+'MtaRootPlan',109.01);rect(sk,126,y-4,12,8)
            sk.setExpression('Constraints[1]',f'{y} mm - MTAParameters.RearPostDiameter/2')
            sk.setExpression('Constraints[3]','MTAParameters.RearPostDiameter')
            b.Tip=feature(b,'Pad',b.Name+'MtaRoot',sk,4)
            sk=sketch(b,b.Name+'MtaPostPlan',113.01);circle(sk,134,y,8)
            sk.setExpression('Constraints[2]','MTAParameters.RearPostDiameter')
            b.Tip=feature(b,'Pad',b.Name+'MtaPost',sk,23.99)
            pad(b,b.Name+'MtaSeat',137,[(102.5,7 if y>0 else -29,37,22)],2)
        bodies=[doc.UpperCarrier,source]+sides
        baseline=validate(doc,bodies)
        p.RearPostDiameter=9;trial=validate(doc,bodies)
        assert all(trial[b.Name]>baseline[b.Name] for b in sides)
        p.RearPostDiameter=8;restored=validate(doc,bodies)
        assert all(abs(v-restored[n])<1e-6 for n,v in baseline.items())
        r['parameter_test']=dict(rear_post_diameter_mm=[8,9,8],matching_integral_root_width_follows=True,restored=True)
        allocation=read(OUT/'shared-allocation-plan.json');targets=planned_shapes(allocation,mount,ctx)
        ties={}
        for name,cx,cy,z in [('FL',-15,40.5,132.6),('FR',-15,-40.5,132.6),('RL',120,18,139),('RR',120,-18,139)]:
            sign=1 if cy>0 else -1
            for i,x in enumerate((cx-8,cx+8)):
                box=[x-1.25,cy-12.2,z-3.2,x+1.25,cy+12.2,z+17.2]
                head=[x-2.25,cy+11,z-5.5,x+2.25,cy+15.8,z-2]
                if sign<0:head[1],head[4]=cy-15.8,cy-11
                ob=doc.addObject('Part::Feature',name+'MtaBodyTie'+str(i));ob.Shape=ring(A,Part,0,2.5,box,head);ties[ob.Name]=ob.Shape
            ob=doc.addObject('Part::Feature','MTA_'+name+'_CP2');ob.Shape=targets['MTA_'+name+'_CP2'].copy()
            ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Frozen nominal case budget; supplier body/leads/delivered fit remain gates'
        doc.recompute();validate(doc,bodies);doc.saveAs(str(MODEL))
        print('SAVED native4MTA seats/8bodystraps; checking ONLY added material and straps',flush=True)
        added={}
        for b in [source]+sides:
            additions=b.Shape.cut(old[b.Name]);removed=old[b.Name].cut(b.Shape)
            assert additions.isValid() and removed.isValid() and removed.Volume<1e-6,b.Name
            added[b.Name+'/added']=additions
        current={b.Name:b.Shape for b in bodies}
        current.update({o.Name:o.Shape for o in doc.Objects if o.TypeId=='Part::Feature' and not o.Shape.isNull()})
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name in ('UpperCarrier','BUS_CP2'):continue
            if o.Name.startswith(('SourceLeftCarrier','SourceRightCarrier','SideRail','SideColumn','SideDistributionRail','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_')) or o.Name.endswith('_CurrentReference'):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier'):targets[o.Name]=o.Shape
        for group in mount.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name and group.Name!='SideMountHardware':
                for o in group.Group:
                    if 'Shape' in o.PropertiesList and not o.Shape.isNull():targets['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets[o.Name]=o.Shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            r['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        new={**added,**ties};done=set()
        for n,s in new.items():
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():check(n,s,m,t)
            for m,t in current.items():
                if n==m or (n.endswith('/added') and m==n.split('/')[0]):continue
                key=tuple(sorted((n,m)))
                if key in done:continue
                done.add(key);check(n,s,m,t)
        r['native_geometry']=dict(valid_bodies=4,strict_bop_errors=0,fully_constrained_sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in doc.Objects),volumes_mm3=baseline)
        r['print_dimensions_mm']={b.Name:[b.Shape.BoundBox.XLength,b.Shape.BoundBox.YLength,b.Shape.BoundBox.ZLength] for b in bodies}
        assert all(max(q)<246 for q in r['print_dimensions_mm'].values())
        r['model_sha256']=sha(MODEL)
        r['status']='NATIVE_COMMON4MTA_MOUNTS_STATIC_CLEAR_FULL8TAILS_OPEN' if not any(r[k] for k in ('contacts','errors','outside_torso')) else 'NATIVE_COMMON4MTA_CHANGED_INTERFACES_REQUIRE_CAUSE_CHANGE'
    except Exception as e:
        r['status']='NATIVE_MTA_BUILD_OR_GATE_ERROR';r['errors'].append(dict(error=repr(e)))
        if not MODEL.exists():doc.saveAs(str(MODEL));r['partial_native_preserved']=True
        raise
    finally:
        for d in (doc,rail,mount,ctx):
            if d.Name in A.listDocuments():A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','outside_torso','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
