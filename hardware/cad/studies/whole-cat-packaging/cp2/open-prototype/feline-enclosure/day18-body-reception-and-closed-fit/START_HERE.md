# Przymiarka przodu WAVEGO — iteracja 4, 18 listopada 2026

**Status całego kota: HOLD.** Zapis FreeCAD z 14:19:23 UTC zachowuje kompletny mechanizm i oba złącza JR po stronie korpusu. W pięciu badanych położeniach taśma FFC i przewód serwa pitch mieszczą się w sprawdzonych przejściach. Górny powrót czterech żył ToF przecina tył czaszki w czterech położeniach, także na wprost. Pod brodą widać wyposażenie, a z boku przerwę między głową i barkiem. Zamknięcie, wygląd i ciągły ruch pozostają do odbioru.

[Złożenie FreeCAD](body-reception.FCStd) · [Przód](frozen-front.png) · [Bok](frozen-side.png) · [Widok ¾](frozen-three-quarter.png) · [Wnętrze](frozen-interior.png) · [Przekrój](frozen-section.png)

### Co można przymierzyć

Jedyny eksport obejmuje widelec osi yaw ze wspólnym siodłem przewodu. Ponownie wczytana siatka ma jedną szczelną bryłę. W neutralnym złożeniu widelec ma 0 mm³ części wspólnej z serwem pitch, pełną śrubą poprzeczną, jej dwiema podkładkami i nakrętką. Obrys z zapasem 8 mm na stronę i 4 mm w pionie wynosi 81,43 × 107,78 × 43,00 mm. Przymiarka służy sprawdzeniu wyjścia przewodu konkretnego MG, ułożenia pełnego przewodu w siodle i montażu sworznia. [Warunkowy STL widelca](conditional-yaw-fork-MG-crosspin.stl) · [Weryfikacja siatki](fork-fit-export.json)

Siodło łączy się z widelcem na objętości 98,7 mm³, żebro nośnika Pi z podporą na 230,4 mm³, słupek ToF z podłogą na 287,0 mm³, a uchwyt przy wejściu JR z odbiornikiem na 130,6 mm³. Pełna para C_HP i trzy pola izolowanych połączeń mają po 0 mm³ części wspólnej z krawędzią piersi. Cztery nieruchome dojścia ToF i pola nieruchomych przewodów JR przeszły lokalne sprawdzenie zmienionych druków. Sprawdzenie ruchomego przewodu pitch objęło również kupne oprawy i czynne WAGO w pięciu ustawieniach yaw. [Połączenia podpór](integrated-fit.json) · [Końcowe podpory](finished-landings.json) · [Sprawdzenie kupnych części](yaw-lay-gate.json) · [Wyniki dla zapisanej geometrii](frozen-field-check.json)

### Budżet jednej rzeczywistej sztuki

| Jednostka | Podział długości w mm |
|---|---|
| FFC 200 | 10 łącznie na oba końce + 190 wolnego odcinka. Zachowane strony styków. |
| Fabryczny yaw 250 → C_HY | 11,45 przy obudowie + 223,55 nieruchomego przewodu + 15 wtyk. |
| Fabryczny pitch 250 → C_HP | 11,45 przy obudowie + 65,45 na siodle yaw + 158,10 odcinka ruchomego + 15 wtyk. Najmniejszy próbkowany promień wewnętrzny 22,33. |
| JR 300 od C_HP | 12 na wtyk + 246 wspólnego odcinka + 25 rozprowadzenia + 9 odcinka w izolacji + 8 zakładki. Trzy osobne połączenia, każde w osłonie 20 mm. |
| ToF, cztery żyły Ø2,1 | Plany EXT011/012/013/014 odpowiednio 530/530/535/525. Każda obejmuje 170 ruchomego odcinka i 12 łącznie na końce. Najmniejszy próbkowany promień wewnętrzny 31,95 w ruchu i 14,45 za wspólnym unieruchomieniem. |
| DATA 500 | 26 + 194,63 doprowadzenia + 253,37 zapasu + 26. Długość dostarczonego USB_AUDIO pozostaje do pomiaru. |

Połączenia z JR300 prowadzą dalej do G_AUX.3, F_HP.out i R2.2. Odległości 169,45 / 102,66 / 98,70 mm są dolnymi granicami do obwiedni odpowiednich zespołów. Długości dalszych przewodów HELU pozostają otwarte do ustalenia pełnej drogi i punktu R2.2 na E1. Dla wszystkich jednostek rzeczywiste cięcia, luz i dopasowanie pozostają niezmierzone. [Budżety, właściwe końce i wyniki lokalne](frozen-unit-receipt.json)

### Kolejność dla dwóch osób przy otwartym korpusie

1. Pierwsza osoba osadza mechanizm i podtrzymuje głowę. Druga zakłada pełną śrubę poprzeczną z podkładkami i nakrętką, po czym układa niecięty przewód pitch na siodle. Przy rzeczywistym serwie sprawdzają miejsce wyjścia przewodu oraz nacisk opaski.
2. Przy zdjętych osłonach druga osoba wpina kluczowane pary C_HY i C_HP na korpusie, układa nieruchomy JR300 i trzy osobne izolowane połączenia. Taśmę FFC wprowadza otwartym bokiem zgodnie ze stronami styków. Cztery żyły ToF prowadzi między wspólnymi uchwytami do rozprowadzenia przy JP3.
3. Przed zamknięciem sprawdzają dojście do zatrzasku CSI przy rzeczywistym chłodzeniu, jednoczesne osadzenie obu dostarczonych wtyków USB-A i długość USB_AUDIO do ReSpeaker. Głośnik zachowuje oba wyjścia BTL wzmacniacza. Przy JP3.2 i JP3.3 pozostaje przymiarka końca miedzi, izolacji, lutu i podkładki. Optyka wymaga próby rzeczywistej maski.
4. **Montaż zamkniętej szyi zatrzymuje powrót ToF.** Próba wspólnego wybrania w tyle czaszki oddzieliła fragment policzka o objętości 2551,74 mm³. W zamrożonym złożeniu zachowano jednoczęściowy tył z dwoma mocowaniami. Do rozstrzygnięcia pozostaje podział i mocowanie policzka wokół pełnego powrotu ToF, razem z osłonięciem szyi. W neutralnym położeniu maska optyczna i uchwyt wejścia pitch mają jeszcze 1,055 mm³ części wspólnej. [Świadkowie kolizji](frozen-field-check.json) · [Próba wybrania](finished-landings.json)

Zachowano surowe wyniki. Dawne położenie WAGO415_data_1_0 odpowiada tej samej fizycznej sztuce co obecne PBAY_P_AUX. Siedem trafień sprawdzono z czynną sztuką. Wszystkie 16 wybranych WAGO pozostaje w układzie. Cztery końcowe trafienia obwiedni PVC przy JP3 odpowiadają narożnikom oddalonym o 1,485 mm od osi otworów lutowniczych Ø1,016 mm. Ocena końców dotyczy rzeczywistej żyły i lutu. [Podstawienie czynnego WAGO](pa-aux-effectivity.json) · [Zakończenia JP3](typed-jp3.json) · [Manifest źródeł i SHA-256](verified-reception.json)
