"""Cheap contract checks; no FreeCAD, printer, or powered hardware."""
import copy
import json
import math
from pathlib import Path
import unittest
from open_prototype_layout import assign_group, endpoint_plan, factory_splice_budget, CORRIDORS

BASE=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2'


def fixture():
    graph=json.loads((BASE/'whole-harness-board-plan.json').read_text(encoding='utf-8'))
    mount=json.loads((BASE/'neck-support/main-mount-sequence/checks.json').read_text(encoding='utf-8'))
    return graph,mount


def assert_close(actual, expected):
    if isinstance(expected, list):
        assert len(actual)==len(expected)
        assert all(math.isclose(a,b,abs_tol=1e-7) for a,b in zip(actual,expected))
    else:
        assert math.isclose(actual,expected,abs_tol=1e-7)


def test_identity_and_sources_preserved():
    graph,mount=fixture();baseline=copy.deepcopy(graph)
    datums,rows=endpoint_plan(graph,mount,[-19,-28,42],True)
    assert graph==baseline
    assert len(rows)==80 and len({r['id'] for r in rows})==80
    assert [(r['id'],r['a'],r['b'],r['net'],r['material']) for r in rows]==[
        (r['id'],r['a'],r['b'],r['net'],r['material']) for r in graph['body_conductors']]
    assert sum(r['bound_end_count'] for r in rows)==122
    assert all(r['corridor_group'] in CORRIDORS for r in rows)
    assert all(r['actual_cut_mm'] is None for r in rows)
    assert datums['SPLICE_PI.16']['point_mm']==datums['SPLICE_PI.18']['point_mm']


def test_pi_translation_is_datum_not_box_centre():
    graph,mount=fixture()
    first,_=endpoint_plan(graph,mount,[-19,-28,42],True)
    shifted,_=endpoint_plan(graph,mount,[-31,-28,43],True)
    assert_close(first['PI_USB_C.VBUS']['point_mm'],[-9.4,-53,45.2])
    assert_close(first['PI_USB_C.GND']['point_mm'],[-12.6,-53,45.2])
    assert_close(shifted['PI_USB_C.VBUS']['point_mm'],[-21.4,-53,46.2])
    with unittest.TestCase().assertRaises(AssertionError):endpoint_plan(graph,mount,[-19,-28,42],False)


def test_main_neck_shift_propagates():
    graph,mount=fixture();datums,rows=endpoint_plan(graph,mount,[-19,-28,42],True)
    row=next(r for r in rows if r['id']=='W078')
    point=next(e['point_mm'] for e in row['ends'] if e['role']=='MAIN.VIN')
    assert_close(point,[-38.18,21.289,48.0948])
    assert not any('MAIN' in e['role'] and e.get('route_restraint_and_lever_qualified',False)
                   for r in rows for e in r['ends'])
    assert_close(math.dist(datums['MAIN.VOUT']['point_mm'],datums['MAIN.GND_OUT']['point_mm']),3.5)


def test_factory_minimum_not_100mm():
    budget=factory_splice_budget([-24,41.25,53],[-38.18,94,53])
    assert 0<budget['available_margin_mm']<15
    assert budget['including_8mm_strip_mm']<84.5
    assert budget['static_clearance_checked'] is False


GROUP_CASES=[
    (['F_FL.in','P_FRONT.2'],'FL'),(['F_FR.out','FR_P.1'],'FR'),
    (['F_RL1.out','RL1.V'],'RL'),(['RR_G.1','G2.3'],'RR'),
    (['F_PI.out','SPLICE_PI.16'],'MAIN_PI'),(['BAT.plus','F0.in'],'SOURCE_SWITCH'),
    (['AUX.GND','G_AUX.2'],'LOGIC_AUX'),(['C_TY.GND','G_TAIL.2'],'TAIL'),
    (['C_HP.GND','LOCAL.GND'],'HEAD'),(['BUS.D','D_FL.1'],'FL')]


class ContractTests(unittest.TestCase):
    test_identity=staticmethod(test_identity_and_sources_preserved)
    test_pi=staticmethod(test_pi_translation_is_datum_not_box_centre)
    test_main=staticmethod(test_main_neck_shift_propagates)
    test_factory=staticmethod(test_factory_minimum_not_100mm)


for index,(roles,group) in enumerate(GROUP_CASES):
    def check(self, roles=roles, group=group):
        self.assertEqual(assign_group(roles),group)
    setattr(ContractTests,'test_group_%02d'%index,check)


if __name__=='__main__':unittest.main()
