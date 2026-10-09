# CP2: kompletna mechanika ogona, nie wiązka

Ten pakiet przygotowuje M3 do hobbystycznego prototypu. Nie zamyka W4/W5,
nie zatwierdza druku ani obciążeń i nie stwierdza fizycznego PASS.
Wynik można zaliczyć dopiero po przejściu wszystkich kontroli i utworzeniu
`selection.json`/`manifest.json`, nie za samą podporę.

## Jedna konstrukcja

Mostek i cały ogon zachowują podniesienie15mm. Cztery pierścieniowe dystanse
Ø7/otwór2,6/wysokość19mm stoją na istniejącej płycie P0: osieX112/122,
Y±22,5, Z38,52..57,52. Przenoszą obciążenie na ramę, nie na elektronikę.
PrzejściaØ7,6 w dopasowanej LowerCarrier nie zaciskają dystansów.
Nie instalować dawnych wysokich podpór elektroniki OpenDeckSupports.

Monitor pozostaje w tylnym polu pomiędzy podporami: nominalny cały obrys
X108..149, Y−12,5..12,5, Z42,92..54,92. Podłoga zagłębienia ma1,8mm,
cztery podparcia brzegowe1,4mm; minimum nominalnego odstępu od mostka1,08mm.
Stare cztery podparcia monitora usunięto, pozostałe otwory płyt zachowano.
Dwie zachowane T18I111-02370 przechodzą przez integralne mostki nad podłogą,
nie pod płytą przez podkładkę ramy. Pas2,5×1,2mm, długość145mm.
Pełny kanał poprzeczny3,2mm ma lokalną podłogę minimum1,6mm; pozostała
podłoga zagłębienia zachowuje1,8mm. Kanały wykonano odejmowaniem materiału,
bez nowego kontaktu z otoczeniem; dwie pary pas/płyta sprawdzono ponownie.
Nominalny prostokątny obwód96,24mm plus25mm zapasu. Główka4,8×4,5×3,5mm to budżet
producenta, nie dokładny BRep otworu zapadki. Własne zazębienie pasa/główki
jest zamierzone, nie kolizja dwóch różnych części. Po dostawie obowiązkowa
przymiarka obudowy/padów/wyjść, lekkie zapięcie bez ściskania elektroniki.

## Montaż i rozbiórka

1. Na pustej ramie, przed nogami, baterią, spodem, elektroniką i górnym
   modułem ogona, przygotować istniejące otwory według receptury P0.
   Otwory ramyØ2,05 wymagają wykończeniaØ2,4 po druku; nie zmieniono osi
   ani nie wycinano półek ram dla uzyskania przejścia.
2. Zastąpić cztery tylne wspólne śruby P0 przez M2×30, nie dodawać kolejnego
   zestawu TailFrame. Zachować4nakrętkiAF4/H1,6 i8podkładekØ5/Ø2,2×0,3.
   Cztery przednie śruby P0 pozostają bez zmian. Konkretny nowy element:
   Rosentaler0200912020030, DIN912 A2-70 M2×30, pełny gwint30mm, łebØ3,8/H2,
   imbus1,5. Wkład zakupowy to4instalowane+1zapas, sztuki; nic nie kupiono.
3. Na każdym boku wprowadzić X122 przed X112. Śruba opuszczona30mm:
   podłeb5,22, tip35,22; wprowadzić od wnętrza30mm wzdłuż+X i podnieść30mm.
   Pionowe wsuwanie od samego spodu jest odrzucone: dolna półka ramy blokuje
   główkę. Podkładka dolna jest wprowadzana razem, nie przez otwór ramy.
4. Założyć dopasowaną dolną płytę, cztery dystanse i mostek. Docelowo:
   podłeb35,22, tip65,22, górna podkładka60,52..60,82, nakrętka60,82..62,42.
   Nominalne zazębienie1,6 i wystawanie2,8mm; rzeczywiste wybiegi/tolerancje,
   szczęki kluczaAF4, imbus i lekki docisk PETG sprawdzić w fazie2.
5. Monitor/opaski założyć przed górnym modułem; nie wciskać nieznanych
   padów ani pinów. Podpory dotyczą nominalnej zewnętrznej obwiedni.
