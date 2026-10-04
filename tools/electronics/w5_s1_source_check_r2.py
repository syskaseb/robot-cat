"""Check one lowered-P_SYS/outward-ring family; all six leads remain open.

Do not silently omit the old W043/W066 and their restraints. Their contacts
show the work reopened by this proposed displacement, not completed wiring.
"""
from pathlib import Path
import runpy

BASE=Path(__file__).with_name('w5_s1_source_check_r1.py')
source=BASE.read_text(encoding='utf-8')


def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)


replace("w5-s1-source-check-r1'","w5-s1-source-check-r2'")
replace("w5-s1-source-layout-r1/intent.json'","w5-s1-source-layout-r2/intent.json'")
replace("    assert len(intent['routes'])==4 and not intent['selected']", """    assert len(intent['routes'])==4 and not intent['selected']
    assert intent['source_qualified_wires_reopened']==['W043','W066']""")
replace("    owners['S1_body_provisional']=box([111,49,66,135,91,103])", """    owners['S1_body_provisional']=box([111,49,66,135,91,103])
    old_system=owners['P_SYS_design'].copy()
    owners['P_SYS_design']=old_system.copy()
    owners['P_SYS_design'].translate(A.Vector(*intent['P_SYS_displacement_mm']))""")
begin=source.index("    for row in intent['routes']:\n        end=row['end'];left=")
end=source.index('    geometries=[]',begin)
source=source[:begin]+'''    for row in intent['routes']:
        end=row['end'];front=row['wire'] in ('W064','W065')
        ymin=end[1] if front else end[1]-27.686
        owners[row['b']+'_ring_provisional']=box([end[0]-9.525/2,ymin,56,end[0]+9.525/2,ymin+27.686,68])
''' +source[end:]
replace("    for row in intent['routes']:\n        edges=[];pieces=[]", """    for key,other in owners.items():
        if key!='P_SYS_design':check('P_SYS_DISPLACED_BODY',owners['P_SYS_design'],key,other,'changed_bought_body')
    for row in intent['routes']:
        edges=[];pieces=[]""")
begin=source.index('    # Receive the whole leg candidate first.')
end=source.index('    files=[]',begin)
source=source[:begin]+'''    # This is one source family, not a qualification of the rejected leg R4.
    leg_file=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r1/checks.json'
    leg_folder=leg_file.parent
    leg=dict(status='NOT_INCLUDED_IN_SOURCE_FAMILY_PROOF',errors=[])
''' +source[end:]
replace("pins=owner_pins+[source,selected_file,deck,bus_file,leg_file,leg_folder/'FANOUTS_WORLD.brep',leg_folder/'RELOCATED_OWNERS_WORLD.brep',Path(__file__),",
        "pins=owner_pins+[source,selected_file,deck,bus_file,leg_file,Path(__file__),BASE,")
replace("status='SOURCE_ROUTES_REJECTED' if fixed or errors else 'SOURCE_STATIC_ROUTES_ONLY_RESTRAINTS_OPEN'",
        "status='JOINT_SOURCE_REJECTED' if fixed or errors else 'JOINT_SOURCE_INTERFACES_OPEN'")
replace('        selected=False,W5_complete=False,physical_pass=False,',
        "        source_qualified_wires_reopened=['W043','W066'],P_SYS_supports_reopened=True,selected=False,W5_complete=False,physical_pass=False,")
exec(compile(source,str(Path(__file__).resolve()),'exec'))
