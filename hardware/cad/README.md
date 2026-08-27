# CAD — rama i nogi, do druku

Sześć części, parametrycznie powiązanych z `cat.urdf.xacro` i `leg_ik.py`, żeby
nie mogły się z nimi rozjechać. OpenSCAD, bez zewnętrznych bibliotek.

| plik | co to jest | ile drukować |
|---|---|---|
| `thigh_segment.scad` | segment uda | ×4 |
| `calf_segment.scad` | segment goleni | ×4 |
| `hip_link.scad` | łącznik biodro→udo (25 mm) | ×4 |
| `trunk_frame.scad` | rama tułowia — drabinka, nie skorupa | ×1 |
| `pi_shelf.scad` | półka pod Raspberry Pi 5 | ×1 |
| `paw_pad.scad` | nakładka łapy | ×4, materiał do wyboru |

## Zanim wydrukujesz komplet — jedna sztuka, jedna sprawdzana rzecz

To jest jedyny krok, którego nie dało się przejść bez fizycznych części w ręku.
Dwie liczby w `params.scad` są oznaczone `ADJUSTABLE`, bo strony
Printables/Thingiverse/GrabCAD blokują automatyczny dostęp — nie mogłem ich
pobrać i zmierzyć tak jak resztę:

- **`bracket_hole_x`, `bracket_hole_y`** — rozstaw śrub, którymi uchwyt
  Printables 653674 mocuje się od zewnątrz (opis modelu potwierdza, że to
  zwykłe M3, ale nie podaje rozstawu w mm).
- **`horn_bolt_r_major`, `horn_bolt_r_minor`** — okrąg śrub orczyka. Nie
  zgadnięty: **zmierzony z prawdziwego, wydrukowanego pliku STL** innego
  projektu na tych samych serwach (`github.com/garciamathias/OpenRoboticDog`,
  plik `hip_x4.stl`) — stąd nietypowa asymetria (3 otwory w 6,7 mm, jeden w
  5,6 mm; to nie zaokrąglenie, mesh naprawdę tak ma). Realna liczba, nie
  zgadywana — ale z cudzego uchwytu na orczyk, nie z datasheetu.

**Wydrukuj jeden `hip_link.scad`, przyłóż do prawdziwego uchwytu 653674 i
serwa, popraw te cztery liczby, dopiero potem drukuj resztę.** Wszystko inne
w tym katalogu jest zweryfikowane niezależnie i bezpieczne do druku od razu.

## Co jest zweryfikowane, a co nie

| wartość | źródło | pewność |
|---|---|---|
| długości segmentów (110/110/25 mm) | `leg_ik.py` / `cat.urdf.xacro` | **pewne** — to własny, testowany model |
| rozstaw bioder (220×110 mm) | ten sam model | **pewne** |
| gabaryt ST3215 (45,2×24,7×35 mm) | DFRobot + servodatabase.com, zgodne | **pewne** |
| wzór montażowy Pi 5 (58×49 mm, Ø2,7) | oficjalny rysunek mechaniczny Raspberry Pi Ltd (RP-008347-DS-1) | **pewne** |
| rozstaw śrub uchwytu 653674 | — | **do potwierdzenia**, patrz wyżej |
| okrąg śrub orczyka | zmierzony z cudzego STL, nie z datasheetu servа | **prawdopodobne, nie pewne** |
| która strona uchwytu styka się z ramą | — | **do sprawdzenia na fizycznej części** — `trunk_frame.scad` zakłada mocowanie od zewnątrz, popraw orientację `corner_pad()`, jeśli uchwyt siada inaczej |

## Czego ten CAD NIE sprawdza

Fizycznego prześwitu między obudowami sąsiednich serw przy 25 mm odstępu
biodra. `leg_assembly.scad` to podgląd tylko do orientacji w skali — znaczniki
serw to bloki wskazujące w jedną stronę na sztywno, nie realną orientację, więc
nie dowodzą ani nie wykluczają kolizji. To sprawdza się przykładając prawdziwe
serwa do wydrukowanego `hip_link`, nie w OpenSCADzie.

## Materiał łapy

`paw_pad.scad` daje tylko kształt. Goły PETG ma za mało tarcia (mu 0,3–0,4
wobec założonych w symulacji 1,2) — montaz.pdf i tak to już mówi. Drukuj w
TPU 95A, albo w PETG i obtocz Plasti Dipem, albo zamiast drukować kup
silikonową stopkę meblową w tym rozmiarze.

## Weryfikacja i podgląd

```bash
sudo apt install openscad
pip install trimesh scipy

python3 verify.py                    # każda część: 1 bryła, szczelna, czy nie
openscad thigh_segment.scad          # podgląd interaktywny
openscad -o thigh_segment.stl thigh_segment.scad   # eksport do druku
```

`verify.py` renderuje każdą część i sprawdza w trimeshu, że to jedna spójna,
szczelna bryła — nie tylko że OpenSCAD się nie wywalił. Uruchom po każdej
zmianie w `params.scad`, zanim wyślesz coś do drukarki.

## Druk

Z `montaz.pdf`: PETG, 3–4 obrysy, wypełnienie 30–40%, warstwa 0,2 mm.
Jedno miejsce w całym projekcie potrzebuje wkładki gwintowanej M3, wtapianej
lutownicą: koniec `calf_segment.scad` (goleń), tam gdzie przykręca się
`paw_pad.scad` — otwór ma już Ø4,2 mm pod typowy wkład termiczny. Reszta
połączeń (orczyk, uchwyt bioder, półka Pi) idzie na zwykłe przelotowe otwory
pod M3, bez wkładek.
