# MG92B: znaleziony model orczyka i warunkowa kontrola miejsca

2026-09-23. **Referencja społecznościowa, nie model producenta ani zatwierdzenie
montażu. Nie zmieniono robota.** Użytkownik polecił samodzielnie dobierać dalsze
kroki i wyszukiwać brakujące pomiary/modelowanie, zamiast czekać na jego pomiary.

## Znalezisko

Autor **Alberto / otrebla333**, projekt [Dtto Modular Robot](https://github.com/otrebla333/Dtto-Modular-Robot),
wersja v2.0.1, commit `b4b97069888079e5726600969b8e0783bfe2514f`.
[Oryginalny FreeCAD](https://raw.githubusercontent.com/otrebla333/Dtto-Modular-Robot/b4b97069888079e5726600969b8e0783bfe2514f/3D-printing/Freecad-files/Dttov2.0.1.FCStd)
zawiera obiekty `Fusion105` opisany jako **MG92B arm** i `Cut158` jako MG92B.
[Instrukcja autora dla v2](https://hackaday.io/project/9976/instructions)
używa dwóch MG92B i ich krzyżowych ramion. README głównego repo opisuje starsze
v1 z SG92R — nie wolno mylić tych wersji.

Pobrany plik ma SHA-256
`8630500f6c58886f5fd953bc3f3eae5b0fe36cff955ad65be77af65bea2c1cb1`.
Duży oryginał pozostaje w ignorowanym katalogu roboczym. Z jego archiwum
odczytano tylko XML i zapisane bryły BRep, **bez otwierania oryginalnego
dokumentu i bez ładowania jego obiektów Python**.

[MG92BCommunityReference.FCStd](MG92BCommunityReference.FCStd) ma dwa zwykłe
obiekty referencyjne, bez zależności zewnętrznych. Każda bryła przeszła ścisłe
BOP w FreeCAD 1.1.3 / OCCT 7.8.1. To poprawność zapisu geometrii, nie pomiar
fizycznego orczyka. Źródła, hashe i parametry są w [measurements.json](measurements.json).

## Wymiary odczytane z modelu, nie z egzemplarza

Oś wałka modelu Dtto jest równoległa do **Y**, przez X=6, Z=6 mm.

| Cecha | Wartość modelu [mm] | Znaczenie |
|---|---|---|
| Obrys krzyża w płaszczyźnie XZ | 28 × 16,7 | uproszczony prostokątny obrys ramion |
| Grubość ramion wzdłuż osi Y | 1,95 | Y=32,58…34,53 |
| Szerokości ramion | 4,20 / 3,85 | dwie różne szerokości |
| Długości dłuższego ramienia od osi | 11 / 17 | krzyż nie jest symetryczny w X |
| Cylindryczna obwiednia piasty | Ø7,2 × 5,33 | Y=30…35,33, pełna bryła |
| Całkowity zakres osiowy modelu ramienia | 5,45 | Y=30…35,45; zawiera dodatkowy walec Ø4 |
| Rozstaw otworów uszu serwa Dtto | 27,7 | nie 27,5 odczytane z Adafruit |
| Szerokość serwa z uszami Dtto | 31,3 | nie 31,5 z karty TowerPro/Adafruit |

Krzyż jest sumą **dwóch prostopadłościanów i dwóch pełnych walców**.
Nie zawiera otworów na śruby, wieloklinu, zaokrągleń ani geometrii śruby
centralnej. Dodatkowego walca nie interpretujemy jako wymiaru otworu czy łba
śruby bez dowodu. Nie ma informacji o metodzie pomiaru ani tolerancji autora.
Nie traktujemy go jako gwarantowanej obwiedni wszystkich serw MG92B.

## Co wykazało porównanie z ogonem

MCP potwierdziło w bieżącym kocie: wałek kończy się na Z=91 mm,
nasada `TailRoot29` zaczyna na Z=92 mm. Ta jednomilimetrowa różnica poziomów
nie jest dowodem miejsca na kompletny orczyk. Narzędzie MCP `distance` zwraca
odległość środków, nie minimalny prześwit brył; nie użyto jej do tego wniosku.

W [conditional-clearance.json](conditional-clearance.json) przeliczono 72
warianty, tylko względem siedmiu części PETG podpory. Oś orczyka wyrównano
do (171, −6, 91), **zakładając zrównanie końców wałków** dwóch różnych modeli.
Sprawdzono 24 ustawienia kątowe co 15° i trzy przesunięcia osiowe. Przesunięcie
±1,8 mm jest scenariuszem wrażliwości inspirowanym różnicą 36,8 vs 35 mm
między dotychczasowym CAD serwa i kartą; **nie tolerancją producenta**.

| Przesunięcie osiowe | Próbki z przecięciem / 24 | Największe przecięcie [mm³] |
|---|---:|---:|
| −1,8 mm | 3 | 8,190 |
| 0 mm | 24 | 27,574 |
| +1,8 mm | 24 | 270,048 |

Nominalnie krzyż przecina nasadę `SupportedRoot34` we wszystkich sprawdzonych
ustawieniach. [MG92BClearanceReference.FCStd](MG92BClearanceReference.FCStd)
zachowuje to hipotetyczne ustawienie 0°/0 mm, nie propozycję instalacji.
Nie badano ciągłego ruchu, reszty kota, metalowych łączników, przewodów,
śruby centralnej ani drogi montażu. Ustawienie −1,8 mm nie jest wybraną naprawą.

**Decyzja projektowa:** zachować fabryczny orczyk i wieloklin; projektować
wymienny adapter PETG z miejscem na krzyż oraz dostępem do śruby. Najpierw
wariant nasady/adaptera, nie proste dodanie orczyka do obecnej 1 mm szczeliny.
Model Dtto pomaga rozpocząć projektowanie przestrzeni. Nie pozwala jeszcze
zatwierdzić rozstawu śrub, wysokości osadzenia ani usunąć TEMP sprzęgnięcia.
Wszystkie dziewięć plików głównego CAD pozostało identycznych bajtowo.

## Pozostałe sprawdzone źródła

- [TowerPro MG92B](https://towerpro.com.tw/product/mg92b/): potwierdza ramiona
  i śruby w komplecie, ale nie podaje zwymiarowanego orczyka.
- [Adafruit 2307](https://www.adafruit.com/product/2307): podaje 20 zębów;
  istniejący model serwa nie zawiera ramienia. Nie drukować z tego założenia
  wieloklinu dla innej partii/sklepu.
- [Botland DNG-24409](https://botland.com.pl/serwa-typu-standard/24409-towerpro-mg92b-serwomechanizm-cyfrowy-z-metalowa-przekladnia.html):
  przy odczycie 23.09.2026 dostępny, 61 szt., wysyłka 24 h, 89,90 zł.
  Zostaje bazowym wyborem **3 sztuk pozycyjnych**, nie wersji ciągłej 360°.
  Wysyłka nie jest gwarancją daty doręczenia. Niczego nie zamówiono.
- [SmallpTsai, hexapod](https://github.com/SmallpTsai/hexapod-v2-7697/tree/32d53914d916c4cb263d9942b8edd1a50e70cc82/mechanism):
  instrukcja i STL mocowań MG92B; w sprawdzonym drzewie nie znaleziono osobnego
  modelu orczyka. Nie wywodzono wymiaru części z samej kieszeni.
- [MiniKame autora MaxDuracell](https://www.printables.com/model/568010-minikame-for-mg92b-servos):
  opis deklaruje zmianę kieszeni orczyka pod MG92B; plików nie pobrano.
- [GrabCAD Jimmy Serpico](https://grabcad.com/library/servo-mg92b-1): kandydat
  modelu serwa znaleziony w indeksie, pobranie nie powiodło się. Nie zaliczono
  go jako zweryfikowanego źródła wymiarów.

## Licencja i odtworzenie

Geometria Dtto i jej wyodrębniona/transponowana referencja są udostępniane na
**CC BY-SA 4.0**, autor Alberto / otrebla333. Zachowano [licencję źródła](LICENSE-Dtto.txt).
Zmiany: wyodrębnienie dwóch brył, dodanie opisów, w drugim pliku hipotetyczne
przestawienie orczyka obok kopii podpory kota. Bez poparcia ani gwarancji autora;
materiał udostępniony tak, jak jest. Nie jest modelem certyfikowanym TowerPro.

Narzędzia `tools/cad/probe_mg92b_reference.py` i `probe_mg92b_clearance.py`
działają w świeżym Pythonie FreeCAD, zamykają własne dokumenty i odmawiają
nadpisania istniejącego pliku referencyjnego. Hashe narzędzi i FCStd są w
raportach. Do odtworzenia pobrać wskazany oryginał do ignorowanego katalogu
`hardware/cad/_supplier-research-20260923/`, zweryfikować SHA i użyć świeżego
katalogu wyników (nie usuwać zapisanych dowodów w celu ponownego uruchomienia).
