# Podparcie ogona — moduł rozwojowy

To przeniesienie istniejącej geometrii v34/v35 do modułów, nie nowy mechanizm.
Nie zmieniono liczby serw, sześciu segmentów, osi obrotu ani śrub. Fizyczny
orczyk MG92B pozostaje TEMP. Nie ma zatwierdzenia druku całego podzespołu.

## Własność i edytowanie

`TailMount.FCStd` nadal posiada mostek `TailBridge35` z otworami AUX. Nie wolno
zastąpić go starszą kopią mostka z v34, bo utraciłby te otwory.

`TailSupport.FCStd` posiada siedem części PETG: zintegrowaną podstawę serwa,
nasadę/czop ogona, górny blok, pokrywę łożysk, dwa dystanse oraz pokrywkę czopa.
Zachowano PartDesign Bodies i ich istniejącą historię, w tym bazowe odziedziczone
bryły. `BearingSupport34` jest wejściem operacji Boolean w `ServoSupport34`,
nie dodatkową ósmą częścią do wydrukowania.

`TailPurchased.FCStd` posiada osiem źródeł geometrii dla 20 instancji łożysk,
śrub i nakrętek. Są to dotychczasowe nominalne modele, nie nowe dokładne modele
dostawców. [27 części](../../../bom/tail-support.json) to zakres tego BOM,
nie liczba wszystkich części ogona.

W złożeniu pozostają lokalne kopie serwa MG92B, jego wyjścia, sześciu segmentów
i pozostałych łączników. Dalsza migracja nie może ich zdublować.

## Interfejs i parametr

Jednostki: mm. Zachowano globalny układ CAD, bez sztucznego centrowania modułu.
Oś ogona: Z przez X=171, Y=−6; punkt jointu Z=113. Mostek AUX i jego osie śrub
pozostają w osobnym `TailMount`. Stopy podpory: X=155/187, Y=−16/+16,
cztery M3×16 od spodu mostka. Pełny stos/ograniczenia montażu są w v34.

Oba 608ZZ (nominalnie 8×22×7) mieszczą się w **górnym bloku**: Z=103…110
i 116…123. Dolna część serwa kończy się na Z=101. Wspólny parametr
`RobotParameters → Tail_bearing_interface → BearingSeatDiameter = 22.2`
steruje szkicem gniazda w górnym bloku i zachowanym szkicem wejściowej historii
podpory. Ten ostatni nie zmienia końcowej dolnej bryły po odcięciu górnego bloku.

Test 22,2 → 22,4 mm sprawdza ubytek materiału przy **obu wysokościach łożysk**,
aktualizację App::Link w złożeniu i niezmienność dolnego wspornika. Przywraca
22,2 mm i sprawdza powrót objętości. Nie zapisuje zmienionych części.
To parametr luzu otworu, nie zmiana typu łożysk, czopa, rozstawów czy pozycji osi.

Wszystkie 25 skopiowanych szkiców pozostają w pełni związane. Tylko dwa szkice
gniazd przebudowano z `Block` na położenie środka + promień z wyrażenia.
Pozostałe odziedziczone `Block` nadal ograniczają wygodę dalszego projektowania.

## Połączenia i kontrola

Natywne jointy nadal odwołują się do tych samych `Rigid_*`; ich dzieci są teraz
odnośnikami. `Rev_TailYaw29` łączy górny blok z nasadą. Pięć połączonych części
obraca się: nasada, wewnętrzny dystans, pokrywka czopa, śruba osi i nakrętka.
Łożyska są uproszczonymi nieruchomymi obwiedniami, bez modelu osobnych bieżni.

Kinematyka: 22 klatki, ogon ±30°, nogi ±3°, pomiar szczelin, osi i położeń
geometrii odnośników. To nie ciągły test kolizji, symulacja fizyczna ogona ani
potwierdzenie sprzęgnięcia orczyka. Nie dodano nowych blokad TEMP.

Dwie historie po skopiowaniu/przeliczeniu zmieniają kolejność zapisu BRep
(podstawa i pokrywa łożysk). Są sprawdzane przez ścisłą kontrolę BOP oraz pustą
różnicę brył w obu kierunkach, bez naprawy i przesuwania. Inne części porównuje
się liczbowo z podpisaną bazą. Tego wyjątku nie stosuje się do starej skorupy.

## Montaż i rzeczy pozostałe

Droga obciążenia: nasada/czop → łożyska → górny blok → integralny wspornik
serwa → mostek → rama. Orczyk ma przekazywać napęd, ale jego rzeczywisty
interfejs nie został jeszcze zamodelowany i zatwierdzony.

Podzespół składa się na zdjętym mostku. Dostęp do dwóch przednich śrub podstawy
pod złożonym kotem jest ograniczony; serwo wkłada się po pochylonej trajektorii.
Otwory, luzy, opory przewodu, mocowanie orczyka i osłona wymagają dalszych prac.
Pasowania łożysk/czopa, warstwy PETG, docisk i pełzanie trzeba sprawdzić fizycznie.
Próbki z `hardware/skorupa/v34/coupons` pozostają punktem wyjścia, nie zatwierdzeniem.

Osobno przygotowano [studium bocznego dostępu do nakrętki czopa](../../studies/tail-coupling/README.md).
Nie jest zainstalowane w tym module ani zatwierdzone do druku. Fizyczny orczyk
nadal wymaga wymiarów; nominalna droga nakrętki nie jest jego mocowaniem.
