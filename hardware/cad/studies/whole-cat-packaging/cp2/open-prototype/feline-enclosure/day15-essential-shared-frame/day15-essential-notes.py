from pathlib import Path
import json,csv,shutil,struct,collections,math
P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-essential-shared-frame');part=json.loads((P/'parting.json').read_bytes());region=json.loads((P/'local-result.json').read_bytes())
meshrows=[]
for x in part['parts']:
 p=P/(x['name']+'.stl');b=p.read_bytes();tri=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*tri
 edges=collections.Counter();volume=0
 for j in range(tri):
  v=struct.unpack_from('<12f',b,84+j*50)[3:];a,bv,c=[v[k:k+3] for k in [0,3,6]]
  volume+=sum(a[k]*(bv[(k+1)%3]*c[(k+2)%3]-bv[(k+2)%3]*c[(k+1)%3]) for k in range(3))/6
  pts=[tuple(round(t,5) for t in w) for w in [a,bv,c]]
  for k in range(3):edges[tuple(sorted([pts[k],pts[(k+1)%3]]))]+=1
 counts=collections.Counter(edges.values());meshrows.append(dict(part=x['name'],triangles=tri,edge_multiplicities=dict(counts),signed_volume_mm3=volume,closed=all(n==2 for n in edges.values()),size_mm=x['print_size_mm']));assert all(n==2 for n in edges.values()) and volume>0,x['name']
