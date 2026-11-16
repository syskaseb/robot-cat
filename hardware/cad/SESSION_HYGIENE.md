# Sesja FreeCAD: dokumenty i pamięć

## Bieżący zakres i bezpieczeństwo sesji — 16.11.2026

Wejście organizacyjne: [pierwsza karta WAVEGO](../HOBBY_COMPLETION_PLAN.md). [Fit bez zasilania](../first-fit-2026-11-15/START_HERE.md) i [niezbudowana propozycja tyłu ASSEMBLY HOLD](studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-whole-rear-layer-proposal/START_HERE.md) są oddzielone; nie otwierać ich jako dwóch konkurencyjnych masterów.
Ostatni odebrany zapis propozycji to `day15-whole-rear-layer-proposal/whole-rear-layer.FCStd` (commit `46547bfb`); zapis nie oznacza print-ready ani physical PASS. Liczba jedenastu dokumentów poniżej dotyczy dawnego E6, nie wymogu aktualnej sesji. `current-assembly.json` ma jawny zakres legacy i odsyłacze do bieżącej karty.
Nie zamykać ani zapisywać dokumentów przy cleanupie. Właściciel CAD zabezpiecza swoje zmiany i zależności; jeden autor, jeden bieżący model. Nie zabijać cudzych procesów ani nie usuwać checkpointów/odzyskiwania. Kosztowna próba wymaga konkretnego zadania i uprawnienia do pracy, nie samego historycznego NEXT.
Zasady ochrony dokumentów, odnośników i zasobów poniżej nadal mają zastosowanie w swoim zakresie; historyczne nazwy modeli nie nakazują ich ponownego otwierania.

## Historia sesji E6/P0 i poprzedników


Nie zostawiać poprzednich wersji otwartych po zakończeniu porównania. Kopia
na dysku nie wymaga otwartego dokumentu. Nie uruchamiać drugiej instancji GUI
tylko po to, żeby odzyskać połączenie MCP.

## Zwykły zakres sesji

Po zmianie uszu E1 `current-assembly.json` wskazuje `RobotCatEars.FCStd`:
jedenaście dokumentów, czyli poniższe dziesięć zależności R4 oraz nowy
`HeadEars`. Nadal otwieramy jeden cały kot, nie poprzednika obok niego.

Po integracji R4 poprzedni punkt wejścia wskazywał:
`assembly/RobotCatTailCartridge.FCStd`, dziesięć dokumentów (jeden robot,
osiem wcześniejszych zależności i nowy `TailCartridge`). Poniższe dziewięć
dotyczy zachowanego poprzednika. Nie otwierać poprzednika obok bieżącego kota.

`assembly/RobotCat.FCStd` wczytuje obecnie dziewięć dokumentów: złożenie,
parametry oraz siedem modułów. To jeden robot, nie dziewięć wersji robota.
Listę kontrolować przez MCP `list_documents` przed i po pracy; wzrost liczby
zależności musi wynikać z jawnej zmiany architektury, nie z kolejnych prób.

- Dokumenty użytkownika i niezapisane zmiany nie są automatycznie zbędne.
  Przed zamknięciem ustalić właściciela, ścieżkę i stan zapisu. Niezapisane
  zmiany zachować do osobnej kopii i sprawdzić ją przed zamknięciem; gdy ich
  pochodzenie jest niejasne, poprosić o decyzję. Nie zapisywać ich automatycznie
  na masterze. Flaga modified po wczytaniu nie dowodzi zmiany konstrukcji.
- Tymczasowe dokumenty utworzone przez bieżącą operację zamykać w `finally`.
  Nie zamykać podłączonych modułów używanego złożenia. Domyślnie jedna ciężka
  próba geometrii naraz; nie pozostawiać pracujących prób po zakończeniu zadania.
- Kosztowne BOP, importy historycznych wersji i próby napraw prowadzić w
  osobnym procesie Python dostarczonym z FreeCAD. Wyniki zapisywać w katalogu
  studium, bez zapisu źródłowego FCStd. Proces ma zakończyć się po raporcie.
- OCP i FreeCAD ładować w oddzielnych procesach; wymieniać pliki BRep,
  nie obiekty bibliotek OCCT. Nie instalować pakietów do Pythona aplikacji.

## Kontrola zasobów

**MCP execute_code a odnośniki:** FreeCAD AI 0.23.1 robi tymczasowe SaveAs
obsługiwanego dokumentu. Nawet po przywróceniu FileName zależne PropertyXLink
mogą zachować ścieżkę `AppData/.../FreeCADAI/backups/*.ai-backup.FCStd`.
Migrację/zapis całego złożenia wykonywać z MCP przypiętym do pustego,
niezależnego dokumentu roboczego, nie do jednego z podłączonych modułów.
Przed zapisem sprawdzić/zresetować dotknięte odnośniki do kanonicznych
właścicieli; po zapisie sprawdzić XLink w Document.xml i świeże przeniesione
otwarcie. Pusty dokument roboczy zamknąć na końcu. Nie nadpisywać w tym celu
historycznych modułów ani nie zapisywać ich kopii AI jako nowych masterów.

Na początku, po ciężkich etapach i na końcu sprawdzać liczbę procesów GUI,
liczbę dokumentów, WorkingSet (fizyczny RAM), PrivateMemory (prywatną pamięć
zadeklarowaną procesu), wolny RAM systemu i miejsce na dysku. Tych dwóch
liczb pamięci procesu nie dodawać do siebie. Pojedynczy odczyt nie dowodzi
ani wycieku, ani stabilności; porównywać stan po zakończeniu obliczeń.

Zamknięcie dokumentów nie gwarantuje natychmiastowego oddania całej pamięci
przez FreeCAD/OCCT. Jeśli pamięć rośnie po kolejnych zakończonych próbach,
wstrzymać nowe ciężkie operacje, sprawdzić pozostawione dokumenty i procesy.
Restart GUI dopiero po zabezpieczeniu zmian i sprawdzeniu kopii; nie wymuszać
zabicia procesu ani zatwierdzać odrzucenia zmian w ciemno. Przy małej ilości
wolnej pamięci lub miejsca nie zaczynać nowego kosztownego etapu.

Nie usuwać kopii odzyskiwania ani checkpointów w ramach porządkowania RAM-u.
Ich usunięcie zwalnia dysk, nie pamięć otwartych dokumentów, i wymaga osobnej
decyzji użytkownika. Po pracy zostawiać aktywne bieżące złożenie całego kota.
