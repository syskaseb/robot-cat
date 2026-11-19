from pathlib import Path
P=Path(__file__).parent
s=(P/'cradle-bands.py').read_text();exec(s[:s.index('proto=band()')])
before=json.loads((P/'band-seat.json').read_bytes());res={}
for code,basis in [('HY','H19_FrontFrame'),('AUX','H19_FrontFrame'),('PI','E19_RearBase')]:
 opt=before[code][0];assert list(opt['hits'])==[basis]
 b=sh('PBAY_F_'+code).BoundBox;q=band()
 q.Placement=(A.Placement(V(b.XMax,b.YMin+51*.76,b.ZMin),A.Rotation(V(0,0,1),90)) if code=='HY' else A.Placement(V(b.XMin+51*.19,b.YMin,b.ZMin),A.Rotation()))
 frame=sh(basis).Solids[0];void=q.makeOffsetShape(.14,.01);s=frame.cut(void,.00001).removeSplitter();assert len(s.Solids)==1 and s.isValid()
 res[code]=dict(original_common=q.common(frame).Volume,removed_mm3=frame.Volume-s.Volume,after_common=q.common(s).Volume)
 assert res[code]['after_common']<.0001
 D.getObject(basis).Shape=s;add('I19_FuseBand_'+code,q,(.32,.45,.52),'standard removable paired hooks under transverse case rung; unhook before removing entire holder')
wr('band-receivers.json',res)
n='E19_RearLid';s=sh(n).cut(box(55.5,-35.30,164,11.1,10.6,10.1),.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid();D.getObject(n).Shape=s
