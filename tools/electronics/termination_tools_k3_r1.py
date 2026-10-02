"""Concrete reusable tooling requirements, not purchases or sample PASS."""
from pathlib import Path
from datetime import datetime,timezone
import math,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/termination-tools-k3-r1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cma(mm2):return 4*mm2/(math.pi*.0254**2)
def within_table(mm2,target):return target*.95<=cma(mm2)<=target*1.05
def matrix():
    return dict(status='CATALOG_TOOLING_REQUIREMENTS_NOT_PURCHASE_OR_PHYSICAL_APPROVAL',
        parent='one-batch-prototype-r41',phase1_complete=False,K3_complete=False,W5_complete=False,physical_pass=False,
        tools=[
            dict(sku='69710-1',manufacturer='TE Connectivity',quantity_required=1,kind='frame',used_by=['4-520448-2 IN ×12'],requires=['224027-2']),
            dict(sku='224027-2',manufacturer='TE Connectivity',quantity_required=1,kind='12AWG die',used_by=['4-520448-2 IN ×12'],requires=['69710-1']),
            dict(sku='58628-1',manufacturer='TE Connectivity',quantity_required=1,kind='complete hand tool',used_by=['2-520184-2 OUT ×12 conditional on delivered wire']),
            dict(sku='58433-3',manufacturer='TE Connectivity',quantity_required=1,kind='complete frame354940-1 with die58423-1',used_by=['130171 S1 ×4','130207 S0 ×2'],included=['58423-1'])],
        no_additional_die_purchase=['58423-1 already included in58433-3','224027-1 AWG10 not used'],
        processes=[
            dict(terminal='4-520448-2',ends=12,wire='LAPP0107001 single12AWG3.31mm2',tool='69710-1 +224027-2',
                 strip_mm=[7.54,8.30],CMA_target=6500,CMA_tolerance_fraction=.05,wire_area_nominal_mm2=3.31,
                 wire_area_CMA_nominal=cma(3.31),table_range_nominal_consistent=within_table(3.31,6500),
                 maximum_insulation_guide_mm=8.13,guide_is_not_grip_qualification=True,
                 source='hardware/reference/servo-holder-p0-2026-09-24/114-2123-current-TE.pdf',page=10,revision='K8/21SEP2026'),
            dict(terminal='2-520184-2',ends=12,wire='Delivered ST3215 factory positive; actual copper/OD unverified',tool='58628-1',
                 strip_single_mm=[6.76,7.52],source='hardware/reference/servo-holder-p0-2026-09-24/114-2123-current-TE.pdf',page=9,
                 single_wire_CMA_rows=[700,1000,1600],table_AWG_labels=[22,20,18],CMA_tolerance_fraction=.05,
                 maximum_insulation_guide_mm=3.43,guide_is_not_grip_qualification=True,
                 prior_AWG22_area_assumption_mm2=.326,prior_assumption_CMA=cma(.326),
                 prior_assumption_within700CMA_row=within_table(.326,700),
                 condition='Tool/terminal family match is catalogued. Do not equate nominal AWG22/.326mm2 with measured700CMA±5%; confirm actual delivered copper and insulation/sample. No fake acceptance.',
                 delivered_wire_qualified=False),
            dict(terminal='130171',ends=4,wire='HELU23802 red4mm2, nominalOD4.2',tool='58433-3',die='58423-1',cavity='Y',
                 strip_mm=[7.94,8.73],tool_wire_area_mm2=[2.62,6.64],tool_insulation_OD_max_mm=6.35,
                 source='hardware/reference/manual-stop-p0-2026-09-24/408-9252-N.pdf',pages=[1,2,3],
                 exact_terminal_evidence='hardware/reference/manual-stop-p0-2026-09-24/PIDG-QRG.pdf',evidence_page=5),
            dict(terminal='130207',ends=2,wire='S0 outputHELU23802 and F0 factory12AWG; factoryOD unknown',tool='58433-3',die='58423-1',cavity='Y',
                 strip_mm=[7.94,8.73],tool_wire_area_mm2=[2.62,6.64],tool_insulation_OD_max_mm=6.35,
                 source='hardware/reference/manual-stop-p0-2026-09-24/408-9252-N.pdf',pages=[1,2,3],
                 exact_terminal_evidence='hardware/reference/manual-stop-p0-2026-09-24/130207-product-TE-mirror.pdf',evidence_page=3,
                 condition='Terminal drawing OD max6.4 is not permission to exceed tool6.35; measure delivered F0 insulation. No assumption fromAWG alone.')],
        not_manually_crimped=['Molex2147612112/2147632112/2147611112/2147631112 factory leads','Pololu1871 factory female leads'],
        WAGO_rule='Single untinned stranded copper per cage. No ferrule crimper added; do not use PIDG or UltraFast die on WAGO ends.',
        access_rule='Prepare exact tool access by borrowing or equivalent documented external service before assembly. Ownership/availability unknown; no service booked and no tools bought. This is not a recommendation to buy all expensive TE tools.',
        sample_rule='In phase2 follow tool maintenance/locator instructions, prepare off-robot sample for each actual wire/terminal, inspect copper/insulation retention and required tests. Never substitute pliers, solder-fill a rejected crimp, or transfer a solder-slug calibration dimension to the insulated terminal.',
        open_other_tools=['Exact soldering/heating/stripping/cutting/measuring/fastener tools and solder/flux SKU remain K3.',
                          'Whole harness cut/stock/tie census remains W5/K3; this matrix does not close either.'])

def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'tools.json').exists()
    begin=datetime.now(timezone.utc);v=matrix();assert v['processes'][0]['table_range_nominal_consistent']
    assert not v['processes'][1]['prior_assumption_within700CMA_row']
    paths={p['source'] for p in v['processes']}|{p['exact_terminal_evidence'] for p in v['processes'] if 'exact_terminal_evidence' in p}
    v['source_sha256']={p:sha(ROOT/p) for p in sorted(paths)}
    v['script_sha256']=sha(Path(__file__));v['started_utc']=begin.isoformat();v['finished_utc']=datetime.now(timezone.utc).isoformat()
    (OUT/'tools.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(tool_SKUs=len(v['tools']),processes=len(v['processes']),manual_crimp_ends=sum(p['ends'] for p in v['processes']),phase1_percent=70)),flush=True)

if __name__=='__main__':main()
