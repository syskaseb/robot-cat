# Sesja FreeCAD: dokumenty i pamięć

Nie zostawiać poprzednich wersji otwartych po zakończeniu porównania. Kopia
na dysku nie wymaga otwartego dokumentu. Nie uruchamiać drugiej instancji GUI
tylko po to, żeby odzyskać połączenie MCP.

## Zwykły zakres sesji

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
