# WAVEGO kot — jeden pakiet do suchej przymiarki, 15.11.2026

**Najpierw P00 i małe próbki. To nie jest komplet mocowań całej elektroniki ani gotowy zasilony robot.** Nie drukować od razu wszystkich dużych części. Zestaw zawiera 23 elementy konstrukcji oraz 5 narzędzi/próbek do przymiarki (w tym P00); to wykaz warunkowy, nie polecenie wydrukowania wszystkiego. Fizyczne przymiarki, druk, cięcie przewodów i próba ruchu nie zostały wykonane. Nie stosujemy dawnej oceny „1/10”.

[Karta przymiarek](FIT_CHECKS.md) prowadzi przez jedną sesję pomiarową. [Mapa mocowań](MODULES.md) pokazuje, które moduły nadal nie mają mocowania. [Końcowe uwagi Beauvoir i Zeno](AUDIT_NOTES.md) oddzielają ocenę wykonalności od wyglądu.

PRINT_INDEX.csv wybiera jeden aktualny plik i ilość dla każdej części. P10/P12/P19 są z odebranego carriera z15.11, pozostałe części ramy to niezmienione referencje z jego indeksu. Starych P10/P12 z frame-fastening nie używać. Duża rama służy warunkowej przymiarce konstrukcji, nie ustala pasowania wszystkich modułów.

## Co można wykorzystać

- Podstawa na rzeczywistych osiach WAVEGO, P00 i mocowanie panelu S0.
- Wspólna rama, odsunięcie BUS od chłodzenia Pi, integralne podpory Pi, tacka baterii i dwa prawdziwe przeplecenia całych pasków. Paski zatrzymują poprzeczki połączone z podłogą.
- Aktualne P10/P12/P19 oraz małe próbki. Próbki nie są częściami instalowanymi.
- Widoki otwartej konstrukcji i propozycji Oli. Zeno widzi poprawę krótkiej szyi/dolnego obrysu; odsłonięto złote obramowania oczu. Podobieństwo pozostaje częściowe. Nie ma gotowych druków skóry.

assembly/CURRENT_CONDITIONAL_CARRIER.FCStd to odebrany carrier. Pozostałe moduły pokazano jako propozycję. **Stara reprezentacja AUX w tym modelu obejmuje sam PCB; następny układ wymaga pełnych9,5mm, w tym1,8mm pod płytką.** Ten model nie dowodzi wolnego miejsca dla obsadzonej przetwornicy. Odrzuconej dolnej stopy MAIN/AUX nie ma w częściach montażowych. Nowsza CAŁA tylna warstwa jest w 03-PROPOSAL-NOT-FOR-PRINT/: oba pełne moduły i śruby mają lokalnie potwierdzoną przestrzeń, ale kolejność montażu nadal ma HOLD przez integralne P11. To odrębna propozycja, bez nowych STL. Nie stosować jej pozycji jako zatwierdzonego montażu do starych druków. Najnowsze widoki całości: [przód](views/CURRENT-whole-proposal-front.png) i [bok](views/CURRENT-whole-proposal-side.png).

## Pierwsza sesja przy stole — dwie osoby

1. **P00:** A porównuje osiem osi i rzeczywisty gwint/rewizję; B sprawdza części przy odłączonym zasilaniu. Nie wiercić ani gwintować kupnej ramy, jeśli wzornik nie pasuje.
2. **Próbki:** wolny koniec prawdziwego paska przełożyć przez16,2×4,6; klamra zostaje na zewnątrz. Sprawdzić przeszycie/grubość i wydruk. Próbka Pi sprawdza słupek/nakrętkęM2.5; M2 — nakrętkę oraz bezpieczne oparcie przy otworach rzeczywistej płytki. Nie naciskać IC/lutów. MTA sprawdzać z całymi TE/ATO według osobnej instrukcji, jeżeli próbka jest dołączona. Próbki nie zatwierdzają nośności.
3. Po zgodnych próbach złożyć gołą podstawę/ramę według instructions/foundation.md i carrier-and-strap-anchors.md. Pełne nakrętki/podkładki wsunąć dostępnymi wejściami PRZED płytkami/bankami. Nie prowadzić narzędzia przez elektronikę.
4. Pełne dwa paski włożyć w kotwyP19 przed ogniwem. Ogniwo lub nieprzewodzący wymiarowy zamiennik PRZED zamknięciemP12: otwór ma30mm, ogniwo35mm. Nie ma pionowego drop-in po zamknięciu. Okablowany zestaw i późniejszy częściowy demontaż trzeba sprawdzić z prawdziwymi końcami; bez wirtualnego odpinania lutowanych modułów.
5. Rozłożyć pełne moduły/końce na otwartej ramie: długości, izolacja, chłodzenie, dostęp doS0/bezpieczników i ręczny ruch nóg. Nie zasilać niezamocowanej elektroniki. Moduły bez gotowych podpór pozostają na stole lub w nieprzewodzącym wzorniku podtrzymywanym wyłącznie do przymiarki.

