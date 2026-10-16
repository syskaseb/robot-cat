"""One simultaneous material allocation for all remaining55 saddle groups.

No wire moves. Finite normal/closure choices, then exact shared material gate.
Same-parent roots/native case mounting remain separate mandatory results.
"""
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
from current_source_retention_context import context, same_parent, P, C
from check_main_p0_placement import SavedShapes
from loom_land_port import box
from current_work_guard import check


def normals(axis, common):
    z=A.Vector(*axis);values=[]
    for seed in ([0,1,0],) if common else ([1,0,0],[0,1,0],[0,0,1]):
        v=A.Vector(*seed);v-=z*v.dot(z)
        if v.Length<1e-7:continue
        v.normalize()
        for sign in (1,-1):
            n=list(v*sign)
            if not any(math.dist(n,q)<1e-6 for q in values):values.append(n)
    return values


def profile(g,normal,knot_sign):
    r=g['project_radius_mm'];span=g.get('lateral_half_span_mm',r+.2)
    z=A.Vector(*g.get('axis',g.get('common_axis')));n=A.Vector(*normal);y=z.cross(n)
    assert abs(n.dot(z))<1e-7 and abs(y.Length-1)<1e-7
    m=A.Matrix()
    for col,v in enumerate((n,y,z),1):
        for row,a in enumerate(v,1):setattr(m,'A'+str(row)+str(col),a)
    m.A14,m.A24,m.A34=g['centre_world_mm']
    t=.381;w=1.6764
    pads=[[r+.5,-span,-1.5,r+4.5,span,1.5],
          [r+.5,-span,1.4,r+4.5,span,4.5]]
    outer=[-r-.2-t-.15,-span-.2-t-.15,-w/2-.15,r+4.5+t+.15,span+.2+t+.15,w/2+.15]
    inner=[-r-.2+.15,-span-.2+.15,-w,r+4.5-.15,span+.2-.15,w]
    body=box(pads[0]).fuse(box(pads[1])).cut(box(outer).cut(box(inner))).removeSplitter()
    band=box([-r-.2-t,-span-.2-t,-w/2,r+4.5+t,span+.2+t,w/2]).cut(
        box([-r-.2,-span-.2,-w,r+4.5,span+.2,w]))
    knot=[r+4.5+t,-1,-1.5,r+7.5+t,1,.5] if knot_sign==1 else [-r-.2-t-3,-1,-1.5,-r-.2-t,1,.5]
    band=band.fuse(box(knot)).removeSplitter()
    for s in (body,band):
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        s.Placement=A.Placement(m)*s.Placement
    assert body.common(band).Volume<1e-6
    tip=A.Placement(m).multVec(A.Vector(r+3,0,3))
    return dict(body=body,band=band,root_tip_mm=list(tip),
        recipe=dict(normal=normal,knot_sign=knot_sign,pads=pads,ring_cut=dict(outer=outer,inner=inner),
                    knot=knot,local_to_world=list(m.A),axial_cradle_mm=3,
                    allocated_straight_mm=g['land_mm'],project_lacing_blank_mm=150,
                    physical_retention_verified=False))


def current_context():
    targets,wires,pins,oldprofiles,recipes,parents,grips=context()
    f=P.OUT/'local-source-retention-native/manifest.json';p=json.loads(f.read_text())
    assert p['status']=='THIRTEEN_SOURCE_LANDS_FIVE_NATIVE_PARENT_REPLACEMENTS_COMPLETE'
    reader=SavedShapes()
    for r in p['models']:assert P.SHA(P.ROOT/r['path'])==r['sha256']
    for r in p['parts']:
        shape=reader.shape(P.ROOT/r['native'],r['object']);owner=r['part']
        parents[owner]=shape
        if owner in ('LeftRiser','RightRiser'):targets['neck/'+owner]=shape
        else:targets['CurrentNative/'+owner]=shape
        for name in r['lacing_reference_objects']:
            targets['RetainedSourceLacing/'+name]=reader.shape(P.ROOT/r['native'],name)
    pins.update(reader.hashes);pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    return targets,wires,pins,parents,grips


