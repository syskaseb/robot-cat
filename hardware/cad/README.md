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

## Wymiary serwa są zmierzone, nie zgadnięte

Wcześniejsza wersja tego pliku kazała wydrukować jedną sztukę `hip_link`,
przyłożyć do fizycznego serwa i poprawić cztery liczby, bo rozstawu śrub nie
dało się skądkolwiek pobrać. **To już nieaktualne.** Rozstawy zostały
zmierzone z oficjalnego modelu CAD serwa i potwierdzone drugim źródłem —
metoda, źródła i surowe liczby są w [measure/README.md](measure/README.md).

Najkrócej:

- **orczyk: 4 × Ø2,5 na okręgu Ø14,00**, co 90°, ustawione pod 45°. Ten sam
  wzór jest po obu stronach, bo serwo jest dwuosiowe.
- **śruby obudowy: y = ±10,25, x = +4,2 / −16,5 / −20,3** względem środka
  serwa. Tak mocuje się korpus serwa do ramy — bez żadnego pobieranego
  uchwytu.
- **oś wyjściowa leży 10,2 mm od bliższego czoła**, nie w środku. Dlatego
  płytka mocująca jest chorągiewką w jedną stronę, a nie symetryczną płytą.
- **obudowa ma 35,4 mm, nie 35,0**, a z czopami całość ma 39,6 mm. Sklepowe
  „45,2 × 24,7 × 35" opisuje samą obudowę.

Uchwytu z Printables 653674 **nie trzeba już pobierać** — cała niepewność
wisiała właśnie na nim.

## Co jest zweryfikowane, a co nie

| wartość | źródło | pewność |
|---|---|---|
| długości segmentów (110/110/25 mm) | `leg_ik.py` / `cat.urdf.xacro` | **pewne** — to własny, testowany model |
| rozstaw bioder (220×110 mm) | ten sam model | **pewne** |
| gabaryt i rozstawy ST3215 | oficjalny CAD, patrz `measure/` | **pewne** — dopasowanie okręgu z błędem 0,000 mm |
| wzór montażowy Pi 5 (58×49 mm, Ø2,7) | oficjalny rysunek mechaniczny Raspberry Pi Ltd (RP-008347-DS-1) | **pewne** |
| orientacja serwa ID1 w narożniku | — | **do sprawdzenia na fizycznej części** — rama zakłada, że wszystkie cztery serwa stoją tak samo, zgodnie z regułą „cztery identyczne nogi" |

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
