"""Coarse first falsifier for the current complete low module allocation."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,numpy as np,runpy
P=Path(__file__).parent
R=json.loads((P/"low-actors.json").read_bytes())
source=json.loads((P.parent/"day19-source-bom-budgets"/"source-budget.json").read_bytes())
by={q["name"]:q for q in R}
core=["Pi4B_actual_PCB","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","MAIN_Pololu4853","AUX_Pololu4092","Battery_GEA223S30X6GT","F0_FHAC0002_30A","XT60H_mated_with_boots","BUS25514_installed","Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp","BNO085","Monitor_MOD05015","S0_body","OP_S1_PRIMARY_CASE_CONSERVATIVE","BR_PAIR_HY","BR_FLANK_HP_PAIR","BR_FLANK_THREE_LAPS"]
core += [q["name"] for q in R if q["name"].startswith(("Motor_ATO","WAGO415","WAGO615","PBAY_"))]
candidates=[]
for i,a in enumerate(core):
    for b in core[i+1:]:
        aa,bb=np.array(by[a]["bounds"]),np.array(by[b]["bounds"])
        overlap=np.minimum(aa[3:],bb[3:])-np.maximum(aa[:3],bb[:3])
        if np.all(overlap>.05):candidates.append(dict(a=a,b=b,box_overlap_mm=overlap.tolist()))
# A box hit selects a named exact pair; it is not a material collision by itself.
exact=[]
Saved=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"]
D=Saved(P/"whole-cat19.FCStd")
# Bound the expensive gate to the first real changed rigid-interface witnesses.
for c in candidates[:6]:
    exact.append(dict(a=c["a"],b=c["b"],result=D.common(c["a"],c["b"])))
res=dict(scope="One low whole layout. Module-box candidates, six named exact neighbors only; no old global scan.",
         candidates=candidates,exact=exact,source_budget_sha256=hashlib.sha256((P.parent/"day19-source-bom-budgets"/"source-budget.json").read_bytes()).hexdigest(),
         physical_PASS=False,whole_accepted=False)
(P/"first-occupied-gate.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
print(json.dumps(dict(candidates=len(candidates),first_exact=exact),indent=1))
