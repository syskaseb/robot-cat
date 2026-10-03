"""Complete outboard output returns, not the rejected diagonal R1 crossings.

Run each extension straight outside the MTA/ground case before its westward
rise and turn. Mate two actual same-face WAGO cages with tangent factory
paths, preserving100mm project stock/10mm reserve and existing radius limits.
All three factory approaches and both ends change coherently. Native grips
and any casing relief remain OPEN pending the declared shared check.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r1.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("servo-fuse-output-returns-complete-r1'","servo-fuse-output-returns-complete-r2'")
code=code.replace('    pins={};V=A.Vector;',"    pins={};V=A.Vector;")
code=code.replace("    native=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r1.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r1/checks.json')\n    native=ROOT/",1)
a=code.index('    for leg,ident,left,cy,cz,rise_sine,extra,target_y in [')
b=code.index('    for n,s in changed.items():s.exportBrep',a)
code=code[:a]+'''    for leg,ident,left,cy,cz,sine,turn_y,target_y in [
        ('FR','W037',-79.5,-72,126,.6,-95.8,-121),
        ('RL','W045',16.5,72,130,.7,87.8,113),
        ('RR','W053',28.5,-86,121.5,.5,-91.8,-117)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        mx=-82.5 if leg=='FR' else 25.5
        e=Route([mx,side*49.5,113.5]);e.line([mx,turn_y,113.5])
        co=math.sqrt(1-sine**2);normal=-X*co+Z*sine
        e.arc(Y,normal,25.2)
        e.arc(normal,-X*sine-Z*co,25.2,math.asin(sine))
        assert abs(e.p.y-target_y)<1e-6
        # RL terminates at the retained130mm factory level, shifted west
        # away from both closed P_AUX and the tall F_FL3 blade envelope.
        if leg=='RL':
            tx=-30;factory_z=130;extension_z=136.5
            e.shift(-X,Z*(extension_z-e.p.z),25.2)
            straight=e.p.x-tx;assert straight>=4,dict(leg=leg,straight=straight)
            e.line([tx,target_y,extension_z])
        else:
            tx=e.p.x;extension_z=e.p.z;factory_z=extension_z-6.5
            straight=0
        f=Route([left,cy,cz]);delta=Z*(factory_z-cz)
        extra=left-tx-20
        if delta.Length>1e-6:
            travel=math.sqrt(4*20*delta.Length-delta.Length**2)
            assert extra>=travel,dict(leg=leg,extra=extra,travel=travel)
            f.shift(-X,delta,20)
        f.line([tx+20,cy,factory_z]);f.arc(-X,Y,20)
        assert abs(f.p.x-tx)<1e-6 and abs(f.p.z-factory_z)<1e-6
        assert (V(tx,target_y,factory_z)-f.p).dot(Y)>=0
        f.line([tx,target_y,factory_z])
        lowy=min(target_y,target_y+side*18.3);lowz=factory_z-3.25
        changed[ident+'_221412']=Part.makeBox(8.15,18.3,13,V(tx-4,lowy,lowz))
        wire(ident+'_factory',f,5,'MTA_factory',11,leg)
        wire(ident+'_extension',e,4.2,'HELU23802',25,leg)
        joints.append(dict(id=ident,leg=leg,kind='WAGO221-412',SKU='221-412',
            ports_mm=[[tx,target_y,factory_z],[tx,target_y,extension_z]],
            body_bounds_mm=[tx-4,lowy,lowz,tx+4.15,lowy+18.3,lowz+13],
            strip_mm=11,grip_straight_extension_mm=straight,
            extension_grip_strategy=('4mm end seat' if leg=='RL' else 'Native grip on retained straight outside MTA before the bend; WAGO housing independently restrained.'),
            dimensions_source=facts.relative_to(ROOT).as_posix(),
            native_grips='OPEN: two insulation restraints and housing retention after full shared fit.',
            recipe='Removed unpowered Deck: one UNTINNED4mm2 bare end per separate same-face cage; close levers before fixing. Upper extension/lower factory labels must follow these paths at selection.',
            assumptions='Nominal manufacturer envelope/project cage centres, not delivered lever motion or tolerance. No strip length or100mm factory allowance reduced.'))
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))
