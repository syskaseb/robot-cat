"""Select one supported W061 Deck replacement, retaining every R37 byte pin."""
import copy
import json
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools/cad"))
from release_check import verify,sha256
PARENT=ROOT/"hardware/manufacturing/one-batch-prototype-r37"
BATCH=ROOT/"hardware/manufacturing/one-batch-prototype-r38"
OUT=ROOT/"hardware/electronics/full-cat/body-ground-bridge-finish-r5"
CAD=ROOT/"hardware/cad/studies/body-ground-bridge-finish-r5"
ROUTE=ROOT/"hardware/electronics/full-cat/body-ground-bridge-r5"
START="2026-10-02T01:22:36+00:00"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

def main():
    assert not (BATCH/"manifest.json").exists()
    c=read(OUT/"checks.json");i=read(OUT/"interface.json")
    assert c["status"]=="SUPPORTED_GROUND_BRIDGE_COMPLETE" and not c["hits"] and c["new_STL"]==1
    assert (OUT/"preview.png").is_file(),"Inspect actual geometry preview before packaging"
    start=datetime.now(timezone.utc);tick=time.monotonic();runs=[]
    for pattern in ("test_body_ground_bridge.py","test_body_data_bridges_r3.py"):
        r=subprocess.run([sys.executable,"-X","utf8","-m","unittest","discover","-s","tools/electronics","-p",pattern,"-v"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
        runs.append(dict(pattern=pattern,exit_code=r.returncode,output=r.stdout+r.stderr))
    save(OUT/"regression-run.json",dict(start_utc=start.isoformat(),measured_seconds=time.monotonic()-tick,runs=runs,physical_pass=False))
    assert all(r["exit_code"]==0 for r in runs),runs
    parent=read(PARENT/"manifest.json");assert verify(ROOT,parent)["integrity_ok"]
    selection=copy.deepcopy(read(PARENT/"selection.json"));q=copy.deepcopy(read(PARENT/"one-order-quantities.json"))
    e=next(r for r in selection["prints"] if r["identity"]=="electronics:DeckP10-cover-mount");before=copy.deepcopy(e)
    e.update(stl=(CAD/"Deck_x1.stl").relative_to(ROOT).as_posix(),sha256=sha256(CAD/"Deck_x1.stl"),
        native=(CAD/"DeckGroundBridgeSupported.FCStd").relative_to(ROOT).as_posix(),recipe=(OUT/"interface.json").relative_to(ROOT).as_posix(),
        orientation="World+Zup, lower Deck base on bed; existing DATA seats plus three integral W061 seats. PETG/supports/slicer phase2.",
        print_size_mm_including_5mm_brim=[v+10 if j<2 else v for j,v in enumerate(c["dimensions_mm"])])
    assert e["quantity"]==1 and len(selection["prints"])==71 and selection["installed_petg_parts"]==110
    recipe=(OUT/"interface.json").relative_to(ROOT).as_posix()
    selection.update(parent_selection_sha256=sha256(PARENT/"selection.json"),phase1_percent=70,W5_complete=False,
        fixed_ground_bridge=recipe,fixed_ground_bridge_sha256=sha256(OUT/"interface.json"),replaced_ground_Deck=before,
        W5_recipe_precedence="R38 W061 interface supersedes only legacy W061 geometry/blank and equal-potential G1/G2 cage locations. G1.1 BAT and G2.4/.5 retained; open W060 MAIN input must use G1.2 at X81. R37 DATA and every other retained recipe remain effective. Whole W5 OPEN.")
    q["selected_prints"]=(BATCH/"selection.json").relative_to(ROOT).as_posix()
    tie=next(r for r in q["lines"] if r["id"]=="tie:111-02370")
    assert tie["installed"]==87 and tie["planning_quantity"]==100
    tie["installed"]=90;tie["note"]+=" R38 adds three W061 insulation restraints from the same100pc bag. Working90, not the final K3 census."
    wire=next(r for r in q["lines"] if "2500125" in r["name"])
    assert wire["planning_quantity"]==2 and wire["unit"]=="m"
    wire["note"]+=" R38 W061 one240mm blank from shared2m stock. Nominal exposed181.575mm; reserve28mm plus30mm rework is not stripping. G1.5 strip12-14mm, G2.1 strip11mm; confirm delivered markings. Other grounds/stock balance OPEN."
    q.update(fixed_ground_bridge=recipe,fixed_ground_ties_from_existing_bag100=3)
    assert q["line_count"]==113 and len(q["lines"])==113
    BATCH.mkdir(exist_ok=True);save(BATCH/"selection.json",selection);save(BATCH/"one-order-quantities.json",q)
    summary=("# R38: podparty stały mostek masy G1–G2\n\n"
        "Jeden zamiennik Deck, trzy integralne podparcia W061, cztery pełne przeloty w Deck i dwa w wysuniętym siodełku. "
        "Zachowane P0, E6, otwór chłodzenia i sześć podparć DATA R37. "
        "71 zadań/110 PETG/4 próbki i113 wierszy ilości bez zmian.\n\n"
        "W061: G1.5→G2.1, jeden TKD2500125 SiF4mm², OD4,2mm i promień statyczny≥21mm. "
        "Blank240mm ze wspólnego2m; nominalna trasa181,575mm. Trzy111-02370: roboczo90 ze wspólnego100szt. "
        "G1 kolejność +X [.1,.5,.3,.4,.2], G2 [.2,.3,.1,.4,.5]; są to równe potencjały w każdym złączu, nie przeplot P/G. "
        "BAT pozostaje przy X51; otwarty W060 MAIN input przy X81.\n\n"
        "G1.5 nominalne odizolowanie12–14mm, G2.1=11mm; potwierdzić oznaczenia dostawy. "
        "Nie stosować28mm rezerwy jako długości odizolowania. Cały bezpiecznik18,8mm z rysunku Littelfuse287 "
        "zarezerwowany powyżej kołnierza111mm, bez zgadywania zagłębienia. Nominalna rezerwa od przewodu4,6mm. "
        "Dostawa i PETG pozostają fazą2.\n\n"
        "Opaski przełożyć przed elektroniką, założyć bezpieczniki przed przewodem, osadzić izolację w siodełkach "
        "i dociągnąć ręcznie bez zgniatania. Przy zasłoniętym wyjmowaniu bezpiecznika: najpierw odłączyć baterię, "
        "zdjąć Carrier, przeciąć3opaski, odłączyć oba końce W061 i unieść pętlę. Opaski wymienić.\n\n"
        "Odrzucone drogi/szkice nie są wybranymi wydrukami. Środkowe podparcie sprawdzono względem rzeczywistej płyty. "
        "Źródła native/parametry/ponowne otwarcie, zamknięta siatka, zmienione interfejsy i testy w checks.json. "
        "70%=14/20,+0pp. E3/W5/K2/K3/A2/A3 OPEN; nie deklaruje się fizycznego PASS. "
        "Pozostałe cztery powroty masy, zasilanie/źródło, ruchome wiązki nóg i balans nadal wymagają przygotowania.\n")
    (BATCH/"README.md").write_text(summary,encoding="utf-8",newline="\n")
    (OUT/"README.md").write_text(summary,encoding="utf-8",newline="\n")
    end=datetime.now(timezone.utc)
    save(OUT/"work-time.json",dict(start_utc=START,end_utc=end.isoformat(),wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        kind="Five-return rejected intent, one complete W061 route, native seats/passages, parameter/reopen/export/current-interface checks/tests/package",separately_measured_phases=False,active_robot_work_seconds=None,
        wall_time_includes_user_interruptions=True,new_STL=1,replacement_STL=True,W5_complete=False,physical_pass=False))
    pins={r["path"]:r["sha256"] for r in parent["files"]}
    paths=[p for folder in (OUT,CAD,ROUTE,BATCH) for p in folder.iterdir() if p.is_file() and not p.name.endswith(".FCBak") and p.name not in ("manifest.json","validation.json")]
    paths += [PARENT/"manifest.json",ROOT/"hardware/reference/servo-holder-p0-2026-09-24/0300330.png"]
    for name in ("body_ground_routes_r1.py","body_ground_bridge_r5.py","body_ground_bridge_finish_r1.py","body_ground_seat_preflight_r5.py","complete_body_ground_bridge_checks_r3.py","body_ground_finish_preview.py","test_body_ground_bridge.py",Path(__file__).name):paths.append(Path(__file__).with_name(name))
    for rel,digest in c["source_sha256"].items():assert sha256(ROOT/rel)==digest;paths.append(ROOT/rel)
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();digest=sha256(p)
        assert rel not in pins or pins[rel]==digest,rel
        pins[rel]=digest
    m=copy.deepcopy(parent);m.update(phase1_percent=70,W5_complete=False,parent_pins_preserved=len(parent["files"]),files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    result=verify(ROOT,m);assert result["integrity_ok"],result
    save(BATCH/"manifest.json",m)
    save(BATCH/"validation.json",dict(integrity=result,parent_pins_preserved=len(parent["files"]),new_STL=1,one_Deck_replacement=True,job_part_quantity_lines_unchanged=True,phase1_percent=70,W5_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent["files"]),phase1_percent=70,new_STL=1,work_wall_seconds=(end-datetime.fromisoformat(START)).total_seconds())))
if __name__=="__main__":main()
