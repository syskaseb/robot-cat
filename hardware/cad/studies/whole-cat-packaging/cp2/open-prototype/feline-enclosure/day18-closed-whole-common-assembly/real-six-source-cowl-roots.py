import FreeCAD as A,Part,json
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
# Copy actual retained receiver material ONLY, not old skins or their superseded envelope.
parts=[]
for n in ['CLOSED_BODY_front_negative','CLOSED_BODY_front_positive','CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive']:
 parts.append(D.getObject(n).Shape.common(box(-155,-115,41.5,350,230,4.52)))
lower=parts[0].multiFuse(parts[1:]).removeSplitter()
rows=[]
for fore,x0,x1,axes in [('FORE',-155,20,[-70]),('REAR',20,195,[70,145])]:
 for tag,side in [('NEG',-1),('POS',1)]:
  o=D.getObject('F3_BODY_'+fore+'_'+tag);old=o.Shape.copy();y0=-115 if side<0 else 0
  low=lower.common(box(x0,y0,41.5,x1-x0,115,4.52));members=[old,low];intended=[]
  for x in axes:
   # Outboard column joins the actual source peripheral receiver, clear of the bought deck edge.
   m=box(x-6,84.5 if side>0 else -88.5,43.62,12,4,14.38);members.append(m);intended.append(m)
   if x==70 and side<0:
    # Preserve relocated whole F_PI: route load around its X87 outer end, not through the case.
    add=[box(64,-88.5,55,34,4,3),box(89,-88.5,55,6,47.5,3)]
   elif x==145:
    # Raised rump wall attaches above the real floor on an outboard crossarm, outside S0 X144.
    add=[box(139,84.5 if side>0 else -88.5,55,15,4,3),box(148,84.5 if side>0 else -88.5,55,6,4,17),box(148,38 if side>0 else -88.5,68,6,50.5,4)]
   else:add=[box(x-5,43 if side>0 else -88.5,55,10,45.5,3)]
   members+=add;intended+=add
  s=members[0].multiFuse(members[1:]).removeSplitter();o.Shape=s
  rows.append({'part':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume':s.Volume,'new_PETG_g':s.Volume*.00127,'retained_wall_missing':old.cut(s).Volume,'copied_actual_receiver_missing':low.cut(s).Volume,'new_member_missing':[m.cut(s).Volume for m in intended],'extent':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength]})
for o in D.Objects:
 if o.Name.startswith('BASE') and any(t in o.Name for t in ['M3x10_FULL','lowerwasher','upperwasher','fullnut']):o.ViewObject.Visibility=True
wr('six-source-roots-to-current-cowls.json',{'method':'actual source removable lower receiver/6 bearing tabs copied from retained BRep, then real connected outboard columns and upper arms into current cowl walls; old 36 source hardware/tool checks by identity only','source_axes':[[x,y] for x in [-70,70,145] for y in [-72,72]],'full_source_sets':'6x M3x10 HEX AF5.5, head2, two OD7x.5 washers/full AF5.5x2.4 nut/full tip1.7','deck_functions_unchanged':True,'parts':rows,'assembly':'Preload full upper washers/nuts into actual P02/P03 cages before modules. Fit FOUR cowl halves later by their source open-sided 2.4mm bearing tabs under deckweb2.5, insert retained full six bolts and lower washers from proven side/bottom phase. New arms only, no bought drilling. Cross-seam and open neck/tail closure still engineering OPEN.','not_whole_kit':True,'physical_PASS':False})
D.recompute();D.save();print('SIX_REAL_SOURCE_ROOTS',rows)
