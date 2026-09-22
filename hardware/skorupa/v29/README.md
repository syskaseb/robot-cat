# v29 — wymienny ogon PETG, checkpoint rozwojowy

**To nie jest wydanie do druku.** Fizyczne sprzęgnięcie z dołączonym
orczykiem MG92B oraz niezależne podparcie wałka pozostają nierozwiązane.
Poprawna animacja złącza Fixed nie zastępuje tych elementów.

- `Kot_v29_OGON_PROTOTYP.FCStd`: pełny kot, natywne złożenie FreeCAD 1.1.3.
- `TailDesign29.FCStd`: edytowalne części PartDesign, szkice i model STEP serwa.
- `assembly-plan.json`: członkostwo części, osie i jawne blokady tymczasowe.
- `assembly-validation.json`: zapis wyników natywnego solvera i skróty plików.
- `fit-audit.json`: dokładne przecięcia BRep nowych części i próbkowany obrót.
- `tail-budget.json`: obliczeniowy bilans masy i momentów nowego ogona.

v28 pozostaje niezmienioną kopią wcześniejszej konstrukcji. Master i pełny
kot są osobnymi plikami: kształty w złożeniu to podpisane kopie, **nie live-link**.
Po edycji mastera trzeba odświeżyć kopie i ponowić raporty.

## Co rzeczywiście zmieniono

29 dawnych części ogona zastąpiono 43 nowymi. Pełne złożenie liczy 252 części,
238 złączy Fixed i 13 Revolute (12 nóg + ogon); 36 blokad nadal jest
tymczasowych. Dwa stare zastępcze serwa ogona zastąpił **jeden MG92B**:
razem pozostają wymagane dwa napędy głowy i jeden ogona. Serwa głowy w tej
rewizji wciąż są starymi bryłami zastępczymi.

Sześć segmentów ma zakrzywiony profil, kwadratowe wpusty 6 mm i gniazda
6,5 mm, szczelinę czołową 0,3 mm oraz poprzeczną śrubę M2×12 z nakrętką.
Ostatni segment ma zaokrągloną końcówkę. Segmenty są wymienne, ale po
skręceniu tworzą **sztywny łuk**, nie sześć aktywnych lub elastycznych stawów.
Całość odchyla jedno serwo na boki. PETG nie jest udawane gumową przegubką.

Obwiednie segmentów mieszczą się na stole 256³ mm. Luz 0,25 mm na stronę
jest punktem wyjścia do próbki tolerancji, nie gwarancją dopasowania każdej
drukarki. Minimum materiału między bokiem gniazda a zagłębieniem śruby lub
nakrętki to 1,75 mm; wymaga próbki obciążenia i oceny orientacji warstw.
Nie ma jeszcze zaleconego momentu dokręcania ani walidacji pełzania PETG.

Nowy mostek wykorzystuje cztery istniejące osie M2 ramy i pokrywy:
CAD X=112/122, Y=±22,5 mm. Nóżki podnoszą płytę ponad dotychczasowe części,
a płytkie kieszenie chowają łby pod przetwornicą. W skorupie jest poziomy
przepust dla mostka. To nie jest jeszcze finalna osłona całego mechanizmu.

Uchwyt serwa ma cztery M3 na siatce 32×32 mm, otwarcie z luzem wokół
korpusu i dwa M2 w rozstawie **27,5 mm** zmierzonym z STEP Adafruit 2307.
Płaszczyzny uszu w źródle są na Z=0 i 2 mm. Oś wyjścia to globalne
CAD **[171, −6, 91] mm**, kierunek Z; nie środek przypadkowego pudełka.

## Śruby i dostępność

