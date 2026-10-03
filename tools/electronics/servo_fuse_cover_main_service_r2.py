"""Segmented wire service space, not the rejected whole-owner strap boxes.

The body/source/output straps are consumables released for this service.
Use each actual wire face's conservative projected footprint, not the large
empty corners of a complete bent lead. Preserve all four mounting regions.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_main_service_r1.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r1_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-main-service-r1','servo-fuse-cover-main-service-r2')
old="            or k.startswith(('FRTie/','RLTie/','RRTie/','PWagoTie/'))}"
assert old in code;code=code.replace(old,'            }')
begin=code.index('        for index,(key,s) in enumerate(chosen.items()):')
end=code.index('        assert len(tools)>20',begin)
code=code[:begin]+'''        for key,s in chosen.items():
            covered.append(key)
            for fi,face in enumerate(s.Faces):
                q=face.BoundBox
                if q.ZMax<=bottom:continue
                dims=[max(q.XLength,.001),max(q.YLength,.001),q.ZMax-bottom]
                tool=d.addObject('Part::Box','MainServicePassage'+str(len(tools)))
                tool.addProperty('App::PropertyString','RetainedOwner');tool.RetainedOwner=key+'/Face'+str(fi+1)
                for prop,val in zip(('Length','Width','Height'),dims):
                    tool.setExpression(prop,f'{val} mm + 2*MainFeedServiceParameters.Allowance')
                for axis,val in zip(('x','y','z'),(q.XMin,q.YMin,bottom)):
                    tool.setExpression('Placement.Base.'+axis,f'{val} mm - MainFeedServiceParameters.Allowance')
                tools.append(tool);b.append([q.XMin-.3,q.YMin-.3,bottom-.3,q.XMax+.3,q.YMax+.3,q.ZMax+.3])
'''+code[end:]
code=code.replace("print('COVER_RR_OPEN_BOTTOM_RECOMPUTE',b,flush=True)","print('COVER_MAIN_SEGMENTED_RECOMPUTE',len(tools),len(covered),flush=True)")
marker="        v=s.Volume;p.Allowance=.4;"
assert marker in code
code=code.replace(marker,"""        removed=parent.Shape.cut(s);mounts=[]
        for x in (-84,106):
            for side in (-1,1):
                lo,hi=sorted((side*85,side*97))
                zone=Part.makeBox(12,hi-lo,12,A.Vector(x-6,lo,109))
                loss=removed.common(zone).Volume;mounts.append(dict(xy=[x,side*91],removed_mm3=loss))
        if any(r['removed_mm3']>1e-5 for r in mounts):
            d.saveAs(str(dest));s.exportBrep(str(OUT/'REJECTED_COVER.brep'))
            save(OUT/'checks.json',dict(status='SEGMENTED_SERVICE_REJECTED_MOUNT_LOSS',mounts=mounts,state=state,tool_mm=b,selected=False,physical_pass=False,source_sha256=pins,script_sha256=sha(Path(__file__))))
            print('COVER_MAIN_SEGMENTED_MOUNT_REJECTED',mounts,flush=True);return
        v=s.Volume;p.Allowance=.4;""")
code=code.replace("assembly_ties_cut=33,", "assembly_ties_cut=49,mounts=mounts,")
code=code.replace("Conservative whole-owner rectangles for downward service; not measured contact bounds", "Conservative individual wire-face projections extended to bottom; body/source/output ties released, lower input ties retained; not measured contact bounds")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
