# Ogon — studium bocznego dostępu do nakrętki

2026-09-22, baza `98f466e`. **Koncepcja, niezainstalowana w robocie. Nie do druku.**
To nie jest gotowy orczyk ani zamknięcie istniejącego TEMP. Wszystkie dziewięć
plików głównego CAD pozostaje identycznych bajtowo. Cały kot wygląda jak na
[aktualnym PNG](../../validation/before-tail-coupling.png).

## Co zaprojektowano

[TailCouplingService.FCStd](TailCouplingService.FCStd) zawiera niezależną kopię
historii `SupportedRoot34` i nową kieszeń `SideLoadingNutPocket`. Nie ma
zewnętrznych odnośników do złożenia. Nowy szkic ma wymiary, położenie i pełne
więzy, bez `Block`; dwa odziedziczone szkice pozostają bez zmian. Widok:
[service-root.png](service-root.png).

Materiał części: PETG. Układ globalny zgodny z robotem, jednostki mm:

| Interfejs | Wymiary nominalne CAD |
| --- | --- |
| Oś czopa | X=171, Y=−6, kierunek Z |
| Nowa kieszeń, otwarta ku +X | X=171…179, Y=−8,85…−3,15, Z=95,9…98,4 |
| Szerokość / wysokość szczeliny | 5,7 / 2,5 |
| Istniejąca nakrętka M3 | AF 5,5; wysokość 2,4; Z=96…98,4 |
| Zachowana płaszczyzna oparcia nakrętki | Z=98,4; kontakt około 17,118 mm² |
| Gabaryt nasady | 49,399 × 28 × 31 |

Kieszeń wykonano ustrukturyzowanymi narzędziami MCP. Narzędzie automatycznie
wybrało odwrotny kierunek wycięcia; niezależne porównanie wykryło błąd.
Poprawiono `Reversed=False` przez API, ponieważ `modify_property` odrzucało
wartość logiczną jako tekst. Końcowa bryła dokładnie odpowiada zamierzonemu
wycięciu, a nie temu pierwszemu, błędnemu wynikowi.

Ubyło 40,151 mm³ PETG. **Zachowanie powierzchni oparcia nie oznacza zachowania
wytrzymałości**: nacięto boczną ściankę kołnierza. Potrzebne są ocena obciążeń,
warstw i pełzania oraz fizyczna próba. Nie zmieniono średnic czopa i łożysk.

## Sprawdzony zakres serwisowy

[service-audit.json](service-audit.json) obejmuje:

- ścisłe BOP, jedną poprawną bryłę, brak dodanego materiału i pustą różnicę
  brył w obu kierunkach względem oczekiwanego wycięcia;
- trzy w pełni związane szkice; świeże otwarcie wyłącznie przeniesionego pliku,
  przeliczenie i brak zależności od innych dokumentów;
- wsuwanie samej nominalnej nakrętki od środka X=180,5 do X=171: 39 próbek
  co 0,25 mm. Uwzględniono obwiednie 320 części robota; dokładne przecięcia
  były potrzebne tylko dla nasady i podstawy serwa;
- kontrole dodatnie: pierwotna nasada blokuje tę drogę, a pozostawiona śruba
  osi również blokuje nakrętkę. W wariancie bez śruby nie znaleziono przecięć
  większych niż 0,001 mm³;
- niezmienione oparcie nakrętki i sumy kontrolne wszystkich dziewięciu plików
  głównego CAD. Audyt nie zapisuje żadnego dokumentu CAD.

To **próbkowana droga nakrętki**, nie ciągła obwiednia ruchu, dostęp palców,
narzędzi czy przewodu. Nie uwzględnia niezamodelowanego orczyka. Nie wykonano
nowych prób kinematyki/Gazebo, ponieważ wariant nie został zintegrowany.
Dotychczasowe wyniki ruchu nie zatwierdzają nowego wariantu.