Nowy podzespół zawiera w CAD 12 śrub M2×12, 12 nakrętek M2,
4 śruby M3×12 i 4 nakrętki M3. Kandydat zakupowy:
[Botland NSZ-00637, zestaw 330 szt.](https://botland.com.pl/srubki-i-nakretki/637-zestaw-srubek-podkladek-i-nakretek-330szt-5410329304478.html).
Odczyt 22.09.2026: 12,90 zł, dostępny, deklarowana wysyłka 24 h;
nie jest to gwarancja terminu doręczenia ani złożone zamówienie.
Zestaw zawiera po 20 szt. śrub M2×12 i M3×12 oraz po 40 odpowiednich nakrętek.

Geometria śrub jest uproszczoną obwiednią: łby M2 Ø4,2×2 i M3 Ø6,2×3 mm,
bez gniazd i gwintów; nakrętki są walcami opisanymi na nominalnym sześciokącie.
**Sprzedawca nie podaje wymiarów łbów** — trzeba sprawdzić rzeczywiste części
przed zatwierdzeniem kieszeni. Zestawowe podkładki nie są tu zamodelowane
ani uwzględnione w długościach zacisku; ich dodanie wymaga przeliczenia.
Dostęp narzędzia do nakrętek nie jest jeszcze potwierdzony próbą montażu.

## Test ruchu a fizyka

`RobotConnectionTest29` porusza jednocześnie 12 osi nóg o ±3° i ogonem
o ±30°. Raport musi potwierdzić 22 klatki, amplitudy, zachowanie połączeń
i powrót do spoczynku. To sprawdzenie kinematyczne, nie chód ani obciążenie.
W FreeCAD: rozwiń `RobotCatAssembly24 → Simulations`, otwórz
`RobotConnectionTest29`, wygeneruj/przelicz klatki i użyj odtwarzania.
Generowanie dużego złożenia potrafi trwać kilka minut; nie uruchamiaj
drugiego solvera równocześnie. Zapisuj checkpoint w pozycji spoczynkowej.

FreeCAD 1.1.3/Ondsel może dla formuły `.1*sin(...)` zwrócić kod 0,
ale **zero klatek**. Stosujemy `0.1`, sprawdzamy liczbę klatek i amplitudy.
Reprodukcja na niezapisanym, dwuczęściowym modelu: `probe_sim29.py`.

Audyt bada nowe części przeciw pozostałym w spoczynku oraz 13 ustawień
ogona co 5° w zakresie ±30°. Nie obejmuje wszystkich dawnych par,
ciągłego chodu, kabli, narzędzi, odkształceń ani wytrzymałości.
Natywna animacja 1-sekundowa **nie jest komendą zatwierdzoną dla sprzętu**.

Osobny eksport [Gazebo v29](../../simulation/v29/README.md) zachowuje pełną
masę i geometrię nowego ogona, ale blokuje go w pozycji spoczynkowej
na potrzeby porównania obciążeń nóg. Nie symuluje jeszcze napędu ogona.

## Odtwarzanie

W Pythonie dostarczonym z FreeCAD, nie w zwykłym Pythonie:

```powershell
& $freecadPython -X utf8 tools/freecad/skorupa/cache29.py
& $freecadPython -X utf8 tools/freecad/skorupa/audit29.py
& $freecadPython -X utf8 tools/freecad/skorupa/tail_budget29.py
```

`cache29.py` tylko czyta zapisany plik; cache jest lokalny i ignorowany w Git.
W GUI `Refresh29.FCMacro` odświeża już istniejące v29, po czym
`Validate29.FCMacro` przelicza złożenie, zapisuje je i tworzy cache/raport.
`Integrate29.FCMacro` służy wyłącznie budowie nowego checkpointu z v28
i mastera; celowo odmawia nadpisania istniejącego v29.

## Nadal do wykonania

Orczyk/śruba wałka MG92B i niezależne podparcie, obudowa mechanizmu,
sprawdzenie montażu narzędziami, próby tolerancji i obciążenia PETG.
Poza ogonem pozostają dwa mechanizmy głowy, rzeczywiste mocowania
elektroniki i serwis akumulatora; szczegóły w [STATUS](../STATUS.md).
