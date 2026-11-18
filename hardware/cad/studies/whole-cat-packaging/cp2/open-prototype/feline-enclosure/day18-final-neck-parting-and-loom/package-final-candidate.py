from pathlib import Path
import json,hashlib,zipfile,datetime
P=Path(__file__).parent;S=P.parent/'day18-closed-whole-common-assembly'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
source=S/'closed-whole-common-assembly.FCStd';native=P/'final-neck-parting-and-loom.FCStd'
assert sha(source)=='cb6cae78d89b1aee9bb05ba18c1a8ed129aadec572b3417a9c7677f7b61984c1'
state=json.loads((P/'native-idle-receipt.json').read_text());assert state['modified'] is False
with zipfile.ZipFile(source) as z0,zipfile.ZipFile(native) as z1:
 assert z1.testzip() is None
 crc=len(z1.infolist());n0=set(z0.namelist());n1=set(z1.namelist())
 changed=[n for n in sorted(n0&n1) if n.endswith('.Shape.brp') and z0.read(n)!=z1.read(n)]
 identity=[]
 for o in ['D18C_TRUE_PITCH_OPTICAL_RECEIVER','F3_E1_REMOVABLE_EDGE_KEEPER','F2_COMMON_PI_BUS_PCA_RECEIVER','D18C_P02_THREE_ROOT_THROUGH_VERSION','P03_rear_deck_integrated_load_yoke']:
  n=o+'.Shape.brp';identity.append({'object':o,'serialized_geometry_payload_equal':n in n0&n1 and z0.read(n)==z1.read(n),'meaning':'only explicit serialized payload identity; no new neighbor or motion approval inferred'})
