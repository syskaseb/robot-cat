# Obecna rama — lokalna pojemność zasilania

Otwórz `power-capacity.FCStd`. Nie ma nowych druków, metalu ani przesuniętych modułów. STL/BOM/ilości pozostają w `day15-frame-fastening`; dokładne piny w `source-pins.json` — bez kolejnej kopii siatek.

**P12: CLOSED_SCOPED dla pojemności.** Prostokąt 13,8×6,8 nie jest dostarczonym przewodem. Dwa pełne profile Ø6, odstęp 1 i margines zewnętrzny 0,4 przechodzą przy rzeczywistym P12: ciągły konserwatywny cover ma minimum **1,259124 mm ≥1,25**. Rzeczywista krawędź X=−10 wymaga X≥−8,75. Obrót przekroju wyprowadzono z przestrzeni i promienia: dopuszczalne 16,835–17,878°, wybrane 17,357°. Na prostej przed łukiem przekrój łagodnie wraca do dotychczasowego ułożenia; pierwotny łuk R24 i jego końce nie są przesunięte. Analityczna dolna granica R żyły: **24,784748 mm**. Zachowano wszystkie profile/marginesy, nie wycięto pustych naroży jako rzekomego przewodu.

`capacity-plan.json` opisuje C1 roll, krzywiznę, ciągły odstęp i pokrycie normalnych dysków przez odcinki z analityczną rezerwą odchyłki. `capacity-result.json` sprawdza pełny P12 i rzeczywistych sąsiadów; dodatkowe 60 granic pokrywa pełne metale. `P12-local-capacity-section.png` jest przekrojem Z94 z krawędziami z aktualnego CAD, a `local-continuous-cover.png` pokazuje cały lokalny cover. Przekrój nie zastępuje ciągłego testu. To pojemność projektowa OD6/R24, nie producent ani fizyczny PASS; rzeczywiste wyjścia baterii nadal FIT2.

**Dalsza droga: OPEN.** Po zamknięciu P12 odebrano wyłącznie brakujące relacje. Pierwszy nowy HOLD: prostokątny `POWER_F0_SHORT_INPUT_APPROACH` vs P10 — common **180 mm³**, gap0. To konflikt wybranego pola 10×12×14 przy niepotwierdzonym kierunku końca F0, nie stwierdzenie kontaktu fabrycznego przewodu ani niemożliwości wszystkich dróg. Zatrzymano kontrolę zasilania; górny dostęp po tym kluczu NIEODEBRANY. Nie zmieniono F0, P10 ani nie podjęto drugiej rodziny.

**Materiał ramy/audio: CLOSED_SCOPED.** Niezależnie dokończono wyłącznie brakujące klucze addedmaterial/audio: 2050 nowych granic, 2168 starych dodatnich relacji reużytych przy identycznych operandach, bez nowego konfliktu. Poprzedni XT60 jest wyłącznie zapasem mating/wire; jego bieżący pełny obszar 50×24×18 ma osobny odebrany dowód. Zachowano stare negatywy; nie powtarzano 30metali/10feedów/31narzędzi/15parting ani R12audio84+21. Wynik nie przyjmuje całego okablowania ani retencji wszystkich modułów.

## Montaż dwóch osób i następny krok

1. A podtrzymuje wspólną ramę, B ładuje pełne nakrętki/podkładki i skręca połączenia przed PCB/bankami. Używać zestawów z przypiętego BOM; nie przeliczać starych długości śrub z identyfikatorów obiektów.
2. Przewody układać w otwartej ramie przed P15/BUS i późnymi osłonami; profil nie wymaga przeciągania całego złącza przez zamknięty kanał. P14 z dotykiem pozostaje stały, E1 nie jest rozlutowywany. Podana pojemność nie jest zaciśniętym odciążeniem.
3. Przy dostępie do baterii: rzeczywisty USB mikrofonu/P15, następnie rzeczywiste końce BUS/P13, XT60 oraz zachowany interfejs balancera przed wyjęciem baterii. Kierunek/zakres rozłączenia i wyjmowania pozostają FIT2; dopuszczony częściowy demontaż.

Najmniejszy następny krok: związać rzeczywisty końcowy interfejs/odcinek F0 z dostępną otwartą stroną P10 i połączonym obszarem XT60. Nie przesuwać tego samego pudełka ani nie zmieniać druku automatycznie. W075 nadal ≤50 projektowo, bez przyjmowania dawnych 30/70/545 za wykonane cięcia; brak przedłużenia, pożyczania długości lub nowego złącza. Dopiero po tej decyzji kończyć pozostały dostęp zasilania i prostą retencję PCB/audio/banków/baterii.

FIT1: rzeczywiste 8osi/gwinty/rewizja i stożki śrub; FIT2: rzeczywiste porty, końce/długości/R/odłączanie balancera/F0/G1/USB/4niezależnych220 i obu MTA; FIT3: chłodzenie/retencja/masa/ruch i obrys. Wszystkie 57pozycji, audio/czujniki, ochrona oraz 4DATA/5plus/7G zachowane. Brak druku, zasilania, zakupów lub fizycznego odbioru. Whole layout niezwolniony; actualfit/cut/slack=NULL.
