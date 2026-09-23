# Adapter ogona R3 — zintegrowana górna obejma PETG

23.09.2026. **Koncepcja na stole, NIE zamontowana w kocie i NIE do druku.**
[Model](TailCartridgeIntegrated.FCStd), [widok](integrated-cartridge.png).
Poprzednie [R2](../tail-cartridge-service/README.md) pozostaje niezmienione.

## Konstrukcja

Górna obejma i nasada są teraz jedną fizyczną częścią PETG. Parametryczny
`PartDesign::Boolean` zachowuje obie historie; ukryte `UpperCarrierPETG` jest
narzędziem tej operacji, **nie trzecim wydrukiem ani osobnym członem złożenia**.
Dolna płytka pozostaje odkręcana, z czterema nominalnymi M2×10 i nakrętkami.
Nie sklejamy orczyka w nierozbieralnej obudowie.

- Górna obejma ma wysokość 6,4 zamiast 4 mm (Z90…96,4). Nad długim ramieniem
  orczyka lokalny dach pod kanałem nakrętki rośnie z 1,65 do 3,55 mm;
  w sprawdzonym przekroju po przeciwnej stronie zintegrowane wzmocnienie
  daje 5,65 mm. To dwie zmierzone sekcje, nie globalny certyfikat grubości ścian.
- Kanał nakrętki M3 został ponownie wycięty **po scaleniu**, żeby dodany materiał
  nie zamknął drogi serwisowej. Zachowano X167,7…174,3 i Z95,9…98,4,
  ale wydłużono wyjście z Y8 do Y16, poza pogrubione ramię (kończy się na Y13).
  [Odrzucona próba](rejected-short-channel/audit.json) z krótszym kanałem
  przechodziła kontrolę obrotu i nasuwania, ale blokowała nakrętkę przy wejściu.
  Zachowano jej model i skrypt; jest kontrolą dodatnią w ponownym audycie.
- Kieszenie łbów M2 mają 2,0 zamiast 2,2 mm głębokości. Usuwa to cienki
  pierścień 0,8 mm szerokości, który występował na wysokości tylko 0,2 mm
  ponad pełną dolną płytą. Gniazdo łba kończy się teraz na Z90.
- Śruby M2 przesunięto o −0,2 mm; nakrętki pozostają na Z98…99,6. Nominalny
  występ trzpienia spada z 0,6 do 0,4 mm. Nie jest to potwierdzenie pełnego
  zazębienia gwintu konkretnej śruby/nakrętki, których fazy nie są zamodelowane.
- Nie przesunięto rozstawu śrub, osi serwa, orczyka, czopa ani łożysk.
  Wąska przegroda 0,9 mm między kieszenią ramienia a gniazdem słupka nadal
  wymaga dopracowania; nie poprawiono jej kosztem oparcia nakrętek przy brzegu.

Zmiany cech/szkiców wykonano przez MCP. Konwersja odziedziczonego parametru
całkowitoliczbowego na dziesiętny i migracja jawnych ramek jointów wymagały API.
Położenie szkicu otworów wiąże się z `AttachmentOffset`, nie nadpisywanym
przez przywiązanie `Placement`. Jest 22 w pełni związanych szkiców.
Odziedziczona baza nasady i obwiednie części kupnych nadal są snapshotami.

## Kontrola i zakres

Wynik końcowy: kontrola warunkowa zaliczona — 13 kątów obrotu, 13 wysokości
nasuwania i 73 pozycje nakrętki bez wykrytych przecięć, dziewięć prób odtworzenia
pozycji przez natywny solver zaliczonych. Obwiednie trzpieni Ø2,5/3 przechodzą,
Ø6 pozostaje zablokowana. Zachowano oparcie nakrętki 17,118 mm². Zestaw
narzędzi CAD: 47 testów zaliczonych. To nadal koncepcja z otwartymi bramkami.

[Audyt](audit.json) wiąże model, poprzednika i skrypt sumami SHA-256. Sprawdza:

- dwie pojedyncze bryły PETG w ścisłej kontroli BOP; niezależną konstrukcję
  oczekiwanej różnicy względem R2, otwarcie z innego katalogu, zmianę wspólnego
  promienia otworów i dokładny powrót geometrii;
