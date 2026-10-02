"""Keep the R2 routes; place six ties in intact Deck material.

Two ties rotate onto straight X lanes, avoiding the retained Pi fan opening
and the existing return-wire slot. No filling or narrowing inherited openings.
"""
import body_data_bridges_r2 as R2

M=R2.M
M.OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r3"
M.CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r3"
M.ANCHORS=[(n,e,(-1.5 if n=="W007" and e==0 else 103.8 if n=="W011" and e==1 else x),
               (17.5 if n=="W007" and e==0 else -17.5 if n=="W011" and e==1 else y))
           for n,e,x,y in M.ANCHORS]
M.ANCHOR_ROTATIONS={("W007",0):90,("W011",1):90}
M.DATUM_OVERRIDES.update(restraint_change="W007 north restraint on its straight X lane at(-1.5,17.5); W011 east restraint on its straight X lane at(103.8,-17.5). Both rotated90deg; preserve Pi fan window and old return slot.",
    R2_rejected_cut_volume_mm3=245.60242677309625,
    expected_twelve_full_slots_mm3=307.2)

if __name__=="__main__":M.main()