Źródłowe instrukcje w instructions/ są zachowanymi kopiami i mogą wymieniać stare katalogi lub etapowe ograniczenia. Dla nazw STL i ilości stosować wyłącznie główny PRINT_INDEX.csv. Odbiór tacki nie jest odbiorem całego robota. Szczegóły źródłowe służą odczytaniu wejść nakrętek i kolejności; nie przywracają odrzuconych geometrii.

## Co blokuje cały zestaw

| Brak | Następny konkretny krok |
|---|---|
| MAIN/AUX i tylna warstwaP11/P13/S0/E2 | Nowa wspólna otwarta warstwa na rzeczywistym P11 mieści pełne moduły/śruby. MONTAŻ nadal HOLD: wybrane pionowe pola narzędzi trafiają w integralną belkę; nie dowodzi to niemożliwości wszystkich kluczy. Trzeba zamknąć całą zależność root płaszczyzny ↔ AUX ↔ P11 ↔ dostęp M2 albo zaprojektować prawdziwy podział nośny P11. Druga oś root leży pod AUX, więc samo „złożyć PCB na stole, potem przykręcić całość” nie jest przyjętą kolejnością. Bez kolejnych pojedynczych offsetów/skracanego pola klucza. Fabryczne M2/#2, bezpieczne oparcie do przymiarki. |
| BankiMTA/WAGO/FHAC, częśćaudio, S1/monitor | Wspólne podpory zaplanowano, retencja niegotowa. Sprawdzić jeden fabryczny kołnierz/zatrzask MTA zTE/ATO przed powielaniem. WAGO: czynne dźwignie/porty; adapterówDIN nie kupowano. |
| Nośna głowa/rogi serw | Na jednym prawdziwym MG92B zmierzyć ucha, oś, wysokość osadzonego fabrycznego rogu i użyteczne otwory; potem mostek. Otwórłożyska8mm nie jest wyjściem serwa. Kosmetyczna maska nie podtrzymuje głowy. |
| Końce, masa/ruch i osłony | FIT1–FIT3 poniżej, potem skorupa. Nie ogłaszać braku przewodu z cięciwy ani narzucać starego55mm jako wymogu użytkownika. |

FIT1: rewizja/osiem osi/gwint WAVEGO, masa i ręczny zakres ruchu.
FIT2: rzeczywiste końce/fabryczne długości/luz, ochrona/F0, izolacja/dostęp/bateria/chłodzenie.
FIT3: paski/klamry, druk/bezpieczne polaPCB, MTA, rogi/łożyska, CSI/optika i makieta Oli.
Actualfit/cut/slack nieustalone. Kupnych części, ochrony i fabrycznych końców nie usunięto.

## Druk i zapotrzebowanie

STL wmm, bez skalowania. Zamknięcie/dodatnią objętość sprawdzono w źródłach; kopie są bajtowo identyczne. Z0 nie oznacza druku bez podpór. Duże części wymagają sprawdzenia orientacji/podpór na posiadanej drukarce po próbce; slicingu nie wykonywano.

HARDWARE.md i source-lists/ rozdzielają nominalne zapotrzebowanie od potwierdzonego zapasu. Niczego nie kupiono. Nie skracać śrub ani nie przedłużać fabrycznych przewodów dla modelu. provenance.json wskazuje źródła; historyczneHOLD nie są alternatywnymi wariantami do wydruku.