Do takiego montażu trzeba podeprzeć ogon i wycofać `SpindleBolt34`, zanim
nakrętka zacznie się przesuwać. Demontaż zabezpieczenia osi na obciążonym
ogonie jest niewłaściwy. Planowana procedura jest na zdjętym podzespole,
nie obietnicą dostępu pod kompletnym kotem. Cała kolejność montażu łożysk,
pokrywki, orczyka i śrub wymaga jeszcze sprawdzenia.

## Czego brakuje do rzeczywistego sprzęgnięcia MG92B

Obecny model Adafruit zawiera obudowę i wałek, **nie dostarczony orczyk**.
Wałek kończy się na Z=91, a nasada zaczyna na Z=92; zmierzona minimalna
odległość brył wynosi około 1,0604 mm. Nie wolno uznać tego za miejsce
wystarczające dla dowolnego orczyka. Po poznaniu jego geometrii mogą być
potrzebne zmiany wysokości lub podcięć, a następnie nowe testy całego modułu.

Źródła sprawdzone 2026-09-22:

- [TowerPro MG92B](https://towerpro.com.tw/product/mg92b/): gabaryty serwa,
  informacja o dołączonych ramionach i śrubach; brak zwymiarowanego ramienia.
- [Adafruit 2307](https://www.adafruit.com/product/2307): komplet z orczykami;
  ta referencja podaje 20 zębów. Nie przenosić tej informacji automatycznie
  na podobnie nazwane warianty innych sprzedawców.
- [Przypięty model Adafruit](https://github.com/adafruit/Adafruit_CAD_Parts/tree/6f52ee4d48df0e7118d2d82f485cb572051a24fe/2307%20MicroServo%20MG923B):
  katalog nazwany `MG923B`, istniejący model referencyjny MG92B w projekcie.
  Brak osobnego modelu orczyka w tym katalogu.

Do zamknięcia interfejsu potrzebne są zdjęcia z góry/boku i pomiary dokładnie
tego orczyka, który przyjdzie z wybranym serwem:

1. Rodzaj ramienia, jego obrys, grubość i średnica/wysokość piasty.
2. Wysokość obu powierzchni ramienia po pełnym osadzeniu na serwie.
3. Odległości środków otworów od osi, średnice otworów i dostęp od spodu.
4. Śruba mocująca do wałka: gwint, użyteczna długość, łeb i głębokość otworu.

Wieloklin pozostaje fabryczny — nie zaprojektowano drukowanego zamiennika
na podstawie podobnego serwa. Nominalna nakrętka CAD także wymaga porównania
z zakupioną sztuką; 0,2 mm luzu szerokości szczeliny nie jest potwierdzonym
pasowaniem wydruku PETG.

## Druk i kolejne kroki

Gabaryt mieści się w 256³ z dużym zapasem, lecz brak zatwierdzonej orientacji
i slicingu. Płaska podstawa od spodu jest kandydatem do prób, nie zaleceniem
produkcyjnym: trzeba sprawdzić most szczeliny, gniazdo nakrętki, okrągłość czopa
i obciążenie warstw. Profil drukarki, dysza i filament nadal nie są określone.

Najpierw zmierzyć orczyk i rozwiązać jego połączenie/śrubę, potem ocenić
osłabienie kołnierza, wydrukować próbkę i dopiero integrować. Nowy wariant
nie zastępuje automatycznie części w `modules/tail/TailSupport.FCStd`.

Powtórzenie audytu w świeżym Pythonie dostarczonym z FreeCAD 1.1.3:

```text
python tools/cad/tail_service_study.py audit
python tools/cad/tail_service_study.py package
python tools/cad/release_check.py hardware/releases/tail-service-study.json
```

Manifest przypina pliki i dowody. `--require-print-ready` ma odmówić.
Pełny zestaw ROS/narzędzi: 656 testów zaliczonych, bez pominięć, trzy istniejące
ostrzeżenia bibliotek; cztery nowe kontrole spójności dowodów tego studium.
