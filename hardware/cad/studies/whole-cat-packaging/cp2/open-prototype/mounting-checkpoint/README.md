# Bieżące mocowania otwartego prototypu, etap 2

Aktualna kopia: **RetentionMountsAssembly.FCStd**. Jedyna bieżąca lista
wydruków w `mount-current-set.json`: **10 geometrii / 26 sztuk**, nie
wszystkie historyczne STL w katalogu. To mocowania modułu, nie cały kot.
31 śrub, w tym2M2×10 dla U1;20par/40kawałków20×10mm SJ4570 jako kandydat
retencji WAGO od spodu.40opasek przez dźwignie nie należy do tego zestawu.
Monitor zachowuje2opaski. Nie kupowano osprzętu ani materiałów.

Stan: **przygotowanie prowizorycznych mocowań etapu2 kompletne**, zgodnie
z jawną zgodą na regulowany/wymienny uchwyt i bramkę po dostawie. Nadal
**bez gotowości do druku i bez fizycznego PASS**. Dopasowanie U1, klejenie
WAGO i rzeczywiste obciążenia NIE są zatwierdzone. Przed drukiem lokalnego
mocowania U1 należy zmierzyć dostarczony adapter i dopasować parametry.
Minimum zweryfikowanej fazy 1 nadal 3/20 = 15%, bez punktów za fragmenty.

### Aktualna retencja i kolejność

U1 obrócony270°, środekX88/Y28. Integralna wąska podniesiona półka
X77..97/Y11..45/Z87,52..90,02, dystanse4mm,2wpuszczane nakrętki od góry.
Cały zaprojektowany pierścień oparcia obu stóp ma podparcie; otwarta
kieszeń nakrętki pozostawia74,882997% nominalnego pierścienia. Nie jest
to ocena wytrzymałości. Krótki nominalny L-klucz ma wspólną obwiednię
60°/3mm unoszenia przy osadzonych śrubach; brak kontaktów z otoczeniem.
**U1 montować przed MTA nad nim; pełne wykręcenie śrub wymaga zdjęcia MTA.**
Nie dowodzi to serwisu już połączonej wiązki ani konkretnego kupnego klucza.

`shared-retention-mount-checks.json`:30zmienionych par,0kontaktów/0błędów,
parametry otworów/wysokości i przeniesione otwarcie poprawne,3zamknięteSTL
z brimem5mm mieszczą się w256³. S1 i4MTA pozostają na miejscu. Wariant
boczny z kontaktem rzeczywistych końcówekS1 odrzucony, zapisany wGit
`a813d8a`; nie wybierać go ani nie drukować.

WAGO zachowują istniejące listwy i XY;20podkładek ma nominalne pełne
200mm² podparcia. Typowe2,49mm z karty3M2024, projektowy limit miejsca3mm,
nie tolerancja producenta. Położenia końców przewodów muszą uwzględnić
podniesienie korpusów w następnym etapie. Klej NIE zastępuje odciążenia
przewodów. Dokładne bramki/montaż są w aktualnej liście i planach U1/WAGO.

## Co rzeczywiście sprawdzono

- MAIN: absolutne Z46,52, cykl4→5→4, przeniesione otwarcie; zachowana
  geometria źródła i poprzedni eksport.
- Płyty: wzory rzeczywistych otworów, cztery zaciski wolnych odcinków P0,
  cztery powierzchnie oparcia po65 mm². Dolne nakrętki wpuszczane przed
  montażem Pi; dojście do dwóch tylnych nakrętek góry bocznym kluczem,
  nie odrzuconą nasadką od dołu.
- Dwie boczne listwy, cztery podpory i dolna płyta z integralnymi ramionami:
  88 wybranych par, bez kontaktów materiału, błędów operacji ani przecięć
  zapisanych rezerwacji. Położenia20 WAGO nominalne, nie model dźwigni.
- BUS:117 poprawnych brył po skopiowaniu i transformacji sprawdzonych
  osobno. Surowy zbiorczy BRep pozostaje nieprawidłowy i nie był operandem
  wspólnej operacji. Tekstowe `116` w dawnym `known_bounds` jest nieaktualne;
  wynik liczbowy raportu to117. Nie nadpisujemy przypiętego dowodu.
- Monitor przeniesiony na ujemną stronę Y; zachowana jawnie prowizoryczna
  przestrzeń wtyku USB-C i wyjęcia BUS jest wolna. To nie zmierzony wtyk.
