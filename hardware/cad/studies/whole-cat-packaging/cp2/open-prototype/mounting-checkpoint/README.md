# Bieżące mocowania otwartego prototypu, etap 2

Aktualna kopia rozwojowa: **MountsCurrent.FCStd**. Jedyna bieżąca lista
wydruków jest w `mount-current-set.json`: **8 geometrii / 22 sztuki**, nie
wszystkie historyczne STL w katalogu. To mocowania tego modułu, nie liczba
części całego kota. 29 śrub; 2 górne metalowe podkładki PWM1608 zastąpione
własnymi płaskimi izolatorami PETG Ø5/Ø2,4 × 1 mm. Nie kupowano osprzętu.

Stan: **etap 2 OPEN, bez gotowości do druku i bez fizycznego PASS**.
Minimum zweryfikowanej fazy 1 nadal 3/20 = 15%, bez punktów za fragmenty.

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

## Dlaczego nie zamykamy etapu

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

Następny użyteczny checkpoint: rozwiązać **retencję U1 i WAGO**, zachowując
sprawdzone mocowania płyt. Najpierw wiarygodne mapy/model obudowy i montażu
albo jawnie zatwierdzony prosty, wymienny wariant; potem jeden wspólny
układ i tylko zmienione kontrole. Nie ponawiać MAIN, fundacji, tylnej nasadki
ani geometrii ramion/listw. Bez danych nie podajemy czasu ukończenia;
po uzyskaniu wejść pierwszy ograniczony blok planu/mocowania45–90 min,
nie obietnica zamknięcia całej fazy.

## Integralność i wydanie

`tools/cad/verify_open_prototype_integrated_mounts.py` sprawdza57 przypięć
źródeł; `mount-release.json` wiąże47 plików. Kontrola integralności
checkpointu przechodzi, `--require-print-ready` prawidłowo odmawia.
Nie uruchamiać starego weryfikatora lokalnych pięciu wydruków jako wyboru
aktualnego zestawu; wygenerowałby listę sprzed dołożenia dystrybucji.

Historyczne kopie i odrzucona tulejka są dowodami, nie dodatkowymi częściami
do druku. Źródła historyczne zachowane; bez pushów, maila i resetu limitu.