wr('sourcepins.json',{'source_commit':'98e254116c1128f13a94742449beddf451461fd5','source_native':str(source),'source_sha256':sha(source),'source_immutable_verified':True,'candidate_native':native.name,'candidate_native_sha256':sha(native),'native_zip_crc_records':crc,'changed_shape_payloads':changed,'unchanged_local_interface_payloads':identity,'source_poses':'no purchased module/port/protection/leg/tail/source cable end moved; eight full existing upper-shell M2 set actors moved with their complete new receiving joints, same volume recorded','current_views':[{ 'path':p.name,'sha256':sha(p)} for p in sorted(P.glob('candidate-whole-*.png'))]})
idx=json.loads((S/'conditional-current-print-index.json').read_text())
wr('print-effectivity-NO-NEW-RELEASE.json',{'status':'NO NEW STL OR COMPLETE CAT RELEASE','candidate_native':'UNSELECTED neck architecture FAILS full crosspin clearance, FFC occupied interface and protected visual closure','unchanged_prior_local_fit_only':[{'file':str(S/q['stl']),'sha256':sha(S/q['stl']),'scope':q['condition'],'source_object':q['source_object']} for q in idx['parts'] if q.get('closed_reopened')], 'instructions':'prior two small source98 local dryfit objects remain PRIOR conditional artifacts; no automatic whole current assembly approval and no source file overwritten','physical_PASS':False})
gate=json.loads((P/'current-combined-neck-decision-gate.json').read_text())
wr('final-whole-interface-disposition.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ONE_CANDIDATE_REJECTED_NOT_A_CLOSED_PROTOTYPE','material_change':'One real fixed/moving partition: front skull+upper back pitch-moving; lower neck becomes fixed shoulder; fixed inset guard on actual unchanged-bearing outer cap with two complete original cap sets. Same two upper-shell M2x16 sets relocated to real upper joint. No new purchased hardware.','scoped_positive':['30 neutral/four-extreme actual changed head-versus-neck material BOPs common0','source bearing-cap and both new columns/baffle intended volumes0missing after actual positive overlap repair','both source floor/receiving-root material below90 retained0missing','current front/back shells and fixed shoulders valid1solid, separate head parts common0 after profile-bounded roof completion','analytic vertical cap/lower-guard lower gap2.438mm and inner baffle/core-cavity bound1.866mm under stated assumptions; not global movement/assembly approval'], 'rejection':{'full_actual_standard_crosspin_vs_new_guard':'two actual yaw+/-20 witnesses common0.233389mm3; neutral gap1.0<1.25. Fork-only clearance had hidden full tip, so root gate does NOT accept interface. No bolt shrink/stock cut allowed.','FFC':'52 accepted full16.8x1.8 occupied profile corner witnesses inside actual new print. They reject this mapped family/guard allocation, not prove physical conductor contact, stock shortage, or all manual routes impossible.','ToF':'no sampled centre inside print but four EXT011 clearance candidates down to0.20mm after OD+project allowance; not full-profile or whole-motion GO.','JR':'full250+250+300 units and source roles retained, actual strain/grips/complete upper budget not qualified','appearance':'All four actual snapshots inspected. Large side/back neck opening still exposes internal hardware. Protected closed appearance NOT achieved; no Ola approval.'},'whole_causal_consequence':'A rear skin/cowl cut alone did remove old shell commons but cannot deliver the requested protected interface. The chosen axial cap-rooted guard needs a load/parting route outside the COMPLETE yaw crosspin sweep and the full occupied loom, plus continuous visual underlap. No second geometry family attempted after combined failure; finish/save/curation only.','source98_not_replaced_as_selected':True,'geometry_work_finished_utc':state['utc'],'new_STL_release':False,'wholekit_ready':False,'physical_PASS':False,'actual_fit':None,'actual_cut':None,'installed_slack':None})
text='''# Ostatnia próba podziału głowa–szyja — ODRZUCONA

**Nie uzyskano zamkniętego interfejsu. Ten native jest NIEPRZYJĘTYM kandydatem, nie modelem do drukowania ani następcą przyjętych lokalnych przymiarek98.** Źródło98 pozostało bajtowo niezmienione.

Otwórz `final-neck-parting-and-loom.FCStd` wyłącznie do oglądania przyczyny. `candidate-whole-front.png`, `candidate-whole-side.png`, `candidate-whole-three-quarter.png` i `candidate-whole-interior.png` pokazują tę samą rzeczywistą geometrię. Części kupne i wystające elementy nie zostały ukryte. Obejrzałem wszystkie cztery obrazy: bok szyi nadal szeroko odsłania wnętrze. Wygląd zamkniętego kota nie został osiągnięty.

## Co zmieniono i co sprawdzono

Dolną część dawnego ruchomego tyłu głowy przeniesiono funkcjonalnie do stałych barków. Twarz i górny tył pozostają na pitch; górny tył wykorzystuje te same dwa kompletne zestawyM2x16 na rzeczywistych nowych gniazdach. Dwa pierwotne mocowania czaszki do pitch i pełne części Camera3/ToF, dwa MG, rogi/łożyska, kątyyaw±20/pitch±10 i fabryczne końce pozostają. Nie zmieniano modułów elektroniki, nóg ani osiYogona.

Stara kolizja194,55/199,84mm3 została usunięta: 30 lokalnych odczytów materiału w neutralnej i czterech skrajnych skorelowanych pozach dało common0. To nie certyfikat wszystkich odstępów/ruchu. Źródłowa pokrywa łożyska i oba nowe słupki/osłona mają0brakującego materiału; rzeczywiste dodatnie połączenia są zapisane. Dolne źródłowe gniazda osłon/podłoga poniżej90 pozostały0missing. Nie fuzjowano części, które muszą być ruchome lub zdejmowane.

## Dlaczego odrzucono CAŁY interfejs

- Pełna śruba sprzęgła yaw koliduje z nowym stałym wspornikiem przy obu±20: **0,233389mm3**, a neutralnie odstęp wynosi1,0<1,25. Test samego drukowanego widelca tego nie wykrywał. Nie skrócono śruby ani nie obniżono marginesu.
- Pełny przyjęty profil FFC16,8×1,8 ma **52 świadki naroży wewnątrz druku**. To odrzuca tę konkretną alokację, nie dowodzi kolizji każdej możliwej ręcznej trasy ani braku długości kabla200. ZachowaneRinner12,5, końce10raz i zakresy ruchu.
- Przy aktualnym stałym fanoucie ToF znaleziono cztery małe odstępy EXT011, minimalnie0,20mm po uwzględnieniuOD i założenia pakowania. Brak wejścia osi w druk nie daje zgody na cały profil. Cztery HELU/R31,5, sourceJP3.2/6/3/4 i poprzedni plan510/rdzeń pozostają bez nowych złączy, przewodów czy zapasuPololu.
- JR250+250+300, obecneDATA500/POWER i pozostałe prawdziwe jednostki nadal mają otwarte zadania ułożenia/odciążenia. Nie otrzymały pozornegoPASS przez uproszczenie rysunku.
- Rzeczywista osłona pozostawia zbyt duży widoczny otwór szyi. To niewykonane zamknięcie konstrukcyjne, nie nieznana fizyczna tolerancja.

## Montaż i skutek

Źródłowy mechanizm ma osobny widelec/journal i rzeczywisty crosspin. Fabryczny róg/śrubę składa się na stole bez dodanej grubości pod śrubą; journal od dołu, widelec i pełny crosspin przed elektroniką i późnymi osłonami. Nowy guard zachowuje źródłową pokrywę, pełne istniejące zestawy i otwory narzędzia, ale **nie ma dopuszczenia funkcjonalnego** z powodu konfliktu pełnego crosspinu. Nie wykonywać końcowego montażu tej wersji. E1/PCA pozostają całym lutowanym zespołem; nie zakłada się wirtualnego odpinania.

Wniosek dotyczy wspólnego układu: ochrona szyi potrzebuje drogi podparcia/podziału poza pełną kopertą sprzęgła i zajętą wiązką oraz ciągłego nakrycia widokowego. Tego nie rozwiązuje kolejny mały otwór na czubek ani wycięcie powierzchni dla jednego położenia. Zgodnie z ostatnim zakresem po falsyfikatorze nie rozpoczęto drugiej rodziny; geometria zakończona, dalej tylko kuracja/zapis.

**ZERO nowychSTL.** `print-effectivity-NO-NEW-RELEASE.json` wskazuje jedynie wcześniejsze dwa małe warunkowe pliki98 bez kopiowania/awansu całego zestawu. Pozostałe mocowania/4MTA0100335sample/całe ułożenie/masa pozostają otwarte. Aktualny subtotal materiału dotyczy dziesięciu wybranych modeli kandydata, nie całego kota i nie uznanej oszczędności — kandydat ma brakujące zamknięcie. PhysicalPASS=false, rzeczywistefit/cut/slack=NULL. Brak zasilania/druku/zakupów/zmianROS.
'''
(P/'START_HERE.md').write_bytes(text.encode())
wr('receipt.json',{'actual_current_input':'01a1ed74-91af-7113-b2c5-4f0de640ad36','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'COMPLETED_REJECTED_ONE_HYPOTHESIS_NO_FURTHER_GEOMETRY','native':native.name,'native_sha256':sha(native),'native_crc_records':crc,'GUI':{'PID':17796,'documents':1,'objects':1559,'modified':False,'pending':None,'owned_compute':'IDLE'},'geometry_finished_utc':state['utc'],'actual_usage_read_started_utc':'2026-11-18T07:48:18Z','ordinaryUsageAllowed':True,'reset_used':False,'shared_parent_files_edited':False,'source98_immutable':True,'new_print_files':0,'wholekit_ready':False,'physical_PASS':False,'actual_fit_cut_slack':None})
for p in P.iterdir():
 if p.suffix.lower() in ['.json','.py','.md']:p.write_bytes(p.read_text(encoding='utf-8-sig').replace('\r\n','\n').encode())
files=[p for p in P.iterdir() if p.is_file() and (p.suffix.lower() in ['.json','.py','.md','.png'] or p.name==native.name) and p.name!='manifest.json']
wr('manifest.json',{'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'native_crc_records':crc,'source_commit':'98e254116c1128f13a94742449beddf451461fd5','candidate_status':'REJECTED_NOT_SELECTED','new_STL_release':False,'wholekit_ready':False})
print(json.dumps({'files':len(files)+1,'manifest_sha256':sha(P/'manifest.json'),'native_sha256':sha(native),'native_CRC':crc,'geometry_finish':state['utc'],'source_payload_identity':identity}))
