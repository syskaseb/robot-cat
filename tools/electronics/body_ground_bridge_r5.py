"""Use a conservative whole-fuse height above the MTA flange, no guessed seat.

Littelfuse287 drawing full height18.8mm, not just plastic12.3mm.
Reserve flange top111 + whole18.8 =129.8; wire centre136.5 clears it.
Actual inserted depth/terminals remain phase2. Preserve R4 as diagnostic.
"""
from pathlib import Path
import body_ground_routes_r1 as M
M.OUT=M.ROOT/"hardware/electronics/full-cat/body-ground-bridge-r5"
M.STRAIGHT=2.0
M.SPECS={"W061":("G1.5",[58.5,11,113.5],1,"G2.1",[111,9.5,113.5],1,136.5,75)}
prior_save=M.save

def save(p,value):
    if p.name=="intent.json":
        value["cage_labels"]={"G1":[".1",".5",".3",".4",".2"],"G2":[".2",".3",".1",".4",".5"]}
        value["remap_rule"]="Equal-potential cage labels only. G1.1 BAT original nearest51; G1.2 MAIN input logical role now physical81 and its open W060 route must adopt it. G2.4 BUS/G2.5 XA05 retained."
        value["scope"]="W061 only. Four ground returns and other body/source/leg routes remain open."
        value["fuse_height_reserve"]={"MTA_flange_top_mm":111,"whole_287_height_mm":18.8,"conservative_top_mm":129.8,"why":"Conservatively put the entire fuse ABOVE flange instead of guessing inserted depth.","source_drawing":"hardware/reference/servo-holder-p0-2026-09-24/0300330.png","manufacturer_url":"https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40","verified_date_utc":"2026-10-02"}
    if p.name=="lengths.json" or p.name=="checks.json":
        lengths=value if p.name=="lengths.json" else value["lengths"]
        for row in lengths.values():
            row.pop("nominal_strip_each_mm",None)
            row["nominal_strip_by_end_mm"]={"G1.5":[12,14],"G2.1":11}
            row["reserve_28mm_is_not_stripping_instruction"]=True
        if p.name=="checks.json":value["wrapper_sha256"]=M.sha(Path(__file__))
    prior_save(p,value)

M.save=save
if __name__=="__main__":M.main()
