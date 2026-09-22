# Modułowe mastery CAD — plan przejścia

Data: 2026-09-22. Branch: `codex/robot-cat-mechanical`.
Status: **wdrożony pilot AUX; dalsza migracja etapami**. Rzeczywisty zakres,
dokumenty i dowody są w [cad/README.md](cad/README.md). 18 elementów ma odnośniki;
302 pozostają snapshotami. Nie przeniesiono całego robota do pełnych masterów.

## Punkt wyjścia

Zachowujemy złożenie [v35](skorupa/v35/README.md), jego źródła i dowody testów.
Nie usuwamy historycznych katalogów ani nie przenosimy ich teraz do archiwum.
Znane ograniczenia są w [STATUS.md](skorupa/STATUS.md): m.in. błędy BOP skorupy,
29 połączeń tymczasowych, nieukończone napędy głowy, orczyk ogona i wiązka.
Migracja organizacji plików nie może oznaczać zatwierdzenia tych elementów.

Baza porównawcza z commita `6033edca1519dcc0cfa9e9dce4bf6cb1bc08f964`:

| Plik | SHA-256 |
| --- | --- |
| `skorupa/v35/Kot_v35_ZASILANIE_AUX.FCStd` | `11e8c27e496032df6f556736e94699424723cef5fe0192b0ade2d152f810bdc5` |
| `skorupa/v35/AuxPower35.FCStd` | `2eb5d64a63136815bf6e066ea753a9b96a07deae4db5eb8fdd496dea7200833f` |

## Co jest masterem

Master to autorytatywny, edytowalny dokument podzespołu: jego części, parametry,
szkice z więzami, historia operacji i nazwane interfejsy montażowe. Nie jest
eksportem STL ani kolejną kopią całego kota. Jeden master może zawierać wiele
oddzielnych części do druku i referencje części kupnych; nie oznacza jednej bryły.

Przykład: `Tail.FCStd` może definiować podstawę, podparcie osi i segmenty,
korzystać z referencji serwa i łożysk oraz publikować oś obrotu i punkty mocowania.
Złożenie główne używa instancji tego modułu, zamiast kopiować jego geometrię.

Każdy moduł musi mieć opis:

- lokalnego układu współrzędnych, jednostek i nazwanych osi/płaszczyzn montażu;
- rozstawów otworów, pasowań, tolerancji i części współpracujących;
- obwiedni ruchu, miejsca na przewody, wtyki, narzędzia i demontaż;
- drogi przenoszenia obciążenia, materiału oraz numerów i rewizji części.

Wspólne wymiary mają jedno źródło: dokument parametrów FreeCAD, np. Spreadsheet
lub VarSet. Wybór mechanizmu i odwołań między dokumentami sprawdzamy w pilotażu.
Plik JSON/YAML dla testów może być eksportem tych danych, nie drugą ręcznie
edytowaną kopią. Więzy powinny wyrażać intencję projektu; samo zablokowanie
całego szkicu nie zapewnia użytecznej parametryczności.

## Docelowy układ repo

Poniżej układ docelowy, a nie wykaz ukończonych modułów. Stan rzeczywisty opisuje
README pilotażu; np. pełne mastery głowy i nogi nie zostały jeszcze wydzielone:

```text
hardware/
  cad/
    parameters/RobotParameters.FCStd
    modules/
      chassis/Chassis.FCStd
      leg/Leg.FCStd
      head/Head.FCStd
      tail/Tail.FCStd
      shell/Shell.FCStd
      electronics/PowerMounts.FCStd
    assembly/RobotCat.FCStd
  reference/                       # istniejące źródła części handlowych
  electronics/                     # schematy, PCB, wiązki, bilans zasilania
  manufacturing/                   # PETG, orientacje, rysunki, próbki
  bom/                             # numery części, rewizje, ilości
  releases/                        # manifesty wydań i wyniki kontroli
  skorupa/                         # istniejące checkpointy bez przenoszenia
  simulation/                      # istniejące modele i wyniki
  wavego/                          # istniejące materiały bazowe
tools/cad/                         # wspólne audyty i eksport, poza hardware/
```

Zależności są jednokierunkowe:

`parametry + reference → mastery modułów → złożenie → eksporty i symulacja`.

