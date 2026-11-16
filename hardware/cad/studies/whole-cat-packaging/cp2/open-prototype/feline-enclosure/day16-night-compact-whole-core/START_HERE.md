# Noc — pierwszy cały zwarty układ, hipoteza ODRZUCONA w obecnej alokacji

Otwórz `night-compact-whole-core.FCStd`. Jedna kopia6a, bez zmiany źródeł. Aktualne opaque przód/bok/3q i wnętrze są rzeczywistym CAD. Dwie bryły ciemnej obwiedni są **PROVISIONAL_NOT_PRINT_NOT_MASS**, nie gotową skorupą ani dowodem zmieszczenia. Wystających części nie ukryto.

## Co zmieniono jako całość

12pełnychMTA+TE/ATO obrócono długim wymiarem wzdłuż bazy:3kolumny×2rzędy×2poziomy, zakres **218,29×45,70×66mm**, zamiast250,85×194,16×28. To prawdziwe źródłowe zespoły w CAD, nie same obudowy. 15WAGO415 ma dwa krótsze banki4×2zjednympustymstanowiskiem, a16-taP_AUX pozostaje w funkcjonalnym odgałęzieniu. 4WAGO615/25komór i wszystkie5FHAC/10końców są oddzielnie zapisane. Bateria/Pi nisko; lutowanyPCA/E1 przeniesiony jednym sztywnym przesunięciem, pełneAUX9,5/MAIN zachowane. 12ST3215/nogi/źródłowa baza126 bez zmiany.

Pi ma nowe rzeczywiste pola wszystkich portów i chłodzenia. S0 przesunięto/obrócono ze wszystkimi11częściami, bez usuwania klucza/studów. Cały ogonY/MG/horn/bearing/retainers przesunięty razem do osi(140,0,130); nie sam czubek. Nowe koncepcyjne podpory odnoszą się doP01 i stałego siodła serwa głowy, nie do obracającego sięforku. To nie jest jeszcze odebrana mechanika mocowań.

Pierwsze widoki dają krótszą obwiednię **318.41×206.85×132.33mm** wobec396×238×127przedtem, ale nowa obwiednia nie oznacza zamknięcia wszystkich części; miejscami wystają. Nie ogłaszam niższego całego robota ani finalnejmasy. Wygląd do uczciwej oceny, nie przyjęty wynikOli.

## Pierwsza tania falsyfikacja całego układu

1. **P_SYS↔PCA:gap0**. Obrót pełnej kostki daje37mm wY; nie wolno było liczyć tej orientacji jako22mm. To koliduje z warstwą całegoPCA/E1, nie wymaga jeszcze żadnej nowej osi przewodu.
2. **S0body↔S1 i S0key↔monitor:gap0**. Cała zatoka obsługi jest nieprzyjęta. Nie poprawiano po kolei śrub, obudowy ani krzywej.
3. PełneCSI200: dla bieżących projektowych punktów kamery/Pi prosta dolna granica193,351mm +roboczeosadzenie10 =**203,351mm**. To odrzuca **wybrane punkty i budżet**, nie dowodzi fizycznego braku kabla ani niemożliwości wszystkich tras; rzeczywiste usta/strony styków są niepotwierdzone. Chord NIE jest długością trasy.

Zachowane lokalne separacje: głośnik–GPIO dolnagr3mm, AUXpełne–MAIN17,6mm, F_PI–S0body12,5mm. Nie przyjmują reszty układu. Nie wykonano drugiej rodziny/scalargrid po falsyfikacji.

## Źródła i niepewności widoczne przed zamknięciem

8nowych inline to osiem osobnych **nominalnych pokryw35,5×8,1×8,9mm** według odebranegoWAGOprimary, nie odlanyprostyplastik: po2przykażdejnodze; oppositeports/leverUP/strip11 ztegoSAMEGOunit. Ich dostarczone lever-open/stop/centra wymagają próby. 4złote kulki oznaczają tylko datums **pełnychniepowiązanychMTA0100335**: nie są numericznąkopertą. Stary błędnyBOXpożyczony zWAGO usunięto z operatingrepresentation, lecz nie zBOM; cztery wybrane oprawki/fuse/lid/tether/dwaUNCUTleads wymagają jednej właściwejpróbki. Nie twierdzę, że zmieszczą się w obwiedni.

4niezależneE2/JPWMmin220 oraz ich prawdziwe kontakty są zachowane w kontrakcie; stary zbiorczyE2+inlineBOX nie jest dowodem czterech końców. Samo zaznaczenie wspólnych regionów transportu nie jest dowodem pełnejzajętejprzestrzeni lub schowania zapasu. `whole-connected-groups-and-short-units.json` zapisuje wszystkie25komór/10FHACkońców i rozdziela źródłowe jednostki. Każdy factoryFHAC84,5..94,5 zawiera goły koniec; terminacje raz. XA/XBzachowują tylko istniejące właściwe rozszerzenia. K1474jednapara, W078RED210, CSI200 i5właściwychPololuparents600 nie są wspólną pulą. Wszystkie actualcuts/slackNULL.

## Masa i następna decyzja

Nowe pełne obwiednie NIE wchodzą do masy wydruku. Znany materiał zachowanych mechanizmów i nowych wspólnych struktur: **309.98g pełnegoPETG1,27**. Dodatkowo jawnie zatrzymano **833.32g poprzedniego materiału osłon jako rezerwęporównania**, aby nie „odchudzić” przez ich ukrycie. Brakuje części retencji/warstw/pełnychmocowań i metalu; nie podaję nowej oszczędności ani masy gotowego kota.

Następna jedna decyzja dotyczy **wspólnej warstwy P_SYS/PCA, całej zatoki S0/S1/monitor i relacji Pi–kamera**, z uwzględnieniem obu stron F_PI/pełnych końców. Nie nowy uchwyt, kolejna skorupa lub krzywa wokół tych samych pozy. Podpory, magazynowanie całych jednostek, układanie otwarte dwóch osób i późne pokrywy opisuje `whole-open-assembly-and-next-decision.json`. To źródło do boundedwhole-review; `wholekit=false`, `physicalPASS=false`, niezaakceptowanywygląd, brakSTL.
