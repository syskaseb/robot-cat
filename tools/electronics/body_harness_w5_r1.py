"""One physical-conductor/termination ledger for the remaining P0 harness.

Read-only inputs: selected R35, E4 and historical P0 labels. No CAD changes,
hardware I/O, purchases, inferred delivered AWG or invented routing PASS.
"""
import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/electronics/full-cat/body-harness-w5-r1"
P0 = "hardware/electronics/power-platform/"
E4 = "hardware/electronics/full-cat/connection-map-e4-r1/netlist.json"
PI = "hardware/electronics/full-cat/pi-interface-final-r2/wiring-card.json"
PARENT = ROOT / "hardware/manufacturing/one-batch-prototype-r35"
BATCH = ROOT / "hardware/manufacturing/one-batch-prototype-r36"
START = datetime.fromisoformat("2026-10-01T22:41:52+00:00")
SOURCES = [P0 + n for n in ("wiring-p0.json", "p0-routes.json",
    "servo-terminations-p0.json", "switch-terminations-p0.json",
    "MAIN-INPUT-P0.md", "DATA-HARNESS-P0.md", "BATTERY-INLET-P0.md")]
SOURCES += [E4, PI,
    "hardware/reference/power-distribution-2026-09-23/README.md",
    "hardware/reference/p0-kit-2026-09-25/SIGNAL-CABLES.md",
    "hardware/manufacturing/one-batch-prototype-r28/head-local-interface.json",
    "hardware/manufacturing/one-batch-prototype-r29/tail-wiring-interface.json"]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def termination(endpoint, blocks):
    block, _, pin = endpoint.rpartition(".")
    if block in blocks:
        sku = blocks[block]["sku"]
        return dict(method="bare_stranded_copper_one_per_port", sku=sku,
            strip_mm=[12, 14] if sku == "221-615" else None,
            strip_rule="221-615:12–14mm;221-415:marking on delivered housing",
            copper_range_mm2=[.5, 6] if sku == "221-615" else [.14, 4],
            tin_allowed=False, double_wire_allowed=False,
            source=P0+"CENTRAL-HARNESS-P0.md")
    if re.fullmatch(r"(FL|FR|RL|RR)[123]\.[VDG]", endpoint):
        return dict(method="preserve_factory_servo_end_5264_keyed",
            sku="included lead of Waveshare22414 ST3215 12V",
            role=pin, do_not_assign_left_right_cavities=True,
            second_parallel_socket="NC", delivered_wire_mm2=None,
            source=P0+"DATA-HARNESS-P0.md")
    if re.fullmatch(r"F_(FL|FR|RL|RR)[123]\.(in|out)", endpoint):
        if pin == "in":
            return dict(method="fully_insulated_FASTON_crimp",
                sku="TE4-520448-2", wire_sku="LAPP0107001 AWG12",
                tools=["TE69710-1", "TE224027-2"], strip_mm=[7.54, 8.30],
                marking="red + at BOTH ends of black AWG12",
                source=P0+"servo-terminations-p0.json")
        return dict(method="fully_insulated_FASTON_crimp_conditional_factory_wire",
            sku="TE2-520184-2", copper_range_mm2=[.32, .82],
            tool="TE58628-1", delivered_wire_mm2=None,
            condition="Check actual copper/insulation; no fold/tinning/strand removal",
            source=P0+"servo-terminations-p0.json")
    if re.fullmatch(r"F_(FL|FR|RL|RR)\.(in|out)", endpoint):
        return dict(method="preserve_inline_holder_factory_lead",
            sku="MTA0100335", nominal_mm2=4,
            source=P0+"LEG-HARNESS-P0.md")
    if endpoint in ("F0.in", "F0.out", "F_PI.in", "F_PI.out"):
        return dict(method="preserve_inline_holder_factory_lead",
            sku="FHAC0002ZXJ" if endpoint.startswith("F0.") else "FHAC0001ZXJ",
            nominal_awg=12 if endpoint.startswith("F0.") else 16,
            source=P0+"WIRING-P0.md")
    if endpoint.startswith("S1."):
        return dict(method="insulated_ring_crimp_under_original_switch_screw",
            sku="TE130171", tool="TE58433-3 chamber Y",
            strip_mm=[7.94, 8.73], screw="original NKK S821 M4.5; not an M5 replacement",
            source=P0+"switch-terminations-p0.json")
    if endpoint.startswith("S0."):
        return dict(method="insulated_ring_crimp_under_original_switch_terminal",
            sku="TE130207", tool="TE58433-3 chamber Y",
            source=P0+"switch-terminations-p0.json")
    if endpoint in ("BAT.plus", "BAT.minus"):
        return dict(method="solder_to_robot_side_XT60_marked_polarity",
            sku="AMASS XT60H-M Kamami581961", strip_mm=None,
            must_disconnect_battery=True, battery_factory_plug_unchanged=True,
            source=P0+"BATTERY-INLET-P0.md")
    if endpoint.startswith("BUS."):
        return dict(method="preserve_factory_34171_connector_remove_V_contact",
            sku="Waveshare34171 one300mm cable", role=pin,
            physical_adapter_pad="H3.1" if pin == "D" else "H3.3",
            delivered_wire_mm2=None, source=P0+"ADAPTER-PIGTAIL-P0.md")
    if endpoint.startswith("SPLICE_PI."):
        return dict(method="single_insulated_16_to_18AWG_solder_joint",
            joint_id="MAIN_INPUT_SPLICE", tools=["soldering_station"],
            strain_relief="both intact insulation sides; no solder neck bending",
            source=P0+"MAIN-INPUT-P0.md")
    if endpoint.startswith("MAIN."):
        return dict(method="direct_solder_to_named_large_MAIN_pad",
            sku="Pololu4853", role="GND" if "GND" in pin else pin,
            strip_mm=5 if pin in ("VOUT", "GND_OUT") else None,
            supplied_2444_terminal_blocks="NOT installed",
            source=PI if pin in ("VOUT", "GND_OUT") else P0+"MAIN-INPUT-P0.md")
    if endpoint.startswith("PI_USB_C."):
        return dict(method="preserve_shared_factory_USB_C_power_plug",
            sku="JoyIT K1474 EAN4250236828305", cable_id="K1474_PI_POWER",
            source=PI)
    raise ValueError("Unassigned termination: " + endpoint)