6. Na stole złożyć zachowany moduł ogona: serwo BODY na dwóch M2×12,
   dolne nakrętki przed obudową, łożyska/spacery/wrzeciono i wymienny
   adapter R5 z jednym drukowanym orczykiem R2; potem obudowę, pokrywę
   i sześć biernych segmentów. Zachowany wewnętrzny kit ma44tożsamości.
   Nie montować starego proxy orczyka obok nowego, nie dublować starych
   śrub TailFrame. Jeden z trzech wspólnych orczyków MG92B przypada ogonowi.
7. Dopiero potem przykręcić kompletną podporę do mostka czterema M3×16
   i zamontować górną elektronikę. Przewody nie biegną przez obrót wrzeciona.
   Ich pełne połączenia/odciążenia do korpusu są nadal otwartym W4/W5.
8. Odłączony, niezasilony prototyp rozbierać w odwrotnej kolejności.
   Głęboki demontaż wspólnych śrub wymaga rozebrania do pustej ramy; nie
   obiecuje się wyjmowania całej płyty z podłączoną wiązką ani rutynowego
   rozpinania74zacisków do wymiany bezpiecznika.

## Edytowalność, zakres i dowody

Aktualny zespół to `TailAssemblyCurrent.FCStd`. Zmieniona LowerCarrier
i dystans mają szkice/Pad/Pocket. Mostek i lokalna podpora zachowują swoją
edytowalną historię Part::Cut/Fuse; nie są nową siatką. Adapter R5 i orczykR2
mają skopiowane natywne źródła i lokalne linki. Niezmienione części/śruby
wewnętrzne to jawne geometryczne referencje z przypiętego starego zespołu,
zachowane źródła edytowalne wskazane w selekcji. Nie twierdzi się, że cały
kot jest migrowany do nowego solvera Assembly.

TailRise15→16→15 wiąże podpory i całe położenie ogona. Natywny parametr
TailYaw obraca grupę wokół osi[171;−6], bez przesuwania osi serwa.
Sprawdzane są13położeń −30..+30° co5°, nie ciągły sweep ani próba obciążenia.
Stałe połączenia wewnętrzne bez zmian korzystają ze wcześniejszych dowodów;
nowy R5/orczyk/podpora i relacje do aktualnego CP2 sprawdzane są ponownie.
Niezależny proces otwiera kopię w innym katalogu, sprawdza linki i parametry.
Eksporty mieszczą się z marginesem10mm w256³; slicer i druk to faza2.

Odrzucono boczną kieszeń/opaski przy listwie, przednią kieszeń przy MAIN,
trasę śrub od dołu oraz opaski pod płytą. Nie usuwać tych konfliktów przez
ignorowanie realnej bryły. Trzy dawne nakładania ogólnych rezerwacji PCB
na ich własne podpory nie dowodzą nowej kolizji; dla zmienionej płyty
kontrolowany jest dodany materiał oraz pełne nowe części/obwiednie.

Fizyczne dopasowanie MG92B/splajnu/retencji osiowej, moment i pełzanie
PETG oraz pomierzone przewody pozostają jawnymi bramkami fazy2. Zakres
licznika M3 dopuszcza wymienny PROWIZORYCZNY adapter; nie jest to
zniesienie tych bramek ani elektryczne zatwierdzenie E3.

## Wynik i zmierzony czas09.10

Praca ręczna, hookOFF:13:55:24→15:08:27UTC, do końca kontroli natywnego
modelu73min03s ściennych, nie czasCPU.13położeń/350par:0kontaktów,
0błędów geometrii. Pełny ruch595,391s, naprawa zależności14,203s,
końcowe otwarcie w niezależnym procesie19,797s.17lokalnych linków,
0zewnętrznych;61części zachowuje15→16→15,33ruchome części parametr yaw.
Pierwsze otwarcie kopii ujawniło11zewnętrznych linków R5/orczyka.
Skopiowano rzeczywiste edytowalne źródła i wykazano dwustronną różnicę
brył<0,00001mm³, więc nie ponawiano13położeń. Nie ukrywać tej naprawy:
`tail-motion-checks.json` zachowuje pełny wynik ruchu i błąd pierwszego
otwarcia, `tail-assembly-checks.json` dokumentuje lokalizację,
`tail-reopen-checks.json` końcowe niezależne sprawdzenie.
Po bramkach pakietu M3 daje4/20=20%,+5pp. Pozostałe16rezultatów
nie zostało w tym pakiecie zaliczonych; W4/W5 nadalOPEN.
Zastosowano cad-layout-planning: wspólny układ podpór/monitora/montażu,
bez wycinania ramy i bez zmiany sprawdzonego ogona dla pojedynczego kontaktu.
