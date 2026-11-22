# Źródła części i połączeń — pakiet20Nov

**Wersja20H: źródła do warunkowego pakietu pierwszej przymiarki; FIT_S0 przed dużą podstawą.**

Wybór57pozycji bazy i7dodatków oraz mapa160połączeń pozostają zachowane.
[POLACZENIA.csv](POLACZENIA.csv) obejmuje134połączenia bazy i26ADD7;
[selected-components.csv](selected-components.csv), [design.json](design.json)
i [connections.json](connections.json) ustalają części, końce i sieci.
Pliki źródłowe zachowują historyczne projekty tras. Długości w nich nie stanowią
bieżącej listy cięcia ani pomiaru dostarczonych jednostek. Bieżący montaż:
[START_HERE](../START_HERE.md), [wejście baterii](../WEJSCIE_BATERII.md)
i [montaż elektryczny](../ELECTRICAL_ASSEMBLY.md).

| Grupa | Obsada do wspólnej alokacji |
|---|---|
| Baza i ruch | 12 ST3215, 3 MG92B, 3×608 i 1×688; obecne nogi; głowa yaw±20/pitch±10, ogonY |
| Energia nisko | 1 GEA223S30X6GT 106,5×35×21,5; 2 paski; monitor; pełne końce i droga wyjęcia |
| Ochrona | 12 pełnych MTA0300330+różne TE IN/OUT+ATO4A; 4 MTA0100335+MINIVAL10A; F0; 5 FHAC; S0/S1 z pełnym osprzętem |
| Rozdział | 4 WAGO615, 16 WAGO415, 8 inline2411, POST_F0; WAGO415 =15 bankowych+czynny PBAY_P_AUX |
| Sterowanie | Pi4+pełne porty/POWER/DATA/chłodzenie; BUS25514; MAIN4853; AUX4092; cały lutowany PCA–E1 |
| Głowa i audio | Kamera+ToF; BNO085, touch, AMP, głośnik, ReSpeaker; wszystkie po1; oddzielny USB_AUDIO i para BTL |
| Całe przewody | 3 JR300; MG250 osobno; 4 odrębne E2/JPWM225 nominal/220 dostępne z końcami; CSI według [instrukcji głowy](../GLOWA.md); DATA500 |

Aktualnie wybrany nominalny budżet materiałowy K3/r4 to3mLAPP0107001
oraz9mHELU23802: [wybór źródłowy](phase1-material-selection-r4.json).
Nie oznacza to zakupionej ani dostarczonej ilości. Fizyczne cięcia, dopasowanie
oraz luz pozostająNULL. Fabryczne końce baterii i napędów zachowuje się całe;
przygotowanie robotowegoW075 opisuje bieżąca instrukcja wejścia, z ochronąF0.

Pole druku256³zbrimem/podporami: [jedyny indeks](../PRINT.csv).
Bieżącą objętość materiału podaje [material-index.json](../material-index.json);
masa fizyczna, nośność i chód wymagają prób. Nie sumować nowych i wycofanych
wariantów mocowań. Poprzedni przewodnik źródłowy19Nov zachowano
[oddzielnie jako historię](../reference19I/source-README.md).
