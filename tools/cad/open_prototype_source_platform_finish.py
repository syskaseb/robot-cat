"""Receive4ab9057 native platform; qualify ONLY changed straps and service.

Whole geometry235pair evidence reused except all changed strap interfaces,
which are tested again. Fresh relocated native reopen and candidate exports.
"""
from datetime import datetime,timezone
from pathlib import Path
import copy,json,math,shutil,tempfile,time,subprocess,hashlib
import FreeCAD as A
import Part,Mesh,MeshPart
from open_prototype_common_source_platform import MODEL,PROOF,OUT,AXES
from open_prototype_shared_distribution_carriers import planned_shapes,MODEL as RAILS,validate
from open_prototype_fhac_supports import ring,TIE
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,read,sha


def main():
    tick=time.monotonic();dest=OUT/'common-source-platform-package.json'
    assert not dest.exists(),'Receive finish worker before repeat'
    prior=read(PROOF)
    assert prior['status']=='NATIVE_SOURCE_PLATFORM_HAS_CHANGED_INTERFACE_FAILURES'
    assert {(q['a'],q['b']) for q in prior['contacts']}=={('UpperCarrier','F_TY_OutputTie1')}
    assert not prior['errors'] and not prior['outside_torso']
    for path in (MODEL,PROOF):
        saved=subprocess.check_output(['git','show','4ab9057:'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
        assert hashlib.sha256(saved).hexdigest()==sha(path),'Preserve received result before finish'
    r=dict(schema_version=1,readiness='prototype',status='PENDING',selected=False,stage_completed=False,physical_pass=False,
        prior_geometry_snapshot_commit='4ab9057',prior_interface_pairs=235,prior_contact_rechecked_not_waived=prior['contacts'],
        contacts=[],errors=[],outside_torso=[],tested_pairs=0,changed_straps=[],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,RAILS,TIE,Path(__file__),ROOT/'tools/cad/open_prototype_common_source_platform.py',OUT/'shared-allocation-plan.json')},
        assembly=prior['assembly'],new_hardware_candidate=prior['new_hardware_candidate'],
        manufacturing=prior['manufacturing'],open_gates=prior['gates'],fixed_station_disposition=prior['fixed_station_disposition'])
    d=A.openDocument(str(MODEL));mount=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));rail=A.openDocument(str(RAILS))
    try:
        changed={}
        for i,(cx,y) in enumerate(((-47,44.5),(-7,49))):
            ob=d.getObject('NorthInputTie'+str(i))
            ob.Shape=ring(A,Part,1,2.5,[cx-21.2,y-1.25,111.8,cx+21.2,y+1.25,123.5],
                [cx-2.4,y-2.25,108.3,cx+2.4,y+2.25,112.8]);changed[ob.Name]=ob.Shape
        for name,x,sign in [('F_PI',-40,-1),('F_AUX',-15,-1),('F_HY',10,1),('F_HP',35,1),('F_TY',60,1)]:
            for i,z in enumerate((84.75,89.25)):
                box=[x-7.2,32.25,z-1.25,x+13.2,39.75,z+1.25]
                head=[x+3,38.55,z-2.25,x+7.8,42.05,z+2.25]
                if sign<0:
                    box[1],box[4]=-box[4],-box[1];head[1],head[4]=-head[4],-head[1]
                ob=d.getObject(name+'_OutputTie'+str(i));ob.Shape=ring(A,Part,2,2.5,box,head);changed[ob.Name]=ob.Shape
        d.recompute();r['changed_straps']=list(changed)
        tie=read(TIE);assert tie['length_mm']==145 and tie['head_length_mm']==4.8
        r['tie_length_screen']=[]
        for role,width,height,count in [('body',20.25,24,10),('north5port',40,9.3,2),('south5port',33,9.3,2),('output',18,5.1,10)]:
            required=2*(width+height)+25
            assert required<tie['length_mm'],role
            r['tie_length_screen'].append(dict(role=role,quantity=count,inner_rectangle_mm=[width,height],
                perimeter_plus_project_lock_tail25_mm=required,stock_length_mm=145,
                installed_curvature_lock_and_pull_test_open=True))
        assert sum(q['quantity'] for q in r['tie_length_screen'])==24
        r['shared_grip_gate']='Each wire OD/soft shims/no-crush/no-slip to dry-fit; not assumption that one strap grips different OD wires equally. 9mm seats/two row straps at differentY retained. Adhesive NOT strain relief.'
        bodies=[d.UpperCarrier,d.CommonSourcePlatform];vol=validate(d,bodies)
        assert all(abs(v-prior['native_geometry']['volumes_mm3'][n])<1e-6 for n,v in vol.items())
        # All material unchanged; only12straps are new. Original235pair
        # zero/error scope remains a named snapshot, not a new full-run count.
        targets=planned_shapes(read(OUT/'shared-allocation-plan.json'),mount,ctx)
        targets.update({b.Name:b.Shape for b in rail.Objects if b.TypeId=='PartDesign::Body' and b.Name!='DistributionSpacer'})
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
        current={b.Name:b.Shape for b in bodies}
        current.update({o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature' and 'Shape' in o.PropertiesList and not o.Shape.isNull()})
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            r['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        done=set()
        for n,s in changed.items():
            assert s.isValid() and len(s.Solids)==1,n
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():check(n,s,m,t)
            for m,t in current.items():
                pair=tuple(sorted((n,m)))
                if n==m or pair in done:continue
                done.add(pair);check(n,s,m,t)
        print('Changed12straps checked;5ATO budgets aftercut2bodyties',flush=True)
        r['ATO_access_scope']='22x10x35 project tool budget fromZ137; cut2ties on target body, independent wire grips left. Not measured supplier lid motion; open roof, not torso-contained tool.'
        for name,x in [('F_PI',-40),('F_AUX',-15),('F_HY',10),('F_HP',35),('F_TY',60)]:
            tool=Part.makeBox(22,10,35,A.Vector(x-11,-5,137))
            for m,t in {**targets,**current}.items():
                if m.startswith(name+'_BodyTie'):continue
                check(name+'/ATO_budget',tool,m,t)
        r['native_geometry']=prior['native_geometry'];r['parameter_test']=prior['parameter_test']
        r['print_dimensions_mm']=prior['print_dimensions_mm']
        if any(r[k] for k in ('contacts','errors','outside_torso')):
            r['status']='SOURCE_PLATFORM_FINISH_HAS_OPEN_INTERFACES'
            return
        d.save();A.closeDocument(d.Name);d=None
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-reopen-') as temp:
            path=Path(temp)/MODEL.name;shutil.copy2(MODEL,path)
            d=A.openDocument(str(path));bodies=[d.UpperCarrier,d.CommonSourcePlatform]
            reopened=validate(d,bodies);assert all(abs(v-reopened[n])<1e-6 for n,v in vol.items())
            baseline=[d.getObject('SourceMount'+str(i)+'Nut').Shape.BoundBox.ZMin for i in range(1,5)]
            d.SourceParameters.NutSeatDepth=2.8;trial=validate(d,bodies)
            assert trial['CommonSourcePlatform']<vol['CommonSourcePlatform']
            assert all(abs(d.getObject('SourceMount'+str(i)+'Nut').Shape.BoundBox.ZMin-z-.2)<1e-6 for i,z in enumerate(baseline,1))
            d.SourceParameters.NutSeatDepth=2.6;restored=validate(d,bodies)
            assert all(abs(v-restored[n])<1e-6 for n,v in vol.items())
            r['fresh_relocated_reopen_parameter_restore']=True
            exports={}
            for b in bodies:
                s=b.Shape.copy();box=s.BoundBox;s.translate(-A.Vector(box.XMin,box.YMin,box.ZMin))
                assert max(box.XLength,box.YLength,box.ZLength)<246
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.15,AngularDeflection=.2,Relative=False)
                assert mesh.isSolid();path=OUT/(b.Name+'Current.stl');assert not path.exists()
                mesh.write(str(path));assert Mesh.Mesh(str(path)).isSolid();exports[path.name]=sha(path)
            r['exports']=exports
        r['status']='COMMON_SOURCE_LOCAL_MOUNTS_INPUT_OUTPUT_RESTRAINTS_PREPARED_FULL_WIRING_OPEN'
        r['model_sha256']=sha(MODEL)
        r['files']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in
            [MODEL,PROOF,Path(__file__),ROOT/'tools/cad/open_prototype_common_source_platform.py']+[OUT/n for n in exports]]
        r['gates']={k:dict(status='open',reason=reason) for k,reason in dict(
            fit='Delivered casing/terminal/tie/nut/individual wire shim and no-slip test',
            petg='Profile/support removal/bridges/bearing/layers/creep',loads='Cantilever and vibration dry-fit tests',
            assembly='Local install plan, not full wired robot install/removal',electrical='Full routes/insulation/E3 remain open',
            geometry='Head/tail station load paths and full output fanouts/mounts not included',service='Actual lid motion delivery gate').items()}
    finally:
        for doc in (d,mount,ctx,rail):
            if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in r['source_sha256'].items())
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','outside_torso','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