- 10 części fizycznych, 9 natywnych Fixed i dolną płytkę uziemioną; kolejne
  przesunięcie/obrót każdego nieuziemionego członu i odtworzenie przez solver;
- 13 pozycji obrotu od −30° do +30° co 5°, przeciw geometrii istniejącego kota,
  z potomkami nasady obracanymi razem; to próbki sztywnego ruchu, nie napędzany
  solver Revolute, dynamika ani ciągła obwiednia;
- 13 pozycji opuszczania +36…0 mm bez górnego bloku i jego potomków; wałek
  serwa pozostaje, pomijana jest tylko para referencyjny orczyk–wałek;
- 73 pozycje wyjmowania nakrętki M3, zachowanie powierzchni jej oparcia,
  osiowe obwiednie trzpieni narzędzi Ø2,5/3/6 i kontrolę blokowania przez
  pozostawioną śrubę osi.

Nie przeprowadzono nowych prób Gazebo ani prób fizycznych. Główne dziewięć
plików CAD, 29 TEMP i wcześniejsze błędy BOP skorupy pozostają bez zmian.
Orczyk jest niepołączoną referencją poza złożeniem; nie udajemy zatwierdzonego
sprzęgła ze znanym wieloklinem i śrubą.

## PETG i montaż

Dolna płytka: kandydat orientacji podstawą Z88 na stole, słupkami w górę.
Scalona nasada: kandydat Z90 na stole, czop pionowo; kieszenie od spodu
i poprzeczny kanał wymagają sprawdzenia mostów/podpór oraz ich usuwania.
Pionowy czop wymaga osobnej próby zginania między warstwami. Obie części
mieszczą się gabarytowo w 256³ mm także z 10 mm zapasu z każdej strony;
nie wykonano slicingu ani potwierdzenia podpór. Dysza, warstwa, filament
i profil drukarki pozostają nieokreślone.

Kolejność pozostaje warunkowa: orczyk i cztery M2 skręcić na stole, wsunąć
na serwo przed górnym blokiem łożysk, dokręcić rzeczywistą śrubę orczyka przez
czop przy wyjętej osiowej śrubie/nakrętce M3, następnie domknąć podparcie.
Jeśli łeb śruby orczyka nie przejdzie przez Ø3,4, wymaga wcześniejszego
założenia. Rzeczywista śruba i wieloklin nie są jeszcze potwierdzone.
Dostęp do łbów M2 od spodu po zainstalowaniu blokuje serwo; nie jest to
adapter przeznaczony do rozkręcania tych śrub bez demontażu z robota.

Otwarte: przegroda 0,9 mm, docisk/pełzanie PETG, osłabienie kanałem, gwinty,
fabryczny orczyk i śruba, tolerancje z wydruku, przewody, montaż górnego bloku,
rzeczywiste narzędzie i obciążenie ogona. Poprawa przekroju nie dowodzi nośności.

Referencja orczyka: Alberto / otrebla333, Dtto v2.0.1, CC BY-SA 4.0;
[pochodzenie i licencja](../tail-cartridge/README.md#referencja-orczyka-i-licencja).

[Dalsza kwerenda mocowania](horn-fastener-research.md): karta Adafruit potwierdza
20 zębów; BOM innego autora z MG92B wskazuje M2×6 dla ramienia. Nadal brak
potwierdzonych wymiarów łba i rzeczywistego zazębienia — nie zamknięto bramki pasowania.

## Powtórzenie kontroli

Z korzenia repo, Pythonem dostarczonym z FreeCAD 1.1.3 (nie systemowym):

```text
python tools/cad/tail_cartridge_integrated.py audit
python tools/cad/package_tail_cartridge_integrated.py
python -m unittest discover -s tools/cad -p "test_*.py"
python tools/cad/release_check.py hardware/releases/tail-cartridge-integrated.json
```

Audyt nie zapisuje dokumentów CAD. Tryb `author` jest jednorazową migracją
ramek po operacjach MCP, nie generatorem ani komendą do uruchamiania ponownie.
Kontrola manifestu z `--require-print-ready` ma zakończyć się błędem:
integralność plików i zaliczone testy prototypu nie zamykają bramek produkcji.