def build():
    base, routes, pi = read(P0+"wiring-p0.json"), read(P0+"p0-routes.json"), read(PI)
    blocks = {b["id"]: b for b in base["blocks"]}
    groups = {wire: g for g in routes["groups"] for wire in g["wires"]}
    rows = []
    for w in base["wires"]:
        g = groups[w["id"]]
        row = dict(id=w["id"], a=w["a"], b=w["b"], net=w["net"],
            group=g["id"], material=g["material"], route_policy=g["method"],
            route_intent=g["note"], current_R35_route_checked=False,
            legacy_nominal_mm=g.get("nominal_mm", {}).get(w["id"]),
            limit_mm=w.get("design_max_length_mm", g.get("limits", {}).get(w["id"])),
            actual_cut_mm=None, source_labels=P0+"wiring-p0.json",
            ends=[termination(w["a"], blocks), termination(w["b"], blocks)])
        if w["id"] in ("W079", "W080"):
            row.update(material=pi["power"]["cable"], shared_cable_id="K1474_PI_POWER",
                legacy_nominal_mm=None, limit_mm=None,
                nominal_cut_bound_mm=pi["power"]["nominal_cut_bound_mm"],
                current_R35_route_checked=True, route_source=PI,
                override="Old250mm maximum superseded by selected R33 power route.")
        if w["id"] == "W060":
            row.update(material="black18AWG leftover of SAME K1474", limit_mm=300,
                shared_stock_id="K1474_1000mm", current_R35_route_checked=False)
        if w["id"] == "W078":
            row.update(material="red18AWG leftover of SAME K1474",
                shared_stock_id="K1474_1000mm")
        if w["id"] in ("W079", "W080"):
            row["shared_stock_id"] = "K1474_1000mm"
        if g["id"] == "MOVING_SERVO_LOOMS":
            row["harness_id"] = next(e.split(".")[0] for e in (w["a"], w["b"])
                if re.fullmatch(r"(FL|FR|RL|RR)[123]\.[VDG]", e))
            row["route_policy"] = "retain_factory_servo_plug_then_cut_after_full_range_dry_fit"
        rows.append(row)
    return dict(schema_version=1, parent="R35", W5_complete=False,
        phase1_percent=70, physical_pass=False, new_STL=0,
        scope="80 P0 conductor labels /160 end recipes; not80 bought cables or E4 graph rows",
        conductors=rows,
        already_selected_interfaces=dict(Pi=PI,
            head=SOURCES[-2], tail=SOURCES[-1],
            PWM="hardware/electronics/full-cat/pwm-complete-e2-r1/interface.json",
            fixed_aux="R19/R20 selected in R35, no replacement"),
        shared_items=dict(K1474="ONE1000mm two-conductor cable, not4cables",
            BUS="ONE34171 cable for W002/W003; V removed, five kit cables spare",
            MAIN_INPUT_SPLICE="ONE solder joint for W077/W078, not2 bought connectors",
            G1_G2="ONE W061 physical bridge; E4 reciprocal rows are not2 wires",
            legs="12 factory three-conductor harnesses, not36 three-conductor cables"),
        balance=dict(roles={"BAT.B0": "P309.minus", "BAT.B1": "P309.1S",
                "BAT.B2": "P309.2S", "BAT.B3": "P309.3S"},
            exact_GTech_cavity_mapping=None, ID_contact="NEVER connect to cell input",
            live_with_S0_off=True, route_checked=False,
            blocker="Exact delivered GEA223S30X6GT tap/ID interface not assigned"),
        open_design=[
            "Current R35 Deck/cover body routing and restraint datums for38 nonmoving nonPi conductors",
            "12 leg harnesses: whole chosen joint range, anchors, stock length and route-to-fuse/body",
            "Battery/F0/S0 restraint, alarm mount and balance physical interface",
            "Factory ST/BUS wire section: no evidence it meets selected FASTON/WAGO; conditional recipe only",
            "Final stock/installed lengths and insulation/tie ledger for K3; E3 protection remains separate"],
        source_bindings={p: sha(ROOT/p) for p in SOURCES})


