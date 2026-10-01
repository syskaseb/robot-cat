# R33 — komplet nominalnego interfejsu Pi/BUS

Ten wariant można wybrać dopiero po zerowych trafieniach w końcowym
`pi-interface-final-r2/checks.json`, sprawdzeniu eksportów i integralności.
Zastępuje PiTray, Deck i Carrier; dodaje jeden BUSBracket. Pozostałe części
R32, w tym Shelf E2, zachowane. Docelowo 71 zadań /110 części PETG /4 próbki.
To przygotowanie hobbystycznego prototypu, nie fizyczny PASS ani koniec fazy1.

Pi podniesione o7mm, PCB nominalnie Z52..53,6. Oryginalne cztery przeloty
Ø2,9 i kieszenie AF5,3 zachowane, ponownie odjęte po dodaniu uchwytów kabli.
Cztery M2,5×16 z istniejącymi podkładkami/nakrętkami. Północne dwa M3×10
zamiast M3×8 podtrzymują również zdejmowany mostek BUS; południowe M3×8
zostają. Nakrętki M3 obrócić zgodnie z kieszeniami zacisków o30° względem
nakrętek Pi. BUS: cztery M2×12, nakrętki AF4 i podkładki ID2,2/OD5/t0,3.
Osi BUS nie zaokrąglono do idealnego prostokąta; pochodzą z oficjalnego CAD.

| Żyła | Fizyczny pin Pi | Drugi koniec |
|---|---:|---|
| XL01 | 1 | LOGIC3V3.in |
| XL10 | 6 | G_LOGIC.in |
| XL07 | 11, BCM17 | OE.in |
| XL05 | 3, SDA | PCA JP3.3 |
| XL06 | 5, SCL | PCA JP3.4 |

Pololu1992 to pełna obudowa2×20, NIE kodowana. Oznaczyć pin1 i sprawdzić
ciągłość przed zasilaniem; piny5V2/4 puste. Pięć brązowych fabrycznych
Pololu1871 26AWG/nominalnie600mm z etykietami na obu końcach; zacisku Pi
nie przerabiać, drugi koniec dociąć i przylutować po przymiarce. Dokładne
długości i dodatkowe30mm przy jedynym rozłączanym końcu zawiera wiring-card.
R10 na izolowanych GPIO, R2 na krótkich wyjściach lutowanych; pięć koszulek
15mm z osobnymi uchwytami. Nie zaciskać opaski na gołej miedzi.

Zasilanie: MAIN5,10V/GND_OUT bezpośrednio do USB-C Pi, nigdy na J8 ani do
AUX. Jeden K-1474 1m dzielony z wejściem MAIN; część do Pi nominalnie około
290mm z końcami/zapasem, nie dawne25cm. Oddzielne izolacje dwóch lutów oraz
JEDNA wspólna koszulka3/8 na izolowanej parze, zakład6mm. Obkurczać poza PETG.
Lanberg500mm USB2A/C do Waveshare25514: nie ciąć, bez zasilanego huba;
R24, nadmiar luźno odłożyć na uchwycie. Zapas serwisowy pochodzi z tego
samego nadmiaru, nie dodawać drugiego kabla ani drugiej pętli60mm.

Montaż bez napięcia: nakrętki od spodu, zaciski/tacka/BUS i śruby, następnie
opaski, płytki, przymiarka wiązki i lutowanie/izolacja, na końcu wtyki.
12 nowych T18I z istniejącej paczki. Powiększony uchwyt SDA mieści koszulkę.
Nowy powrót czerwonego modułu E2 zastępuje TYLKO jego poprzednie segmenty:
pętla R11,1 przesunięta3mm, wejście/zakończenie/odciążenia zachowane; budżet
150mm sprawdzony ponownie, bez podwójnego doliczania luzu.

Wyjęcie tacki: odłączyć wszystkie źródła i USB, zdjąć osłonę, rozpiąć J8,
USB-C Pi i USB BUS. Uwolnić opaski zasilania; odsunąć wolny przewód Pi,
który w pozycji roboczej zasłania klucz południowej śruby. Odkręcić cztery
śruby tacki, zdjąć wspólny mostek BUS z płytką, podnieść tackę15mm.
Nie ciągnąć za lut ani wyciągać tacki z zapiętymi wtykami/opaskami.
Sprawdzono ciągłą drogę bryły; ruch luźnych przewodów i ręki to próby fazy2.

Dokładne SKU/łączniki, końce, źródła, zapasy i jawne założenia są w
`../../electronics/full-cat/pi-interface-final-r2/`. Fazę1 nadal zamyka
13/20=65%, bo Pi to część W5. Pozostały E3/E4/W5/K2/K3/A2/A3.
Faza2: slicer na256³, PETG/próbki, pasowania złączy/śrub/koszulek,
prowadzenie po dostawie oraz pomiary elektryczne/termiczne. ROS w fazie3.
