# WAVEGO 19I — przymiarka i montaż

**Komplet cyfrowy do pierwszej przymiarki bez zasilania.** Znane kolizje montażowe zmienionych podstaw, pięciu opraw, dojść G1/P_FRONT oraz górnej i dolnej strony XT60 rozstrzygnięto w zapisanym modelu. Warunki pomiaru dostarczonych części są wymienione w instrukcji.

[Model FreeCAD](whole-cat19I.FCStd) · [montaż dwóch osób](MONTAZ.md) · [elektryka](ELECTRICAL_ASSEMBLY.md) · [lista wydruków](PRINT.csv) · [pełne połączenia](whole-termination-plan.json) · [zakres odbioru](decision.json)

Zestaw zawiera 50 typów STL na 70 części robota. Pięć identycznych obejm FHAC ma jeden plik. Dwadzieścia części nóg pochodzi z czterech zachowanych plików. Poza robotem jest jeden opcjonalny kupon MTA. Ustawienia względem stołu są zapisane w STL. Maksymalny wymiar wraz z rezerwą na brim i podpory wynosi 234.00 mm przy polu 256 mm. Dostępne są także 5 pliki STEP.

Dla objętości pełnego materiału model daje 1361.11 g PETG. Z dotychczasowym zakresem masy wyposażenia odpowiada to 3.215–3.955 kg dla kompletnego robota. Masę po wydruku, nośność nóg oraz ruch pod obciążeniem ustala się fizycznie.

[Widok całego robota](three-quarter.png) · [przód](front.png) · [bok](side.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png)

| Sprawdzenie w zapisanym modelu | Wynik dla przymiarki |
|---|---|
| Osiem oparć na bazie | Powierzchnie kontaktu od 73.01 do 78.48 mm². Dojście wkrętaka przy pustych podstawach i pełnym osprzęcie gimbala opisuje [pomiar](anchor-access.json). |
| G1, P_FRONT i F_PWM | Pięć zajętych wejść G1 oraz trzy czynne dojścia P_FRONT. Przy P_FRONT pozostaje 21,5 mm długości dojścia Ø4,7 mm. Półka F_PWM zachowuje oba otwory mocowania. |
| Pakiet i XT60 | Dla W075 przewidziano 45 mm dojścia i 5 mm zakończenia. Obie żyły dostarczonego pakietu potrzebują w modelu po około 208 mm przed uwzględnieniem rzeczywistych końców. Najmniejszy odstęp od przydzielonych grup przy rozpinaniu w pozycji neutralnej wynosi 7.77 mm. |
| W041 przy przednim banku | Fabryczna strona ma przydzielony dostęp do górnej złączki, a osobny przewód do P_FRONT.2 ma roboczy promień wewnętrzny co najmniej 25,5 mm. Długości i metraż są rozpisane oddzielnie dla każdej jednostki w [bilansie](source-units.json). |

W przedniej ramie pozostają cztery kotwy i pełny gimbal. Tylna podstawa niesie cztery kolejne kotwy i ruchomy ogon. Pięć projektowych obrysów FHAC ma oparcie w otwartych gniazdach. Oba poziomy G1/P_AUX są dostępne przy podpartym przodzie przed zamknięciem. Przy czynności wymiany pakietu głowa jest ustawiona prosto, a obsługa XT60 odbywa się po otwarciu pokryw. Odczepy R7–R9 wymagają przymiarki na dostarczonym JR przed przygotowaniem przewodów.

Ruch nóg w głębokich pozycjach źródłowych ma status planistyczny. Dane obejmują wcześniejszy ujemny wynik i lokalny pomiar zmienionego nadkola. Rzeczywiste ograniczniki przegubów, fizyczne dopasowanie opraw MTA, długości kabli dostarczonego pakietu oraz USB_AUDIO, chłodzenie, nadlewy USB i mapa wnęk G-Tech wymagają pomiaru. Alarm pozostawić zamontowany i odłączony. Zmierzony luz i cięcia pozostają nieustalone.