def validate(data):
    expected = build()
    if data != expected:
        raise ValueError("Conductor recipes differ from pinned selected inputs")
    rows = data["conductors"]
    if len(rows) != 80 or len({w["id"] for w in rows}) != 80:
        raise ValueError("P0 label missing/duplicated")
    by_id = {w["id"]: w for w in rows}
    moving = [w for w in rows if "harness_id" in w]
    harnesses = sorted({w["harness_id"] for w in moving})
    assert len(moving) == 36 and len(harnesses) == 12
    assert all(sum(w.get("harness_id") == h for w in moving) == 3 for h in harnesses)
    assert by_id["W079"]["nominal_cut_bound_mm"] == by_id["W080"]["nominal_cut_bound_mm"]
    assert by_id["W079"]["nominal_cut_bound_mm"] > 250
    # E4 correspondence is role-to-role, not duplicate physical graph entries.
    from connection_map_e4_r1 import component
    net = read(E4)
    edges = copy.deepcopy(net["edges"])
    for alias, ports in read(P0+"wiring-p0.json")["resolved_aliases"].items():
        edges.extend(dict(a=alias, b=p) for p in ports)
    for w in rows:
        if w["id"] in ("W077", "W078"):
            continue  # One E4 functional wire PI_VIN represents both physical segments.
        a = "PI.USB_C.V" if w["a"] == "PI_USB_C.VBUS" else w["a"]
        b = {"PI_USB_C.VBUS":"PI.USB_C.V", "PI_USB_C.GND":"PI.USB_C.G",
             "MAIN.GND_OUT":"MAIN.GND"}.get(w["b"], w["b"])
        a = {"MAIN.GND_OUT":"MAIN.GND"}.get(a, a)
        if b not in component(edges, a):
            raise ValueError("E4 conductor role mismatch: " + w["id"])
    assert "MAIN.VIN" in component(edges, "F_PI.out")
    return dict(conductors=80, end_recipes=160, moving_conductors=36,
        factory_leg_harnesses=12, physical_graph_rows_not_purchase_counts=True,
        current_route_checked=sum(w["current_R35_route_checked"] for w in rows),
        inherited_Pi_route_only=True, W5_complete=False, phase1_percent=70,
        E3_complete=False, new_STL=0, physical_pass=False,
        checks="Coverage, role correspondence, shared-stock accounting, conditional endpoints; no CAD clearance PASS")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--package", action="store_true")
    args=parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    save(OUT/"plan.json", dict(start_utc=START.isoformat(), parent="R35",
        scope="Body/leg harness complete endpoint ledger, W5 remains open", new_STL=0))
    data=build()
    checks=validate(data)
    save(OUT/"interface.json", data)
    save(OUT/"checks.json", checks)
    test_start=datetime.now(timezone.utc); tick=time.monotonic()
    run=subprocess.run([sys.executable,"-m","unittest","discover","-s",
        "tools/electronics","-p","test_body_harness_w5_r1.py","-v"],
        cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
    save(OUT/"regression-run.json",dict(start_utc=test_start.isoformat(),
        measured_seconds=time.monotonic()-tick,exit_code=run.returncode,
        output=run.stdout+run.stderr,physical_pass=False))
    if run.returncode:
        raise RuntimeError("W5 ledger regression failed; not packaging")
    with (OUT/"wire-ends.csv").open("w", newline="", encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["label","a","b","group","material","legacy_nominal_NOT_verified_mm",
            "selected_cut_bound_mm","limit_mm","method_a","sku_a","method_b","sku_b",
            "harness_or_shared_cable","route_checked"])
        for w in data["conductors"]:
            writer.writerow([w["id"],w["a"],w["b"],w["group"],w["material"],
                w["legacy_nominal_mm"],w.get("nominal_cut_bound_mm"),w["limit_mm"],
                w["ends"][0]["method"],w["ends"][0].get("sku"),
                w["ends"][1]["method"],w["ends"][1].get("sku"),
                w.get("harness_id",w.get("shared_cable_id","")),w["current_R35_route_checked"]])
    (OUT/"README.md").write_text(
        "# Wiązka korpusu/nóg W5: jedna karta wykonawcza\n\n"
        "80 etykiet przewodów,160 recept zakończeń. Zachowane W001–W080; "
        "36 żył nóg oznacza12 wiązek, nie36 kabli. W002/W003 to jeden34171, "
        "W079/W080 jeden K1474. W077/W078 to dwa odcinki przy JEDNYM lutowanym przejściu. "
        "W061 to jeden mostek G1–G2, mimo dwóch kierunkowych wierszy E4.\n\n"
        "Wybrany R33/R35 unieważnia stare250mm W079/W080: aktualna granica "
        "nominalna290,249mm plus fabryczny wtyk według karty Pi, nie nowy pomiar. "
        "Nie ciąć przewodu Pi według starego WIRING-P0. Jeden1m K1474 nadal obejmuje "
        "oba wyjściowe przewody oraz resztę na wejście/powrót MAIN.\n\n"
        "Zakończenia WAGO: jedna niecynowana linka na port; "
        "615=12–14mm,415 zgodnie z oznaczeniem dostarczonej obudowy. "
        "S1:TE130171;S0:TE130207;12 wejść oprawek:TE4-520448-2/AWG12, "
        "12 wyjść:TE2-520184-2 tylko jeśli fabryczna linka/izolacja mieści się "
        "w zakresie. Nie zaginać żył podwójnie, nie wycinać drucików. "
        "Luty i zaciski wykonywać na odłączonych modułach przed zamocowaniem. "
        "Odciążać izolację, nie usztywniony lut.\n\n"
        "Dostępne końcówki nie dowodzą trasy ani dostępu narzędzia. "
        "Historyczne nominały mostków są w osobnej kolumnie, NIE zatwierdzone "
        "dla obecnego Deck/E6. Ciąć dopiero po trasie i zapasie ruchu; "
        "zapas zakupowy zostaje poza kotem. Drugie gniazdo każdego ST puste, "
        "nie dodawać mostka V/G do następnego serwa. BUS.H3V usunięty; "
        "nie używać niebieskiego stałego LiY jako ruchomego kabla łapy.\n\n"
        "G-Tech: przypisane tylko role B0/B1/B2/B3→minus/1S/2S/3S P309. "
        "Styk ID nie jest odczepem celi; nie wybierać pinów ze zdjęcia. "
        "Alarm pozostaje zasilony przy S0 OFF. Dokładny interfejs i trasa "
        "nadal otwarte, nie ma zgody na podłączanie.\n\n"
        "W5 nadal OPEN: rzeczywiste wybrane trasy korpusu/nóg, odciążenia, "
        "długości i balans. Pi/głowa/ogon/PWM zachowane, nie projektowane ponownie. "
        "70%=14/20,+0pp.0nowychSTL, brak fizycznego PASS.\n",
        encoding="utf-8")
    save(OUT/"work-time.json", dict(start_utc=START.isoformat(),
        end_utc=(end:=datetime.now(timezone.utc)).isoformat(),
        wall_seconds=(end-START).total_seconds(), kind="W5 body/leg endpoint consolidation",
        separately_measured_phases=False, new_STL=0, physical_pass=False))
    if args.package:
        sys.path.insert(0, str(ROOT/"tools/cad"))
        from release_check import verify
        parent=read(PARENT.relative_to(ROOT)/"manifest.json")
        assert verify(ROOT,parent)["integrity_ok"]
        BATCH.mkdir(exist_ok=True)
        selection=copy.deepcopy(read(PARENT.relative_to(ROOT)/"selection.json"))
        quantities=copy.deepcopy(read(PARENT.relative_to(ROOT)/"one-order-quantities.json"))
        selection.update(parent_selection_sha256=sha(PARENT/"selection.json"),
            phase1_percent=70,W5_complete=False,body_harness=(OUT/"interface.json").relative_to(ROOT).as_posix(),
            body_harness_sha256=sha(OUT/"interface.json"))
        quantities["selected_prints"]=(BATCH/"selection.json").relative_to(ROOT).as_posix()
        save(BATCH/"selection.json",selection);save(BATCH/"one-order-quantities.json",quantities)
        (BATCH/"README.md").write_text("# R36: karta końców wiązki W5\n\n"
            "Wybrany R35 zachowany bez zmian CAD/STL/ilości. "
            "70%=14/20, W5/E3/K2/K3/A2/A3 nadal OPEN. "
            "W5:80przewodów/160końców i wspólny zakup kabli bez duplikacji. "
            "Metadane procentu ujednolicone: R35 miał historyczne65% w manifeście, "
            "mimo E4 i14/20 w planie.0nowychSTL, brak fizycznegoPASS.\n",encoding="utf-8")
        pins={x["path"]:x["sha256"] for x in parent["files"]}
        deps=[ROOT/p for p in SOURCES]+[Path(__file__),
            Path(__file__).with_name("test_body_harness_w5_r1.py"),PARENT/"manifest.json"]
        deps += [p for folder in (OUT,BATCH) for p in folder.iterdir()
            if p.is_file() and p.name not in ("manifest.json","validation.json")]
        for p in deps:
            name=p.relative_to(ROOT).as_posix(); digest=sha(p)
            assert name not in pins or pins[name]==digest,name
            pins[name]=digest
        manifest=copy.deepcopy(parent)
        manifest.update(phase1_percent=70,W5_complete=False,parent_pins_preserved=len(parent["files"]),
            files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
        result=verify(ROOT,manifest);assert result["integrity_ok"]
        save(BATCH/"manifest.json",manifest)
        save(BATCH/"validation.json",dict(integrity=result,new_STL=0,
            parent_pins_preserved=len(parent["files"]),all_prints_and_quantities_unchanged=True,
            print_ready_denied=not verify(ROOT,manifest,True)["integrity_ok"],physical_pass=False))
        checks["package_pins"]=len(pins)
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
