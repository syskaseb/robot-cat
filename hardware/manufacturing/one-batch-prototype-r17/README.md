# R17: lokalne mocowanie XB11

R16 zachowany. Dodano jeden wymienny wydruk: AuxSpliceShelfR2×1.
Wynik:65 zadań,98 części PETG,4 próbki,103 pozycje zakupowe.
WAGO221-412:1 montowane+1 zapasowe. Cztery dodatkowe T18I z istniejącego
worka100, bez nowej zaciskarki, śrub/nakrętek czy zmian P0/Deck.
Wszystkie64 poprzednieSTL pozostają te same. F_HY jest obniżone3mm na
półce; nie utrzymywać równocześnie starego położenia93..105Z.

Źródła/model/STL/PNG i wyniki w aux-splice-shelf-r2; kolejność montażu
w assembly.json. Nominalnie poprawna lokalna konstrukcja, nie fizyczny
PASS. Nieznane rzeczywiste wyjście/OD przewodu FHAC oraz klatki WAGO
pozostają jawnie warunkowe do przymiarki i lokalnej korekty wymiennej półki.
Cała faza1 nadal otwarta: upstreamXB11, XA02–06, pętla głowy R31,5,
pozostałe logiczne SKU/zakończenia i zabezpieczenia.

Poprawka wiązki: R16 zbyt szeroko przypisał HELU0,5mm² doXP02.
R17 unieważnia tylko to mapowanie: JPWM_IN zachowuje fabryczne czerwone
Molex2147612112/2147632112 i czarne2147611112/2147631112.
Nie zaciskać silikonuOD2,1mm w stykach dla izolacji1,42..1,85mm.
Dokładny obowiązujący wyjątek w wire-material-overrides.json;0 nowych SKU.

Następny krok: pełna droga XB11 od P_AUX do tej półki z odciążeniami,
bez przeciskania przewodu przez szczeliny opasek; potem pętla głowy.
Nie ponawiać kolizji zamkniętych brył bez nowego wejścia.
