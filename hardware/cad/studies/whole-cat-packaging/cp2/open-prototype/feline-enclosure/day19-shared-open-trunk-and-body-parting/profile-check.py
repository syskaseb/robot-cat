from common import *
tag=sys.argv[1] if len(sys.argv)>1 else 'final'
s=(G/'named-check.py').read_text();s=s[:s.index("for w in ['W002'")];s=s.replace('whole-cat19G.FCStd','whole-cat19H.FCStd').replace("plan=json.loads((P/'whole-termination-plan.json').read_bytes())","plan=json.loads((G/'whole-termination-plan.json').read_bytes())").replace("'E19_ForeBase','E19_RearBase','E19_FrontShroud'","'H19_FrontFrame','E19_RearBase'");exec(s)
hard.extend(['G19_MIC_C_PlugAllow','H19_DATA_A_Boot','G19_PiAudioBoot','G19_H3_mate_allowance','TTP223_touch'])
for w,q in tr.items():
 p=np.asarray(q['points']);od=q['diameter']
 # Portions within purchased connectors are classified by port and sleeve. No installed
 # insulation is swept through a copper pad. Near the pad use an independent short bare land.
 if w.startswith('XS') or w in ['W078','W079','W080']:
    end=p[-1];delta=np.linalg.norm(p-end,axis=1);ins=p[delta>=2];bare=p[(delta<2)&(delta>.25)]
    screen(w,0,0,circle(ins,od/2))
    if len(bare)>1:screen(w+' bare land',0,0,circle(bare,.35))
 else:
    if w.startswith('W00'):p=p[p[:,2]<1000];p=p[7:] # H3 project mate itself occupies first axial approach
    screen(w,0,0,circle(p[1:-1],od/2))
out=dict(rows=rows,native=sha(native),source='shared-lay.json',scope='near named material with full jacket; final exposed solderland separately; isolated crossings located during hand lay',physical_PASS=False)
wr(tag+'-profiles.json',out);print([(r['field'],[(h['part'],h['point']) for h in r['hits']]) for r in rows if r['hits']])
