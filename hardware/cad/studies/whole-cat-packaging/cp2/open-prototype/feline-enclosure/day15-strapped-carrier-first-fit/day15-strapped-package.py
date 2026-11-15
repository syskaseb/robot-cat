from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-strapped-carrier-first-fit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
r=json.loads((P/'closed-load-path-first-gate.json').read_bytes())
r['chosen_hypothesis_acceptance_criterion']='A common ENCLOSINGclamp tiesP19andbatteryTOactualfixedP12, giving positiveuptake/antiX/Y/rotation withoutgravityorfrictionalone. Same loops must provide this loadrole before rearjoint retirement.'
r['status']='HOLD_CURRENT_LOOPS_NOT_A_COMMON_ENCLOSING_CLAMP'
r['consequence']='The currentloops enclose neitherP12 norP19material, so the chosen SAMELOOP commonenclosingclamp is not established. P19floor liesbelowbottomstrap, P12roofabove. Fourfeet remaincompressionbearingonly. NOrearjointretirement/newprint/secondloopfamily. This doesNOTprove allhook/capture/strap architectures impossible: stopcaptureafterrelativefreeplay wouldneed itsOWN actualbearing/escape/assembly proof, absenthere.'
r['not_a_universal_retention_impossibility_proof']=True
write('closed-load-path-first-gate.json',r)
write('retention-and-initial-lay-map.json',dict(status='ONE_HYPOTHESIS_HOLD_NO_COMPLETE_ASSEMBLY_RELEASE',load_map=[dict(role='BatteryX',actual='Existingendstops x-5..-2/104.5..108',status='P19relative stoponly, padding/cellcontactFIT'),dict(role='BatteryY',actual='InnerloopcapacityY±21 vsbatteryY±17.5',status='takeup/paddingactualFIT, notzero-slip proof'),dict(role='P19downZ',actual='Fourdeckfeet at(5/95,-45/41),bottom48.52',status='receivedcompressioncontactonly'),dict(role='P19upZ_to_frame',actual='P12roofoutsideclosedloops, floorbelowloops',status='MISSINGacceptedpositiveroot; guidescanlimitlatermotion butcapture/freeplayproofnotreceived'),dict(role='P19X/Y/rotation',actual='Two15bandfieldsin16.2guidesat29.5/52.5; frontjointretainedbutnotrequalified',status='No completepositiveanti-slide/rotationdemonstration withoutroot')],initial_order=[dict(step=1,action='A: prethreadbothwhole200units intoopenP12guides; B: supportopenP19; retainfulluntrimmedtails/bucklesoutsidefeed',status='candidateopenhandlayonly, notframeclamp'),dict(step=2,action='Benchlay4independentfull220/MTAfactoryunits andbothendsbeforetray/keepers. Bearingonlyafteractualplasticfit, noTEterminalpressure orE1unplug',status='sourcefunctionsretained/FIT'),dict(step=3,action='KeepfullfrontM3 stock/demand ascurrentlyproposed, driverbeforemodules ifactualaccessqualified',status='notnewfrontrootGO'),dict(step=4,action='STOPbeforeclaimingsecuredcarrier/battery. NeedpositiveP19-to-frameinterface independentofbatterycompression, oractuallyenclosingwholeloadroute',status='HOLD_missingroot'),dict(step=5,action='Forlateracceptedcarrier: fixedtouchP14 stays; removablemicP15 thenBUS/P13 thenactualXT60/balance thenbattery. No quickservice/cut/leadextension',status='conditionalnotverifiednewassembly')],whole_stock=dict(units=2,selected='RCManiak4982 /NSTRIF15200M',nominal_textile_each=200,width=15,total210_includesbuckle=True,bodyloop_source=130.64955592153875,closure_reserve20_project=True,full_tail_each49p350444=True,extra25_required=False,physical_stock_thickness_buckle_lap_takeup_strength='FIT',cut=None),minimal_next_decision='Choosea truecapturedcarrier/frame loadinterface fromactualP12member andP19floor; currentopenbottomguides are not automaticallystrappingroots. No nextvariant builtinthispacket.',physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None))
sources=[P.parent/'day15-head-ola-whole-proposal/manifest.json',P.parent/'day15-head-ola-whole-proposal/head-ola-proposal.FCStd',P.parent/'day15-p12-integrated-retention/manifest.json',P.parent/'day15-p12-integrated-retention/whole-kit-first-gate.json',P.parent/'day15-p12-integrated-retention/actual-stock-fields-and-effectivity.json',ROOT/'hardware/electronics/kicad-current/selected-components.csv']
sources=[p for p in sources if p.exists()]
for folder in ['day15-head-ola-whole-proposal','day15-p12-integrated-retention']:
 p=P.parent/folder;d=json.loads((p/'manifest.json').read_bytes())
 for row in d['files']:
  f=Path(row['path']);f=f if f.is_absolute() else p/f;assert sha(f)==row['sha256'],f
