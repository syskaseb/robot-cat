"""Select one supported DATA Deck replacement; preserve every R36 pin."""
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
PARENT=ROOT/"hardware/manufacturing/one-batch-prototype-r36"
BATCH=ROOT/"hardware/manufacturing/one-batch-prototype-r37"
OUT=ROOT/"hardware/electronics/full-cat/body-data-bridges-r7"
CAD=ROOT/"hardware/cad/studies/body-data-bridges-r7"
START="2026-10-01T22:59:16+00:00"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

def main():
    assert not (BATCH/"manifest.json").exists()
    c=read(OUT/"checks.json");b=read(OUT/"current-body-checks.json")
    assert c["status"]=="THREE_DATA_BRIDGES_NOMINAL_COMPLETE" and c["new_STL"]==1
    assert not c["hits"] and not b["hits"] and c["sourced_T18I_thickness_mm"]==1.2
    assert (OUT/"preview.png").is_file(),"Inspect actual preview before invoking packaging"
    # R7 restores the source lane. Do not present R6's intermediate+1.2 as
    # a final displacement. Geometry/slot bounds already checked independently.
    c.update(changed_anchor_y_mm=[0,-2.3],final_builder_sha256=sha256(ROOT/"tools/electronics/body_data_bridges_r7.py"))
    save(OUT/"checks.json",c)
    interface=read(OUT/"interface.json")
    interface["connector_datums"].update(nominal_strip_length_mm=11,
        strip_spec_source=dict(author="WAGO",item="221-415",datasheet_date="2019-12-10",
            url="https://www.wesco.ie/sites/admin/plugins/elfinder/files/fegimewesco/PDFs/Wago/221415.pdf",
            pages_1_based=[2,6],verified_date_utc="2026-10-02",
            current_item_url="https://www.wago.com/gb/installation-terminal-blocks-and-connectors/splicing-connector-with-levers/p/221-415",
            corroboration="Current manufacturer CAD catalogue also reports ABISOLIERLAENGE11 for BESTNR221-415; not the misleading browser slug221-485.",
            dimensions_note="Older WAGO sheet29.9x18.6x8.3 and current CAD29.8x18.3x8.15 are BOTH within the chosen30x19x9 reservation; no supplier cage pitch inferred."))
    interface["assembly"].append("Nominal manufacturer221-415 strip length11mm. Confirm delivered221-415 marking before stripping; do NOT apply the reserve28mm as a strip length.")
    save(OUT/"interface.json",interface)
    tick=time.monotonic();test_start=datetime.now(timezone.utc)
    run=subprocess.run([sys.executable,"-X","utf8","-m","unittest","discover","-s","tools/electronics","-p","test_body_data_bridges_r3.py","-v"],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
    save(OUT/"regression-run.json",dict(start_utc=test_start.isoformat(),measured_seconds=time.monotonic()-tick,
        exit_code=run.returncode,output=run.stdout+run.stderr,physical_pass=False))
    assert run.returncode==0,run.stdout+run.stderr
    parent=read(PARENT/"manifest.json");assert verify(ROOT,parent)["integrity_ok"]
    selection=copy.deepcopy(read(PARENT/"selection.json"));q=copy.deepcopy(read(PARENT/"one-order-quantities.json"))
    entry=next(r for r in selection["prints"] if r["identity"]=="electronics:DeckP10-cover-mount")
    before=copy.deepcopy(entry)
    stl=CAD/"Deck_x1.stl"
    entry.update(stl=stl.relative_to(ROOT).as_posix(),sha256=sha256(stl),
        recipe=(OUT/"interface.json").relative_to(ROOT).as_posix(),
        native=(CAD/"DeckDataBridgesSupported.FCStd").relative_to(ROOT).as_posix(),
        orientation="World+Zup, original lower Deck base on bed. Six integral saddles; PETG/supports/slicer phase2.",
        print_size_mm_including_5mm_brim=[v+10 if i<2 else v for i,v in enumerate(c["dimensions_mm"])])
    assert entry["quantity"]==1
    selection.update(parent_selection_sha256=sha256(PARENT/"selection.json"),phase1_percent=70,W5_complete=False,
        fixed_DATA_bridges=(OUT/"interface.json").relative_to(ROOT).as_posix(),
        fixed_DATA_bridges_sha256=sha256(OUT/"interface.json"),
        replaced_DATA_Deck=before,
        W5_recipe_precedence="R37 fixed DATA interface supersedes W007/W011/W012 legacy nominal route values in the inherited endpoint ledger. All other R36 recipes retained. D_RR/D_RL cage permutations apply to later leg harness design.")
    assert len(selection["prints"])==71 and selection["installed_petg_parts"]==110
    q["selected_prints"]=(BATCH/"selection.json").relative_to(ROOT).as_posix()
    tie=next(r for r in q["lines"] if r["id"]=="tie:111-02370")
    assert tie["installed"]==81 and tie["planning_quantity"]==100
    tie["installed"]=87
    tie["note"]+=" R37 adds six insulation-seat ties for W007/W011/W012, two per stationary DATA bridge. Working installed87 from the same100pc bag. Not yet the final whole-robot K3 census."
    data=next(r for r in q["lines"] if r["id"]=="p0:DATA-BRIDGE-WIRE-P0")
    assert data["planning_quantity"]==7 and data["unit"]=="m"
    data["note"]+=" R37: three200mm blanks (=600mm); actual nominal exposed path lengths in fixed_DATA_bridges interface. Includes28mm cut/strip reserve plus30mm rework allowance. Actual stripping by delivered221-415 marking. Remaining purchase stock stays outside the robot."
    q.update(fixed_DATA_bridges=selection["fixed_DATA_bridges"],fixed_DATA_ties_from_existing_bag100=6)
    assert q["line_count"]==113 and len(q["lines"])==113
    BATCH.mkdir(exist_ok=True)
    save(BATCH/"selection.json",selection);save(BATCH/"one-order-quantities.json",q)
    text=("# R37: trzy stałe mostki DATA z podparciem izolacji\n\n"
        "Jeden zamiennik Deck:12 pełnych otworów na6 opasek i6 integralnych siodełek, "
        "bez osobnych nowych części. Zachowane otwory/wycięcia R36, w tym okno wentylatora. "
        "71zadań/110PETG/4próbki,113wierszy ilości.\n\n"
        "W007:D_FL.5→D_FR.1;W011:D_FR.5→D_RR.1;W012:D_RR.5→D_RL.1. "
        "W011 przechodzi5mm nad XA05 dwoma łukamiS R5,2. D_RR:logicznyport1 "
        "w środkowej komorze;port3 w lewej. D_RL zachowuje pierwotne role; pozostałe według interface.json. "
        "Wszystkie komory DATA na jednym potencjale; nie pomylić z P/G. "
        "Pozycje komór są nominalne, nie fizyczny pomiar.\n\n"
        "Trzy200mm blanki LiY4126002S ze wspólnego zakupu7m. "
        "Dokładne nominalne długości tras w interface.json;28mm rezerwy cięcia i30mm na poprawkę. "
        "28mm NIE jest instrukcją odizolowania:nominalnie11mm według WAGO221-415, potwierdzić oznaczenie dostawy. "
        "Stały LiY nie zastępuje ruchomej wiązki nóg.\n\n"
        "T18I111-02370:2,5×1,2mm;główka4,8×4,5×3,5mm. "
        "Sześć opasek przełożyć przed elektroniką, potem osadzić izolację w siodełkach "
        "i ręcznie dociągnąć bez zgniatania. Główki pod Deck; dostęp po odłączeniu źródła. "
        "Nie dociskać dźwigni/styków WAGO. Przy demontażu opaski przeciąć i wymienić. "
        "87roboczych z istniejącego100szt; cały K3 nadal otwarty.\n\n"
        "R1–R6 diagnostyczne, niewybrane. R4 wykazał trafienie0,010902mm³ paska1,2mm w XA05; R5 kolizję z P0Support3 i odwrócenie unsigned-prostokąta. R6 wykazał kolizję przesuniętej opaski z P0Support2. R7 zachowuje komory i trasy: północna kotwaY24, źródłowaY−29 z jednym krótszym siodełkiem2,5mm. Pozostałe pięć4mm. Wszystkie prostokąty mają kierunkowe wymiary. R3 trafiał w stary uncięty Deck_DESIGN "
        "z cache Pi, nie w nową płytę. R37 sprawdza właściciela aktualnego i pasek1,2mm, "
        "zamiast uznawać te trafienia za fizyczny PASS.\n\n"
        "70%=14/20,+0pp. E3/W5/K2/K3/A2/A3 nadal OPEN. "
        "Pozostały pozostałe przewody zasilania/źródła,12ruchomych wiązek nóg i balans. "
        "Dostawa/PETG/slicer/pasowania/elektryka to faza2. Bez fizycznegoPASS.\n")
    (BATCH/"README.md").write_text(text,encoding="utf-8",newline="\n")
    (OUT/"README.md").write_text(text,encoding="utf-8",newline="\n")
    end=datetime.now(timezone.utc)
    save(OUT/"work-time.json",dict(start_utc=START,end_utc=end.isoformat(),
        wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        kind="Instructions/current-source construction, three DATA routes, six diagnostic revisions, full six restraints/supports, native/export/changed-current owners/regression/package",
        separately_measured_phases=False,wall_time_includes_user_interruptions=True,
        active_robot_work_seconds=None,new_STL=1,replacement_STL=True,W5_complete=False,physical_pass=False))
    pins={r["path"]:r["sha256"] for r in parent["files"]}
    paths=[p for folder in (OUT,CAD,BATCH,ROOT/"hardware/electronics/full-cat/body-data-bridges-r3")
        for p in folder.iterdir() if p.is_file() and not p.name.endswith(".FCBak") and p.name not in ("manifest.json","validation.json")]
    paths += [ROOT/"hardware/cad/studies/body-data-bridges-r3/DeckDataBridges.FCStd",PARENT/"manifest.json"]
    paths += [ROOT/"hardware/cad/studies/body-data-bridges-r4/DeckDataBridgesSupported.FCStd",
        ROOT/"hardware/electronics/full-cat/body-data-bridges-r4/checks.json",
        ROOT/"hardware/electronics/full-cat/body-data-bridges-r4/current-body-checks.json"]
    paths += [ROOT/"hardware/cad/studies/body-data-bridges-r6/DeckDataBridgesSupported.FCStd",
        ROOT/"hardware/electronics/full-cat/body-data-bridges-r6/checks.json",
        ROOT/"hardware/electronics/full-cat/body-data-bridges-r6/interface.json",
        ROOT/"hardware/electronics/full-cat/body-data-bridges-r6/current-body-checks.json"]
    paths += [ROOT/"hardware/electronics/full-cat/body-data-bridges-r5"/n
              for n in ("checks.json","interface.json","current-body-checks.json")]
    for n in ("body_data_bridges_r1.py","body_data_bridges_r2.py","body_data_bridges_r3.py","body_data_bridges_r4.py",
        "body_data_bridges_r5.py","body_data_bridges_r6.py","body_data_bridges_r7.py","body_data_bridges_current_check.py","body_data_bridges_preview.py","test_body_data_bridges_r3.py",Path(__file__).name):paths.append(Path(__file__).with_name(n))
    for rel,h in b["source_sha256"].items():
        assert sha256(ROOT/rel)==h;paths.append(ROOT/rel)
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();digest=sha256(p)
        assert rel not in pins or pins[rel]==digest,rel
        pins[rel]=digest
    manifest=copy.deepcopy(parent);manifest.update(phase1_percent=70,W5_complete=False,parent_pins_preserved=len(parent["files"]),
        files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    result=verify(ROOT,manifest);assert result["integrity_ok"],result
    save(BATCH/"manifest.json",manifest)
    save(BATCH/"validation.json",dict(integrity=result,parent_pins_preserved=len(parent["files"]),
        new_STL=1,one_Deck_replacement=True,job_part_quantity_lines_unchanged=True,
        phase1_percent=70,W5_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent["files"]),phase1_percent=70,new_STL=1,work_wall_seconds=(end-datetime.fromisoformat(START)).total_seconds())))

if __name__=="__main__":main()