Nie tworzymy zależności zwrotnej z modułu do złożenia. Interfejsy opieramy na
nazwanych datumach, a nie przypadkowym `Face27`. Kandydatem do instancji jest
FreeCAD `App::Link`, także między dokumentami; zgodność z używanym natywnym
Assembly, ścieżkami i ponownym otwarciem wymaga sprawdzenia w pilotażu.
Cztery nogi mogą korzystać z jednego mastera dopiero po potwierdzeniu orientacji
i ewentualnych różnic stron — nie przez automatyczne lustrzane odbicie.

Geometrię części projektujemy w modułach. Relacje kinematyczne tworzymy w
złożeniu odpowiedniego poziomu, odwołując się do opublikowanych interfejsów.
Joint `Fixed` nie zastępuje śrub ani fizycznego podparcia; `Revolute` nie
zastępuje wału, łożyska i orczyka. Oba rodzaje zgodności trzeba kontrolować.

## MCP i inne metody

| Zadanie | Preferowana metoda |
| --- | --- |
| Oglądanie otwartego modelu, pomiary, szkice, operacje, datumy, złożenia i jointy | Ustrukturyzowane narzędzia FreeCAD MCP; po zmianie recompute i kontrola |
| Operacja niedostępna w narzędziach MCP | Mały skrypt Python przez MCP, z jawnymi obiektami wejścia/wyjścia i testem wyniku |
| Powtarzalne generowanie, eksport, geometria, masa, porównania i testy regresji | Wersjonowane skrypty Python uruchamiane w zgodnym środowisku FreeCAD |
| Funkcje zależne od GUI, np. widok lub część API złożenia | Aktywna sesja FreeCAD przez MCP lub kontrolowane makro; nie zakładamy obsługi headless |
| Dynamika chodu | Istniejący pipeline ROS/Gazebo; na Windows ścieżka Docker |
| Schematy/PCB i automatyczne kontrole elektroniki | KiCad i jego CLI, jeśli zostaną wdrożone; StepUp do wymiany ECAD/MCAD |

MCP jest kanałem dostępu, nie innym silnikiem CAD. Wywołanie Pythona przez MCP
i uruchomienie skryptu z FreeCAD korzystają z API FreeCAD; różnią się kontekstem,
powtarzalnością i dostępem do GUI. Unikamy ogromnych jednorazowych skryptów
przesyłanych ad hoc: trwała logika i testy powinny być w repo.

## Pierwszy pilotaż: mocowanie AUX

1. Pracować na nowych plikach, zachowując oba pliki v35 i ich sumy kontrolne.
2. Wydzielić wspólny interfejs montażu AUX. Obecny `AuxPower35.FCStd` zawiera
   również zmienione kopie płyty ramy, skorupy i mostka ogona; nie można po prostu
   przemianować go na niezależny moduł.
3. Przypisać geometrię właścicielom: otwory w płycie do chassis, otwory mostka
   do tail, przejścia skorupy do shell, dystanse AUX do power mounts.
   Wszystkie korzystają z tego samego opisu interfejsu; model płytki handlowej
   pozostaje referencją ze źródłem i rewizją.
4. Sprawdzić odnośniki, natywne jointy, recompute, zapis i ponowne otwarcie
   FreeCAD 1.1.3. Sprawdzić także odtworzenie z czystego checkoutu w innej
   lokalizacji, bez zależności od bezwzględnych ścieżek tego komputera.
5. Porównać z bazą: wszystkie 320 części, globalne położenia i geometrię,
   bilans masy, 306 Fixed + 13 Revolute, bez wzrostu 29 TEMP. Ponowić istniejące
   22 klatki testu kinematycznego i istotne kontrole kolizji. Znane błędy bazy
   raportować osobno; nie ukrywać ich za zaliczonym testem migracji.
6. Zmienić próbnie parametr montażu, sprawdzić zgodną aktualizację otworów
   i mocowań, następnie przywrócić bazę. To dowód parametryczności, nie sam
   fakt istnienia odnośnika. Wyniki zapisać przed migracją kolejnych modułów.

Kolejne moduły migrujemy pojedynczo, dopiero po zaliczonym pilotażu. Dotychczasowe
skrypty i ścieżki pozostają obsługiwane, dopóki nowy pipeline ich nie zastąpi.

## Wersje i wydania

- Stałe nazwy plików masterów; historię przechowuje Git, nie ciąg `v36`, `v37`
  w nazwach każdej roboczej kopii. Historycznych nazw nie zmieniamy wstecz.
- Osobny numer wydania konstrukcji, np. przyszłe `hw-v0.1.0`, i rewizje części,
  np. `RC-TAIL-001 rev A`. Te przykłady nie oznaczają utworzonych tagów.
