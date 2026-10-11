# Jeden udokumentowany kandydat adaptera U1

Adafruit1208, projekt `28-pin SOIC+TSSOP.brd`, nie obecny niejednoznaczny575070.
Producent: https://www.adafruit.com/product/1208
Repozytorium: https://github.com/adafruit/Adafruit-SMT-Breakout-PCBs
Commit: `dbd7a1928c2b668a9edf3d53277063eac4c3e938`.
Pobrano11.10.2026 około22:10UTC bez zmiany pliku.
SHA256 BRD: `0e5c355106d9531b9e28526dc643164064becfd8aef09f2118e39866ad792f87`.
Zachowane oryginalneREADME i licencjaCC-BY-SA3.0; projekt LimorFried/Adafruit.

Wynik wyprowadzenia jest w obecnym body-harness-checkpoint/u1-documented-adapter.json.
Weryfikator sprawdza ciągłość28grafów ścieżek przy środkach padów, w tym przelotki.
To analiza projektu źródłowego, nie ERC/DRC, pomiar dostarczonej płytki ani fizycznyPASS.

Układ pozostaje TI SN74LVC8T245PW, TSSOP24, rysunekPW0024A4220208/A02/2017:
https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf (SCES584D, maj2026).
Raster0,65mm; rozpiętość wyprowadzeń6,2..6,6mm; wysokość maksymalna1,2mm.
Adapter ma17,78×35,56mm z obciętymi narożami, nie30,48×17,78mm.
Raster otworów2,54mm, rozstaw rzędów15,24mm, otwory1,016mm.
Grubość1,6mm pozostaje założeniem projektu, nie pomiarem/katalogową tolerancją.

Używamy wyłącznie stronyTSSOP. W plikuEAGLE jest ona spodemMR0;
patrząc na nią po odwróceniu płytki pin1 ma być po lewej u góry.
Chip24 należy przesunąć o0,65mm wzdłuż footprintu28, wyrównując pin1 doP$1.
Chip1..12 trafia naP$1..12, chip13..24 naP$17..28.
Zewnętrzne otwory: chip1..12 = EAGLEJP2.1..12;
chip13..24 = EAGLEJP1.12..1. NIE traktować nadruku28 jako numerów chip24.
JP1.13/14 iJP2.13/14 pozostają niepodłączone; nie zwierać ich ani nie mostkować.

Kandydat NIE WYBRANY: nie zmieniono obecnego BOM, E4 ani natywnego mocowania.
Przed wyborem wymagane: dopasowane izolujące mocowanie bez otworów wymyślonych
w płytce,24aktualne końce/lokalne elementy/odciążenia, wspólna kontrola montażu
oraz uzgodnienie materiałów. Po dostawie: zgodność artworku, grubość,
kontrola lutowania i ciągłości bez zasilania. Brak zakupu lub deklaracjiE1.
