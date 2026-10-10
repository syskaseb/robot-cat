# Aktualna kompletna gałąź F_PWM, CP2

Jeden wybór lokalnego E2, nie całej wiązki ani dopuszczenie do zasilania.
Aktualny model i eksporty wskazuje `selection.json`; wcześniejsze pliki
z nazwą Selected/Assembly są odrzuconymi odbiorami, NIE wyborem.
P0, bank R47, 15 napędów, M2/M3/M5 i wymienne adaptery MG92B zachowane.

## Obwód i końce

P_REAR.4 po S1 → XP01 HELU23302 0,5mm² → F_PWM0242.100UAT1 →
XP02 źródłowy Molex2147612113 → JPWM_IN1 → Molex2147632113 →
pad wejściowy Adafruit1608/U_PWM pin3. Powrót pin2 przez2147631113,
JPWM_IN2 i2147611113 do G_TAIL.3. Wszystkie cztery fabryczne leady
225±5mm, minimum220mm; zastępują poprzednie długości, nie dodatkowe żyły.
Nie obcinać przed pełną przymiarką. Cavity1/2 identyfikować oznaczeniem
producenta i ciągłością, nie widokiem lewo/prawo. Bez pinoutu zewnętrznego U1.

P_REAR środek18/0/138 i G_TAIL28/−35/141, oba skierowane na +X.
Każde stare podejście pozostałych W5 do tych dwóch złączek jest unieważnione.
W4/W5 nadal OPEN. To te same sieci elektryczne, nie nowe równoległe wyjścia.

XP01 nominalny blank34mm obejmuje12mm odizolowania przy WAGO i22mm
do zakładu lutu. Cały konserwatywny odcinek przed elementem48,4mm ≤50mm,
wliczając obnażenie i korpus wkładki. Bez dodatkowej pętli przed wkładką.
WAGO zaciska żyłę niecynowaną. Lutowane zakłady4mm, osobna izolacja obu
lutów: RNF-100-3/32-0-STK blanki20+20mm; zewnętrzna
RNF-100-3/16-0-STK blank50mm, końcowo42mm i zakłady co najmniej5mm.
Przy PCB dwie RNF-100-1/8-9-STK po15mm, końcowe OD≤2,8mm.
Obkurczać poza PETG. Nominalna geometria nie jest pomiarem gotowych koszulek.

## Mocowanie i montaż

Wymienna platforma na trzech kolumnach i3M3x12,3nakrętkachM3 AF5,5/h2,4,
3podkładkach OD7/ID3,2/t0,5. Pełny stos i2,1mm końca śruby uwzględnione.
Jedna zamienna górna płyta CP2, nie druga płyta obok M5. Dziesięć T18I
111-02370 zastępuje dawny zestaw10opasek, nie dodawać go drugi raz.
Klej korpusów WAGO nie jest odciążeniem żył. Opaski chwytają izolację,
koszulkę lub obudowę złącza, nigdy miedź, luty, pady ani dźwignie.

1. Usunąć baterię oraz USB i połączenie monitora/balansu. S0 OFF nie
   oznacza odłączonej strony wejściowej.
2. Na GOŁEJ, niezłożonej górnej płycie osadzić platformę i boczne nakrętki;
   śruby dokręcić od dołu przed Pi/BUS i spiętrzeniem płyt. Dojście narzędzia
   przez zainstalowaną Pi jest odrzucone. Opaski przełożyć przed przewodami.
3. Zmontować i zaizolować pigtail na stole. Fabryczne kontakty osadzić
   w430250200/430200201, oznaczyć obwody i sprawdzić ciągłość bez zasilania.
4. WAGO korpusami na pełnych podporach, mocowane wymiennymi polami tesa4965
   205µm nominalnie. Projektowy luz0,2mm jest założeniem docisku, nie wymiarem
   katalogowym; przymiarka po dostawie wymagana. Klej ma tylko utrzymywać
   izolowany korpus. Wszystkie obciążenia kabla przejmują osobne opaski.
5. Ułożyć oba wyjścia modułu z R≥11,1mm, krótkie końce do rzeczywistych
   otworów padów1,2mm. Lutować dopiero po przymiarce podpartego PCB.
   Zachować niezależny chwyt przyPCB i pełne podparcie otworów płyt.
6. Założyć dziesięć nowych opasek z umiarkowanym dociskiem, bez zgniecenia
   izolacji. Zespół płyt montować zgodnie z M5; nie zakładać późniejszego
   dostępu do zasłoniętych łbów śrub.

Serwis: całkowicie odłączyć źródło/USB, uwolnić P_REAR.4 i G_TAIL.3,
podtrzymać izolowane końce i przeciąć właściwe opaski, nie przewody.
Uwolnić obudowę, podtrzymać obie połówki i nacisnąć zatrzask; nie ciągnąć
za kabel. Jeżeli przewody stawiają opór, wyjąć podparty górny moduł/PCB
i rozpiąć na stole. Naprawa mocowania wymaga powrotu do gołej płyty.
Sprawdzona rezerwacja korpusu +Z10mm i−Y15mm oraz przestrzeń palca są
nominalnym planem, NIE dowodem ciągłego ruchu przyłączonych przewodów
ani katalogowym wymiarem dźwigni. Pozostałe W5 muszą zachować te przestrzenie.

## Wykonanie i granice

Dwa aktualne edytowalne Body, natywne szkice/operacje, próba parametru
i przeniesione ponowne otwarcie. Eksporty mieszczą się w256³ z brim5mm.
Orientacja aktualna, podstawą w dół; długa platforma i miejsca pod chwytami
wymagają podpór ocenionych w slicerze w fazie2. Oczyścić kanały i kieszenie,
sfazować krawędzie styku izolacji. Nie deklarować gotowości druku ani wytrzymałości
PETG z samej szczelności STL. Siła opasek, docisk, pełzanie, pasowanie złączy
i dostarczonych przewodów wymagają prób bez napięcia.

Zachowano model elektryczny E2: budżet wejścia20mA, nominalny spadek72mV.
Nie jest to gwarancja prądu, termiki ani selektywności. E3 i ochrona od strony
F0 pozostają otwarte. Nie podłączać baterii na podstawie tego pakietu.
W3/W5, komplet globalnych materiałów K3 i końcowy montaż A2 nadal otwarte.
Nie ma fizycznego PASS, zakupów ani resetu limitu.

Źródła fabrycznych długości: [Molex214763](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/214/214763/2147631111_sd.pdf).
Taśma: [tesa4965](https://www.tesa.com/en-us/industry/tesa-4965-original.html).
Wymiary opasek i źródła elektryczne przypięte w manifeście.