def run():
    check();tick=time.monotonic();pf=P.OUT/'remaining25-interface-allocation.json';p=json.loads(pf.read_text())
    assert p['physical_ends']==66 and len(p['groups'])==55
    for n,h in p['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,parents,grips=current_context()
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,Path(__file__))})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'remaining25-restraint-pairs.json',bounds.near)
    rows=[];errors=[];checks=0;accepted={};domains={};failures=[];materials={}
    endpoints={e['id']:e for e in p['ends']}
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        check();checks+=1
        try:
            gap,volume=cache.check(a,b,0,r)
            return volume>1e-5 or bool(r and gap<r-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:
            errors.append(str(e));return True
    def save(status):
        result=dict(status=status,groups=rows,domains=domains,selected_options=accepted,
            failed_groups=failures,errors=errors,checks=checks,
            worker_seconds=round(time.monotonic()-tick,3),source_sha256=pins,
            scope='Current55 new insulation saddles/loops against current36/retained19/25 and13 native source lands. '
                  'Nominal purchased envelopes are conservative allocation constraints, not proof of a physical supplier collision. '
                  'No structural root or future bank support is silently accepted.',
            open=['Chosen parent roots and current bank/source cases M4',
                  'Native/installed assembly/whole stock/current whole-model binding'],
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'remaining25-restraint-space.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    for g in p['groups']:
        check();gid=g['id'];row=dict(id=gid,qualified_options=[],rejected=[]);rows.append(row)
        own={endpoints[e]['wire'] for e in g['ends']}
        options=[]
        for normal in normals(g.get('axis',g.get('common_axis')),len(g['ends'])==3):
            for sign in (1,-1):
                q=profile(g,normal,sign);contacts=[];touching=set()
                for kind in ('body','band'):
                    s=q[kind]
                    for n,t in targets.items():
                        if not t.Solids or not hit(s,t):continue
                        owners=[o for o in parents if same_parent(o,n,grips)]
                        if kind=='body' and len(owners)==1:touching.add(owners[0])
                        else:contacts.append(dict(part=kind,obstacle=n))
                        if len(contacts)>=3:break
                    if len(contacts)>=3:break
                    for n,(w,r) in wires.items():
                        own_wire=any(n==wid or n in ('wire/'+wid,wid+'_FACTORY',wid+'_CUSTOM') for wid in own)
                        if hit(s,w,r if kind=='band' and own_wire else r+.25):
                            contacts.append(dict(part=kind,obstacle=n))
                            if len(contacts)>=3:break
                if len(touching)>1:contacts.append(dict(part='body',obstacle='Different printed parents bridged'))
                if contacts:
                    row['rejected'].append(dict(normal=normal,knot_sign=sign,witnesses=contacts))
                else:
                    q['touching_parents']=sorted(touching);options.append(q)
                    row['qualified_options'].append(dict(index=len(options)-1,recipe=q['recipe'],
                        root_tip_mm=q['root_tip_mm'],touching_parents=q['touching_parents']))
        domains[gid]=row['qualified_options']
        if not options:failures.append(gid)
        else:materials[gid]=options
        save('REMAINING25_MATERIAL_DOMAINS_IN_PROGRESS')
        print('remaining25 domain',gid,'options',len(options),'pairs',checks,flush=True)
        # Stop a known dead shared architecture before native/detail work.
        # Retain all received domains; next run must change the cause, not
        # recompute identical successful groups.
        if len(failures)>=2 or errors:break
    if failures or len(rows)!=55 or errors:
        save('REMAINING25_SHARED_MATERIAL_ALLOCATION_REQUIRES_LAYOUT_CHANGE')
        return
    ordered=sorted(materials,key=lambda n:len(materials[n]));chosen={};attempts=0
    def select(i):
        nonlocal attempts
        check()
        if i==len(ordered):return True
        gid=ordered[i]
        for index,q in enumerate(materials[gid]):
            attempts+=1
            if attempts>10000:return False
            if any(hit(q[a],other[b]) for other in chosen.values() for a in ('body','band') for b in ('body','band')):continue
            chosen[gid]=q;accepted[gid]=index
            if select(i+1):return True
            chosen.pop(gid);accepted.pop(gid)
        return False
    clear=select(0)
    save('FIFTY_FIVE_REMAINING_SADDLE_DOMAINS_AND_SHARED_MATERIAL_CLEAR_ROOTS_OPEN' if clear else
         'REMAINING25_SHARED_MATERIAL_NO_JOINT_SOLUTION')
    print('remaining25 shared',clear,'groups',len(accepted),'pairs',checks,'seconds',round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':run()
