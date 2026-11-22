# Aktualny KiCad: wybrany P0/E6

Edytowalny [projekt](robot_cat.kicad_pro) i [schemat PDF](robot_cat-schematic.pdf)
odwzorowują wybrane części i połączenia `robot-cat-mechanical`, nie równoległy
wariant WAVEGO z innej sesji. Nie projektujemy nowej PCB ani nie zmieniamy CAD.

Źródłem wyboru pozostaje
[pakiet fazy1](../../cad/studies/whole-cat-packaging/cp2/open-prototype/phase1-prototype-final/README.md).
Jego historyczne100% dotyczy nominalnej dokumentacji otwartego prototypu.
Nowy zakres obudowy/kładzenia/zwartych wiązek pozostaje nieukończony.

## Zachowane części i mapy

- 12×ST3215, 3×MG92B, bankR47, 23wybrane wkładki/oprawki.
- MAIN4853/5,10V do Pi4 przez K-1474 USB-C; AUX4092/6V; PWM815revC,
  SN74LVC8T245PW/adapter575070, L78L05ACZ i istniejące21elementów pasywnych.
- S0 HELLA i osobny S1 NKK S821 DPST. USB zasilania Pi nie jest GPIO2/4.
- W001–W080 oraz XA/XB/XP/XS/XL. Bieżące zaciski W5/W1/W3/W4 zastępują
  historyczne przypisania E4, m.in. P_SYS.5/F_PI i G_TAIL.5/ogon.
- Osiem istniejących221-2411 z obiema stronami. SPLICE_PI jest istniejącym
  lutowanym przejściem, nie nowym złączem. POST_F0 zachowuje osobny wybrany
  221-412 i obie porcje W076; nie jest dziewiątym przedłużeniem MTA.

`design.json` przypina źródła SHA256. `connections.csv` podaje końce;
`pinouts.csv` wiąże fizyczne oznaczenia z `ComponentID` i referencją KiCad.
`harness.csv` to porcje korpusu W5 z aktualnym nadpisaniem W003310mm,
nie ponowna lista całego stocku. Pozostałe wiązki i materiały pozostają w K3.
Nie ciąć według tabel bez przymiarki.

Referencje U10xx są wymaganymi przez KiCad oznaczeniami symboli, nie nowymi
układami do zakupu. Symboli nie sumować z BOM. Wybrane ilości są w
`selected-components.csv` i pełnym źródle K2/K3; to nie licencja na zakup.

## Granice dowodu

To schemat montażowy modułów. Pasywne kontakty modułów nie symulują ich
wewnętrznej elektroniki. Kierunki bufora/PWM/GPIO oznaczono tam, gdzie są
ustalone. Zero ERC i zgodna netlista nie oznaczają kwalifikacji prądów,
zwarć, termiki, mocowań lub ruchu.

Alarm MOD05015 ma znane logiczne role B0/B1/B2/B3, ale mapowanie fizycznych
gniazd G-Tech/ID nadal wymaga identyfikacji. Celowo brak połączenia do
zgadniętych pinów baterii. NC przy alarmie oznacza HOLD, nie rezygnację z części.
Adapter575070/U1 pozostaje warunkowy względem beznapięciowej kontroli.
E3/source/leads/clearing/transients i dostarczone styki pozostają bramkami fazy2.
Nie wykonano prób fizycznych; brak zgody na zasilanie.

## Odtworzenie

Z katalogu `robot-cat-mechanical` (KiCad10 w PATH):

```text
python tools/electronics/kicad_current.py
kicad-cli sch export netlist --format kicadxml -o hardware/electronics/kicad-current/netlist.xml hardware/electronics/kicad-current/robot_cat.kicad_sch
kicad-cli sch erc --format json --exit-code-violations -o hardware/electronics/kicad-current/erc.json hardware/electronics/kicad-current/robot_cat.kicad_sch
python tools/electronics/kicad_current.py --validate
python -m unittest discover -s tools/electronics -p test_kicad_current.py -v
kicad-cli sch export pdf -o hardware/electronics/kicad-current/robot_cat-schematic.pdf hardware/electronics/kicad-current/robot_cat.kicad_sch
```

Generator nadpisuje tylko własne pliki. Po ręcznej edycji KiCada porównaj ją
ze źródłową specyfikacją przed regeneracją. Bez skryptów historycznej integracji
WAVEGO i bez eksportu starej geometrii do aktualnego modelu.