(P/'mesh-check.json').write_bytes((json.dumps(meshrows,indent=2)+'\n').encode())
with (P/'print-parts.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['part','qty','print_X_mm','print_Y_mm','print_Z_mm','status','notes'])
 for x in part['parts']:w.writerow([x['name'],x['quantity'],*x['print_size_mm'],'STRUCTURAL_CAD_STAGE_NOT_RELEASED_UNTIL_FRAME_RESULT', 'P10/P12 projecting ribs need support assessment; no slicer/print performed; lowerjaw second position uses flip only if quantity-identity proof received'])
with (P/'used-fasteners.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['role','standard_nominal','qty','source_or_demand','status'])
 for row in [('new_frame_negative_and_upper','M3x12',6,'new standard demand'),('new_frame_positive','M3x10',2,'new standard demand'),('new_BUS_removable','M3x16',2,'new standard demand'),('new_all_joints','M3 nut AF5.5 thickness2.4',10,'new standard demand'),('new_all_joints','washer M3 OD7 thickness0.5',20,'new standard demand'),('retained_four_deck_clamps_front','M3x12',2,'unchanged32152035 nominal demand'),('retained_four_deck_clamps_rear','M3x16',2,'unchanged32152035 nominal demand'),('retained_four_deck_clamps','M3 nut AF5.5 thickness2.4',4,'unchanged32152035 nominal demand'),('retained_four_deck_clamps','washer M3 OD7 thickness0.5',4,'unchanged32152035 nominal demand')]:w.writerow([*row,'inventory/thread/supplier strength UNCONFIRMED; no purchase'])
text='''# START — wspólna rama, etap CAD do przymiarki

**Bieżący dokument:** `shared-frame.FCStd`. `frame-result.json` rozstrzyga odbiór nowych interfejsów; jeśli ma HOLD, tych STL nie traktować jako zwolnionego zestawu. Zamrożona podstawa `day14-fasttrack-first-fit/fit-kit-ready` pozostaje bez zmian, zaczyna się od P00/8 rzeczywistych osi. Nie ma fizycznego testu gwintu/masy/ruchu.

## Zamknięty lokalny problem audio

Nie utrwalono własnegoR14. Z górnego dojściaZ131, zakresu chłodzenia/ramki, rzeczywistych odsunięć7profili i minimalnychRcore6,4/8,4 wynika wspólny przedziałRosi10,45..17mm. WybranoR12; coreRmin9,3. Odcinek przyAMP jest przed górnym łukiem, a jego początek119mm jest5mm nad rozgałęzieniem114mm. Całeprofile+0,4 mają84/84 dodatnie relacje do wybranych sąsiadów, minimum2,38mm; kanałpełnejpojemności7 ma1,30mm, a21/21nominalnychodstępów co najmniej0,2mm. Zasada1,25 zachowana. To lokalne przyjęcie tego konkretnego pola, nie całego gotowego harnessu/leadstock.

Przez feed idą rzeczywiście2speakerBTL, z góry5PiI2S/zasilanie/masa. AniBTL nie jest masą. AMPpady/header/kierunki, PiGPIOwyjście i terminale/długość głośnika są jawnym nominalnym założeniemFIT. Lokalne długości nie są długością całychkabli/cięciem. USB_AUDIO osobny, bez drugiego kredytu500DelockBUS. Cztery niezależne220/obaMTA/FHAC>=84,5/K1474/pełnekońce iE1solder zachowane.

## Realne części i śruby

- P10/P11: przedni/tylnyportal ze wspólnymi górnymi szczękami czterech zachowanych zacisków. P16/P17: osobne dolne szczęki. Nie ma fuzji z kupnym WAVEGO ani wiercenia jego ramy.
- P12: wspólny środek z półką głośnika, standoffamiPi i strefami podparcia logiki. Przednie skrzydło tacki i jeden standoff należą doP10; ich pozycja/kształt zachowane. To rzeczywisty podział, nie luźny odcięty fragment.
- Cztery złącza środkaportal: integralne półzakładki, pełna śruba/nakrętka/dwiepodkładki. DwaM3x12 i dwaM3x10. Przedni ujemny interfejs ma wydłużony wspólny język do obszaru pozaBNO; rawC0BNOcommon1,6539166 zachowany. Nie zmieniono BNO ani otworówPi.
- P13: zdejmowany mostekBUS na dwóch pełnych M3x16 do integralnych uszuP12. Jego31mm separacji odPi nie zamieniono w nowe pasowanie fizyczne.
- P14: stała prawa belkaTTP223. P15: osobna lewa belka+podparcieReSpeaker. DwieparyM3x12 na rzeczywistych dolnych zakładkach do poprzeczek portalów. Żadnej drukowanej części nie sfuzowano z drugą; rzeczywiste wspólne objętości części wynoszą0.

Komplet nowych standardowych zestawów:10śrub/10nakrętek/20podkładek. Zachowane czteryzaciski dodają4śruby/4nakrętki/4podkładki — nie dublować ich przy zamówieniu/listowaniu. Modele mają pełny trzon/czubek/łeb i całą nakrętkę; wymiary nominalne wCSV/JSON. Zapas i rzeczywisty gwint niepotwierdzone, nic nie kupiono. Osobna retencja PCB i bezpieczne chwytaki audio są NEXT, nie ukryte w etapie ramy.

## Dwie osoby, otwarte układanie

1. P00 i rzeczywista8-osiowa rama: FIT1 rewizja/gwint/masa/ruch. A trzyma ramę, B składa dolne szczęki i portale na zachowanych kompletnych zestawach. Banki/WAGO i krótkie połączone końce układać otwarcie, bez wirtualnego rozpinania lutów.
2. Połączyć P12 z portalami na stole bezPCB. Pełny dostęp boczny do śrub PRZED MAIN/AUX/Pi/pionowąlogiką; późniejsza rzadka naprawa może wymagać zdjęcia płytki. Nie prowadzić narzędzia przez zamontowany MAIN.
3. Ułożyć parę głośnika przez otwarty kanał, potem pięć przewodów od góry przyAMP. Dużych fabrycznych obudów nie przeciągać przez zamknięty otwór. PCB/końce/E1 lutowane zachowane; dociski krawędziowe dopiero po układaniu i potwierdzeniu rzeczywistych keepout.
4. P14/TTP223 przykręcić jako stałą prawąbelkę. Jego przewód doE1 zostaje w stałej bocznej strefie, pozycja złączy nie zmienia się przy baterii — nie założono nowej odpinki ani zapasu do parkowania. Ułożyć ten przewód przed dociskami i sprawdzić rzeczywistą długośćFIT2.
5. P13/BUS i P15/mikrofon zamykać na końcu. Przy baterii: odłączyć istniejący rzeczywistyUSB_AUDIO, zdjąć dwa leweM3 i P15/ReSpeaker; odłączyć istniejąceUSB/zasilanieBUS, odkręcić dwaM3mostka i wyjąćP13; odłączoną baterię przesunąć do lewego otwartego miejsca i podnieść. P14 i dotyk pozostają. To wiarygodna kolejność otwartych części; pełne fizyczne końce, długości i próba wyjęcia należą doFIT2, nie szybki serwis ani wykonana czynność sprzętowa.

## Druk i dalszy zakres

Eksporty obejmują WYŁĄCZNIE nasze rzeczywiste części P10..P17. Własny lokalnyXYZ zZ0, każdy wymiar<256mm; zamknięcie siatki i dodatniaobjętość wmesh-check. Współrzędne złożenia wFCStd/partingJSON. Portale mają żebra/zakładki, P12 podwieszenia półki: ocenić podpory przy rzeczywistym slicerpreview w przyszłości, nie nazywać całego zestawu płaskim bez tej próby. Nie uruchamiano slicera/druku.

Nie dociskać niewidocznych elementówAMP/Pi ani membrany głośnika/mikrofonu. Strefy chwytu i otwory akustyczne są nazwanym fizycznym FIT/coupon; bez komory akustycznej ani bramki rozpoznawania mowy. Po odebranej ramie potrzebne: proste bezpieczne edgekeepers/izolujące dystanse, retencja banków/baterii i rzeczywisty stock/ends. FIT3obrysOli/głowa/ogon/otworyosłony pozostaje. Cały robot nie jest przyjęty ani zasilony; actualcut/installedfit/slackNULL. StareHOLDy nie zostały skasowane.
'''
(P/'START_HERE.md').write_bytes(text.encode());print(json.dumps({'meshes':len(meshrows),'closed_positive':all(x['closed'] and x['signed_volume_mm3']>0 for x in meshrows)}))