- Zmianę kompatybilności otworów/pasowań dokumentujemy jawnie. Wersjonowanie
  inspirowane SemVer nie zastępuje tabeli zgodności fizycznych części.
- Manifest wydania przypina commit, rewizje BOM, wszystkie zależne mastery,
  modele dostawców, wersje FreeCAD/dodatków, sumy eksportów i dowody kontroli.
  Nie używa niezdefiniowanego „najnowszego” modelu.
- Status gotowości jest niezależny od numeru: koncepcja, prototyp, do prób,
  zatwierdzone do druku. Nie awansujemy statusu wyłącznie po animacji złożenia.
- STL/3MF/STEP i URDF/SDF są produktami pochodnymi; nie edytujemy ich zamiast
  masterów. Pliki tymczasowe, cache i automatyczne kopie nie są źródłami.
- Binarnych FCStd nie traktujemy jak łatwo scalalnego kodu. Jeden autor naraz
  na master; pracę równoległą dzielimy modułami. Git LFS można ocenić osobno,
  bez przepisywania istniejącej historii w ramach tej migracji.

## Narzędzia pomocnicze

Stan na 2026-09-22. Zainstalowano Fasteners 0.5.67 w katalogu użytkownika FreeCAD,
zarejestrowano go bez restartu i sprawdzono śrubę M2×12. Wersję/commit przypina
[toolchain](cad/toolchain.json). KiCad/StepUp, Curves, FEM i CAM pozostają
odłożone do właściwych zadań; nie dodano ich jako zależności pilotażu.

- Lokalny FreeCAD AI 0.23.1-alpha zawiera skille `fastener-hole`, `thread-insert`
  i `enclosure`, dostępne przez jego mechanizm skilli/MCP. Mogą przyspieszyć
  typowe cechy; dane konkretnej śruby/inserta i próbki PETG mają pierwszeństwo
  przed domyślnymi wymiarami. Obecność skilla nie oznacza zatwierdzenia części.
- [Fasteners Workbench](https://github.com/shaise/FreeCAD_FastenersWB):
  parametryczne łączniki. Wdrożony i sprawdzony niezależnym testem;
  na co dzień uproszczone gwinty, a nie kosztowne szczegółowe helisy.
- [KiCad StepUp](https://www.kicad.org/external-tools/stepup/): wymiana płytki,
  obrysu i modeli 3D pomiędzy KiCad i FreeCAD. Własny schemat/PCB daje więcej
  możliwości niż sam STEP kupnej płytki. [KiCad CLI](https://docs.kicad.org/9.0/en/cli/cli.html)
  nadaje się do ERC/DRC i eksportów; te kontrole nie zatwierdzają całej wiązki,
  termiki ani obciążalności instalacji robota.
- [Curves Workbench](https://github.com/tomate44/CurvesWB): opcjonalnie do
  organicznych powierzchni głowy/skorupy. To eksperymentalny dodatek, nie
  gwarancja szczelnej bryły czy prawidłowej grubości ścian.
- [FEM](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FEM_Install.md):
  później do obciążeń i ugięć, po naprawieniu geometrii i sprawdzeniu solvera.
  PETG z FDM wymaga uwzględnienia orientacji warstw, temperatury i pełzania;
  wynik dla przypadkowego materiału izotropowego nie jest certyfikacją.
- CAM jest przydatny do obróbki CNC. Przy obecnym PETG ważniejszy jest slicer,
  profil drukarki i kupony pasowania. Generatory siatek/obrazów mogą pomagać
  w wyglądzie, lecz nie zastąpią konstrukcji mocowań i wymiarowego CAD.

W przeszukanym katalogu wtyczek Codex nie znaleziono dodatkowej integracji
FreeCAD/KiCad/Fusion/Onshape. To nie twierdzenie, że żadne projekty społeczności
nie istnieją. Najpierw wykorzystujemy działający FreeCAD MCP i dodatki aplikacji.

Utworzono pięć skilli w `.agents/skills`: `robot-cat-module`, `robot-cat-petg`,
`robot-cat-assembly-audit`, `robot-cat-electronics` i `robot-cat-release`.
Korzystają ze wspólnych dokumentów/testów repo i określają wymagane dowody,
w tym niezatwierdzone pasowania, połączenia TEMP i brak danych producenta.
`AGENTS.md` i `CLAUDE.md` kierują do tych samych źródeł, bez ich duplikowania.