- PWM:16 zmienionych par bez kontaktów,19 obrysów maksymalnych elementów
  bez przecięcia nowego stosu/narzędzi. Płaska podkładka jest podzbiorem
  poprzedniej; usunięto4,072013 mm³ niepotrzebnej cienkiej tulejki,
  dodano0. Śruby pozostają M2×14, pod łbem Z85,3202, zazębienie1,6 mm,
  wystawanie1,4998 mm. Podkładka nie daje prawa do zasilenia.
- Edytowalne szkice/cechy, cykle parametrów i otwarcie przeniesionej kopii.
  Każdy wybrany STL zamknięty/jednoskładnikowy, z brimem5 mm mieści się
  w256³. Największa dolna płyta194×191,50×9 mm z tym marginesem.

Mocowania mają własne mastery i linki; odniesienia płyt/sprzętu to zapisane
bryły dostawcy lub jawne rezerwacje. Nie jest to migracja całego robota do
natywnych więzów solvera. P0, R47, E6, 15 napędów i MG92B zachowane.

## Zachowane historyczne blokady i ich obecna dyspozycja

Poniższy opis dotyczył zestawu `MountsCurrent/7e1e64f`. Karta/mapa U1
nie pojawiła się magicznie: nieznane dane pozostają bramkami dostawy.
Do przygotowania prowizorycznego prototypu użytkownik zatwierdził uchwyt
parametryczny. Retencję przez dźwignie zastąpiono podkładkami od spodu.
Nie traktować poniższych dawnych recept jako aktualnych części do druku.

1. **U1/Kamami575070**: obrys30,48×17,78 i raster2,54 są podane przez
   [dostawcę](https://kamami.pl/en/Adapters-SMD-DIP/575070-sop24-pcb-adapter-for-dip24-5906623456895.html).
   Brakuje grubości i mapy obu stron/padów/spoin oraz punktów bezpiecznego
   podparcia. `population.json.adapter_stack.insulated_support_accepted`
   nadalfalse. Nie projektować klipsa przez nieznaną miedź ani udawać,
   że rezerwacja miejsca jest mocowaniem sztywnego modułu PWM/U1.
2. **Retencja WAGO**:40 opasek i sloty to recepta, nie sprawdzony chwyt.
   Zdjęcia z zapisanej karty221-415 pokazują dźwignie na górze; opaski
   przełożone przez cały korpus mogą je blokować. Karta nie wymiaruje
   punktów osi obrotu ani obwiedni ruchu. Starych dowodów banku nie
   przenosić na nowe położenia. Nie zatwierdzono opasek przez dźwignie.
   [Fabryczny uchwyt221-505](https://www.wago.com/global/installation-terminal-blocks-and-connectors/mounting-carrier/p/221-505)
   jest tropem, nie wybranym zamiennikiem. Nie dokładamy go do BOM bez
   uzgodnienia mocowania, wymiarów i wersji221-615.
3. Dostarczone spody PCB/spoiny, AUX, wtyk, narzędzia oraz pasowania,
   ściany/warstwy, pełzanie i izolacja PETG wymagają prób bez napięcia.
   Pełna wiązka/długości/stock i elektryczne bramki należą do innych prac,
   nie służą do sztucznego wypełnienia tego okna.

Następny checkpoint wymaga osobnej zgody: **etap3 wiązki**, rzeczywista
mapa U1/krótkie końce, niezależne odciążenia, pełne trasy/długości/stock.
Nie ponawiać MAIN, fundacji, tylnej nasadki ani niezmienionych listw.
Zmiany U1/WAGO unieważniają dawne wysokości końców, nie całe zachowane CAD.

## Integralność i wydanie

Aktualne wydanie: `retention-release.json`; kontrola pakietu
`tools/cad/package_open_prototype_retention.py`, wynik w
`retention-integrity-checks.json`. Kontrola integralności musi przejść,
`--require-print-ready` nadal musi odmówić. `mount-release.json`, poprzedni
README/lista i ich47pinów pozostają historycznym snapshotem7e1e64f wGit.
Nie uruchamiać starego weryfikatora jako wyboru obecnego zestawu: cofnąłby
listę do8geometrii i opasek przez dźwignie. Historyczne CAD zachowano.

Historyczne kopie i odrzucona tulejka są dowodami, nie dodatkowymi częściami
do druku. Źródła historyczne zachowane; bez pushów, maila i resetu limitu.