write('source-pins.json',dict(source_commit='a28265d0d06037f842510c5897c377d1b0302186',prior20_plus36_exact_unchanged=True,pins=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sources],source_geometry_method='DirectworldShape.copy, no placementtransform orfunctionalCSG. Onlyuppercheekcosmeticchanged; no byteidentityclaim for reserializedBREP.',unchanged_Pi4_guide_frame_audio_scopes='Reuseonlyunchangedsourcephysicalshapesbycopyprovenance; no oldmatrixreplay',no_newSTL=True,no_retirement_of_failed_rear_role=True))
for n in ['day15-strapped-start.py','day15-strapped-read.py','day15-strapped-section-plot.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
(P/'START_HERE.md').write_bytes('''# Carrier baterii/MTA — wynik jednej hipotezy

**HOLD: obecne dwa paski nie zostały zakwalifikowane jako wspólny zacisk P19 do ramy P12. Nie wydano nowego STL ani kompletnego carriera do druku.**

Otwórz `strapped-carrier.FCStd`; bieżący cały układ i stare nieprzyjęte węzły są zachowane. Najważniejszy wynik jest w `actual-two-load-sections.png` oraz `closed-load-path-first-gate.json`. Są to rzeczywiste przekroje BRep w obu aktualnych stacjach X29,5 i52,5, a nie pudełkowy szkic wolnego miejsca.

## Dlaczego nie usunięto tylnej śruby

Obecna zamknięta pętla ma światło Y±21/Z65..86,5 i pełny modelowany pasek2,2mm. W całym15mm pasie każdej z obu pętli **wewnątrz nie ma materiału P12 ani P19: wszystkie4nowe odczyty validcommon0**. Podłoga carriera Z60,8..62,8 leży pod dolnym paskiem Z62,8..65. Dach P12 Z91,3..96 leży nad górnym paskiem Z86,5..88,7; nominalnie2,6mm do dachu. Paski przechodzą przez rzeczywiste otwarte od dołu prowadnice, ale to nie oznacza, że spinają te druki.

Wcześniejsze własne clearance/common0 paska z drukami oraz4stopy na decku są zachowane. Stopy dowodzą oparcia na ściskanie, nie kompletnej retencji przy podnoszeniu/obrocie. Obecna hipoteza wspólnego **obejmującego** zacisku nie została wykazana, dlatego nie wolno na tej podstawie wycofać tylnego węzła. To nie jest dowód niemożliwości wszystkich haków/prowadnic/pasków: ewentualne ograniczenie ruchu po wybraniu luzu wymaga własnego dowodu powierzchni oporowych, drogi wysunięcia i montażu. Tu go nie dorobiono ani nie nazwano gotową kotwą.

Stare rzeczywiste rearM3/S0common60,309861 i P11ROI0materiału pozostają. Nie wycięto łba/tipa, nie przesunięto osi, S0 ani wyposażenia. PełneM3x25/nut/2washers i przód są nadal jawnie nieprzyjętą propozycją; nie ukryto problemu. Nie zbudowano drugiej pętli, nowej podpory ani nowego wariantu ramy.

## Dwie osoby — co wolno przymierzyć, gdzie zatrzymać montaż

1. A podtrzymuje otwarty P19, B wstępnie przewleka dwa CAŁE wybrane paski200 przez istniejące prowadnice. Sprzączki poza feedem, całe reszty w opisanych polach. To przymiarka drogi, nie odbiór zacisku.
2. Cztery niezależne MTA220 i oba fabryczne końce ułożyć otwarcie przed tacką/keeperami; nacisk tylko na potwierdzony plastik obudowy, nie TE. Bez odpinania lutowanego E1.
3. Przedni pełny węzeł i narzędzie przed modułami pozostają do potwierdzenia; ta porcja nie nadaje mu nowego loadPASS.
4. **STOP przed uznaniem tacki/baterii za zabezpieczone.** Potrzebne rzeczywiste dodatnie połączenie P19–rama, niezależne od samego ściskania baterii, albo droga rzeczywiście obejmująca wymagane elementy. W tej porcji nie projektowano kolejnego rozwiązania.
5. Późniejszy serwis po odebraniu mocowania: P14touch pozostaje, micP15 -> BUS/P13 -> rzeczywiste XT60+balance -> bateria. To nadal warunkowa kolejność, nie szybki serwis ani obietnica zasięgu końców.

## Stock i zachowane części

Te same2×RCManiak4982/NSTRIF15200M:15×200mm tkaniny; projektowe210 zawiera sprzączkę, nie dodatkowy lap. Każdy model zachowuje pętlę130,65 +rezerwęclosure20 +całą resztę49,35, bez nowego wymogu25pull i bez cięcia. Rzeczywiste grubość/sprzączka/lap/take-up/padding/wytrzymałość to FIT. Nie dowiedziono fizycznego stockfit. Bateria, wszystkie MTA,4stopy, Pi4/guide, źródłowa rama,57+extras/ochrona/porty/końce i4DATA5plus7G pozostają; actualfit/cut/slack=NULL. Nie powtarzano dawnych macierzy/126compound/F0/PCB/headfamilies. Brak gotowego całego kitu.

## Jedna mała poprawka wyglądu

`whole-opaque-front-three-quarter.png` to rzeczywisty obejrzany widok tego samego układu: cofnięto wyłącznie górny brzeg maski pod pełne złote obramowania oczu (Z133 minus1,25 =131,75). Dolne policzki i wszystkie pełne okna pozostały przez subset, bez ruchu kupnych części; grzbiet/ogon/nogi bez zmian. Piny w `opaque-correction-source-pins.json`. To PROPOSED_NOT_PRINTSKIN, bez STL i bez kolejnej recenzji. `whole-retention-load-context.png` ma tylko kosmetykę ukrytą i przezroczystość P12/P19/baterii dla widoczności pasków; nie udaje skończonej skorupy.
'''.encode())
print(json.dumps(dict(prepared=str(P),status=r['status'],sourcepins=len(sources),noSTL=True)))
