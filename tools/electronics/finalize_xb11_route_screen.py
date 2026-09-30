"""Package the saved full-route failures, without another CAD collision run."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r1=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r1'
    r2=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r2'
    checks=json.loads((r2/'checks.json').read_text(encoding='utf-8'))
    assert not checks['geometry_nominal_clear'] and not checks['selected']
    samples=checks['centerline_samples_mm']
    fig,axs=plt.subplots(1,3,figsize=(14,5))
    for ax,(i,j,label) in zip(axs,[(0,1,'XY'),(0,2,'XZ'),(1,2,'YZ')]):
        ax.plot([p[i] for p in samples],[p[j] for p in samples],color='#b82126',linewidth=2)
        ax.scatter([samples[0][i],samples[-1][i]],[samples[0][j],samples[-1][j]],color='black',s=22)
        ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(label+' exact centerline samples');ax.set_xlabel('XYZ'[i]+' mm');ax.set_ylabel('XYZ'[j]+' mm')
    fig.suptitle('XB11 full-route R2 REJECTED: cooling hat + lower shell; anchors not designed')
    fig.tight_layout();fig.savefig(r2/'preview.png',dpi=150);plt.close(fig)
    files=[Path(__file__).resolve(),ROOT/'tools/electronics/xb11_upstream_route.py',ROOT/'tools/electronics/xb11_upstream_raise.py']
    for folder in (r1,r2):files += [folder/n for n in ('plan.json','checks.json','XB11_DESIGN.brep','README.md')]
    files.append(r2/'preview.png')
    result={'status':'BOTH_FULL_ROUTES_REJECTED_NO_SELECTED_ROUTE','files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files},
            'new_stls':0,'new_skus':0,'physical_pass':False,'not_print_jobs':True,
            'next':'Locate actual shell crossing and use a supported route/guarded opening outside Pi cooling hat; do not shrink specified wire bend radius or waive shell collision.'}
    (r2/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'new_stls':0,'R1':'rejected','R2':'rejected','next':'shell crossing/guard and hat bypass'}))
if __name__=='__main__':main()
