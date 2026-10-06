# Podparcie przesuniętej szyi: lokalny kandydat

07.10.2026. Niewybrane; M2 i pełne złożenie nadal OPEN. Bez fizycznego PASS.

## Aktualny kandydat: szyja z integralnym mocowaniem MAIN

`main-mount-sequence/NeckMainMount.FCStd`: lewa podpora zastępuje poprzednią,
prawa pozostaje z `coupled/RightRiser_candidate.stl`. Nie drukować starej lewej
razem z nową. Nowy lewy STL ma108×20×29mm z5mmbrim,11pełnych szkiców,
1solid/BOP0/zamkniętą siatkę; zapis/reopen i parametr MainGap4→5→4 zgodne.
Zmiana parametru przemieszcza także referencję płytki.0dodatkowych wydruków.

MAIN+34X/+4,52Z względem BoardDatum;2M2x12/2nuts/4washers dodatkowo
to kandydat stock. Podparcie dolnych podkładek100%nominalnie, pełne1,6mm
gwintu nakrętki i1,2252mm wystającego końca śruby.33par/0przecięć/0błędów;
4budżety narzędzi bez kontaktów. Referencja rodziny producenta, NIE dokładny
obrys komponentów dostarczonego SKU4853. Obliczenia44,515s.

MAIN wstępnie lutowany na stole, podpory na gołej P0, śruby od góry,
podkładki/nakrętki i nasadka od dołu; dopiero potem S0. D3×35mm wkrętak
iD6mm nasadka to budżety projektowe, nie zakwalifikowane fizyczne narzędzia.
Pierwszy test `main-mount/checks.json` odrzucił kolejność/narzędzia: S0
blokował wkrętak, bok P0 blokował boczny klucz. Geometrii nie przesuwano;
zmieniono kolejność i dostęp od spodu. Cały montaż robota pozostaje OPEN.

`mount-check-corrected.json`:8stosów osprzętu szyi/0błędów i wolne budżety
narzędzi w sprawdzonym zakresie. Pierwszy `mount-check.json` miał za wysoką
obwiednię wkładania nakrętki; korekta sondy, nie zmiana części.

NEXT: cztery końce MAIN z `main-mount-sequence/checks.json` i pozostałe
końce SPLICE_PI/USB (jeszcze OPEN_DATUM), pełne trasy/odciążenia, ruch głowy,
wspólny montaż i wybór/stock. Nie zaliczać M2 ani W5 za ten lokalny detal.

## Zachowana wcześniejsza baza podpór

Otwórz `coupled/NeckRisers.FCStd`. Dwa natywne PartDesign Bodies, po8w pełni
ograniczonych szkiców. VarSet HeadForward42/HeadRaise25/FootThickness4.
2podpory PETG są geometrycznie identyczne; potrzebne2sztuki. Oba STL
zachowane z raportem, docelowy wybór powinien liczyć jeden projekt×2.
Rozmiar druku78×20×29mm obejmuje5mmbrim wokół; podparcia w slicerze fazy2.

## Jeden uzgodniony krok zamiast mikroprzesunięć

Pierwsza geometria kolidowała wyłącznie z rezerwacją MAIN4853:1351,802486mm³.
`checks.json` dokumentuje odrzucenie; źródło tej wersji commit55a1fe6.
Druga zachowuje osie P0 i położenie głowy; MAIN przenosi się wspólnie+34X
doX−56..−32. Nie poszerza tułowia i nie zmienia P0/wybranego R53.
MocowanieMAIN oraz jego4końce W060/W078/W079/W080 wymagają nowych tras
i odciążeń. `coupled/checks.json` zapisuje stare/nowe datums; to NIE wiązka.

Sprawdzono8par rzeczywistych brył lub jawnych rezerwacji kupnych modułów:
0przecięć/0błędów, oba nowe solids valid/BOP0; nominalne wałki/nakrętki/
podkładki nie przecinają nowych podpór, podparcie podkładek100%nominalnie.
Parametr42→43→42, zapis i ponowne otwarcie zgodne; oba STL zamknięte,
po1komponencie. Obliczenia16,109s. Bbox służy tylko filtrowaniu par.
Nie jest to badanie całego robota ani potwierdzenie dokładnych obrysów SKU.

## Osprzęt i montaż do dalszej kwalifikacji

Dolne4M2x10 zamiast starych4M2x14, osieX−80/−70,Y±22,5 naP0, Z38,52.
Górne4M2x12,4nuts i8OD5washers dodatkowo; oparte o istniejący dokładny
SKU z fixed-fastener-cart R53, lecz nie wybrane ilości. Górne osie
X−122/−112,Y±22,5, płaszczyzna głowyZ67,52. Dwie dawne przednie stopy
kasety zastępowane, nie drukowane razem z nowymi podporami.

Na gołej ramie: dolne śruby od spodu, podkładki/nakrętki bocznymi kieszeniami;
następnie górne nakrętki/podkładki, foundation i górne śruby; potem yaw.
Ta recepta nie zamyka całej kolejności montażu robota.

Obciążenie/pełzanie i fizyczne pasowania PETG
w fazie2. Nie ponawiać odrzuconego układu ani regenerować istniejących plików.
