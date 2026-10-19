"""Read pinned existing cells as a shared-section planning aid, not acceptance.

No new world voxelization, search, BRep changes or geometry approval. Rebuild
the union by source owner, never subtract a module mask from an occupied union.
"""
import io,json,zipfile,hashlib,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_signed_voxels import deposit
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();dest=OUT/'n01-upper-shared-sections.json'
    assert not dest.exists()
    source=OUT/'n01-current-signed-space.json';d=json.loads(source.read_text())
    field=ROOT/d['field'];arc=ROOT/d['voxel_source_archive']
    assert sha(field)==d['field_sha256'] and sha(arc)==d['voxel_source_archive_sha256']
    worldfile=OUT/'n01-roof-layer30-world-received.json';r=json.loads(worldfile.read_text())
    removed=set(r['retired_replaced_old_module_parts'])
    with np.load(field,allow_pickle=False) as f:
        origin=f['origin_mm'];occupied=np.zeros(tuple(f['rigid_occupied'].shape),bool)
        motion=f['motion36_signed_distance'].copy();outer=f['outer_distance'].copy()
    boxes={};kept=0
    with zipfile.ZipFile(arc) as z:
        for name,row in d['parts'].items():
            if not name.startswith('Static:') or name[7:] in removed:continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as f:
                mask=f['occupied'];local=f['origin']
            deposit(occupied,mask,local,origin);kept+=1
            cells=np.argwhere(mask)
            if len(cells):boxes[name[7:]]=[(local+cells.min(0)).tolist(),(local+cells.max(0)).tolist()]
    imagefile=dest.with_suffix('.png');fig,axes=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    ext=[origin[0],origin[0]+occupied.shape[0]-1,origin[1],origin[1]+occupied.shape[1]-1]
    for ax,z in zip(axes.flat,[100,85,70,50]):
        index=int(round(z-origin[2]));pixels=np.zeros((*occupied.shape[:2],3),float)+1
        pixels[outer[:,:,index]<5.75]=[.85,.85,.85]
        pixels[motion[:,:,index]<3.75]=[1,.65,.65]
        pixels[occupied[:,:,index]]=[.25,.32,.38]
        ax.imshow(pixels.transpose(1,0,2),origin='lower',extent=ext,interpolation='nearest')
        ax.set_title(f'Z={z} mm; retained owner cells only')
        ax.set_xlabel('X mm (head left, tail right)');ax.set_ylabel('Y mm');ax.grid(alpha=.2)
        ax.set_aspect('equal')
    fig.suptitle('Planning sections: conservative cells / motion / skin margin; NOT contact proof')
    fig.savefig(imagefile,dpi=130);plt.close(fig)
    failures={f['b'] for f in r['failures'] if not f['b'].startswith('Station:P_REAR:')}
    result=dict(status='PINNED_SHARED_SECTIONS_PLANNING_ONLY',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,field,arc,worldfile)},
        removed_replaced_module_owners=sorted(removed),retained_static_owners=kept,
        blocker_cell_bounds_mm={n:b for n,b in boxes.items() if n in failures},
        upper_owner_cell_bounds_mm={n:b for n,b in boxes.items() if b[1][2]>=68 and b[0][2]<=110},
        image=imagefile.relative_to(ROOT).as_posix(),image_sha256=sha(imagefile),
        false_internal_P_REAR_contact_count=sum(f['a'].startswith('Station:P_REAR:') and f['b'].startswith('Station:P_REAR:') for f in r['failures']),
        no_new_geometry_or_clearance_claim=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','removed_replaced_module_owners','upper_owner_cell_bounds_mm')}),flush=True)


if __name__=='__main__':main()
