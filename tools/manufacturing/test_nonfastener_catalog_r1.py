import copy
import unittest
from nonfastener_catalog_r1 import ROOT, PARENT, SUPPORT, read, bind, consolidate, validate_current_roles

def base_quantities():
    return read((PARENT/'one-order-quantities.json').relative_to(ROOT))

def test_all_83_roles_have_exact_identity_or_generic_offer(q):
    bindings=bind(q)
    assert len(bindings)==83
    assert all(r['manufacturer_part'] or r['supplier_url'] for r in bindings)

def test_wago_all_four_roles_merge_without_quantity_or_source_loss(q):
    out=consolidate(q,bind(q))
    r=next(r for r in out if r['id']=='supplier:Kamami:1188363')
    assert r['planning_quantity']==16
    assert sorted(x['planning_quantity'] for x in r['roles'])==[1,3,4,8]
    assert len(out)==109
    assert all(x['source'] for x in r['roles'])

def test_WAGO_wrong_variant_not_merged(q):
    bindings=bind(q)
    next(r for r in bindings if r['quantity_id']=='p0:DISTRIBUTION-LEGS-P0')['manufacturer_part']='221-615'
    with unittest.TestCase().assertRaises(AssertionError):
        consolidate(q,bindings)

def test_missing_role_fails(q):
    q['lines'].append(dict(id='unknown:new-part',source='none',planning_quantity=1,unit='pcs'))
    with unittest.TestCase().assertRaises(AssertionError):
        bind(q)

def test_minival_are_active_not_obsolete(q):
    out=validate_current_roles(q,read(SUPPORT[10]))
    assert out['active_minival_holders']==4 and not out['removed_roles']

def test_missing_active_fuse_rejected(q):
    n=copy.deepcopy(read(SUPPORT[10]))
    n['fuses']=[r for r in n['fuses'] if r['ref']!='F_RR']
    with unittest.TestCase().assertRaises(AssertionError):
        validate_current_roles(q,n)

def test_fuse_quantity_shortfall_rejected(q):
    next(r for r in q['lines'] if r['id']=='p0:FUSES')['planning_quantity']=3
    with unittest.TestCase().assertRaises(AssertionError):
        validate_current_roles(q,read(SUPPORT[10]))

def test_generic_SD_and_kit_do_not_invent_maker(q):
    by={r['quantity_id']:r for r in bind(q)}
    assert by['p0:SD']['manufacturer'] is None
    assert by['p0:SD']['supplier_sku']=='1188166'
    assert by['p0:HEATSHRINK']['supplier_sku']=='5375'

def test_factory_crimp_preserved_not_replaced_by_loose_contacts(q):
    by={r['quantity_id']:r for r in bind(q)}
    assert by['connector:2147612113']['manufacturer_part']=='2147612113'
    assert 'supplier_constraint' in by['connector:2147612113']
    assert 'connector:430300007' not in by

def test_fixed_offers_unmodified(q):
    out=consolidate(q,bind(q))
    assert [r for r in out if r['id'].startswith('supplier:') and r['id']!='supplier:Kamami:1188363']==[r for r in q['lines'] if r['id'].startswith('supplier:')]

def test_piece_pack_and_meter_quantities_not_recombined(q):
    by={r['quantity_id']:r for r in bind(q)}
    assert by['Pi:GPIO_brown_1871']['planning_quantity']==2
    assert by['Pi:GPIO_brown_1871']['pack_contents']==5
    assert by['p0:PI-POWER-CABLE']['planning_quantity']==1
    assert by['wire:fixed:Donau-118-0']['unit']=='roll10m'

def test_known_offers_reused_without_variant_change(q):
    by={r['quantity_id']:r for r in bind(q)}
    assert by['wire:HELU23301:black']['supplier_sku']=='SIF0.50-B'
    assert by['tie:111-02370']['supplier_sku']=='T18I-PA66-BK'
    assert by['splice:WAGO221-412']['manufacturer_part']=='221-412'
    assert by['wire:fixed:Donau-118-3']['unit']=='roll10m'

def load_tests(loader, tests, pattern):
    suite=unittest.TestSuite()
    for name, function in sorted(globals().items()):
        if name.startswith('test_') and callable(function):
            suite.addTest(unittest.FunctionTestCase(
                lambda function=function: function(base_quantities()), description=name))
    return suite

if __name__=='__main__':
    unittest.main()
