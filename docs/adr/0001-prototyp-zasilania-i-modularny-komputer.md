# ADR-0001: Prosty prototyp zasilania i modularny komputer

- Status: zaakceptowane
- Data: 2026-09-02

## Kontekst

Pierwszy prototyp ma działać na posiadanym Raspberry Pi 4B z Raspberry Pi OS
64-bit. Później komputer zostanie wymieniony na Raspberry Pi 5 z AI HAT+, bez
przeprojektowania całego robota i bez zmiany systemu bazowego. Napęd docelowo
tworzy 12 serw magistralowych ST3215 zasilanych z LiPo 3S. Bus Servo Adapter
(A) ma limit 5 A na torze zasilania, więc nie może przenosić prądu wszystkich
serw.

Prototyp ma być możliwie prosty. Lutowanie ograniczamy do elementów, dla
których jest potrzebne do montażu: złączy przetwornicy, złączy XT30U
oraz rozgałęzień wiązek. XT60 kupujemy z fabrycznie dołączonym przewodem.
Prąd silników nie może płynąć przez Raspberry Pi,
adapter magistrali, płytkę stykową ani przewody sygnałowe.

## Decyzja

1. Źródłem energii jest jeden wymienny pakiet LiPo 3S 2200 mAh, minimum 30C,
   z XT60. Mechanika ma dopuścić także pakiet 3000 mAh. Nie łączymy pakietów
   równolegle; dłuższy czas pracy uzyskujemy przez wymianę pakietu.
2. ST3215 są zasilane napięciem pakietu 3S przez zabezpieczony rozdzielacz.
3. Pakiet trafia przez gotową oprawkę bezpiecznika głównego 30 A i wyłącznik do
   dystrybucji z zaciskami śrubowymi. Prototyp używa listwy 30 A Botland
   KAB-06897, czterech przewodowych oprawek 10 A z zestawu KAB-05473 oraz
   wkładek 10 A z zestawu JUS-22264. Wejście od pakietu realizuje gotowy przewód
   XT60 KAB-07515. Listwa wymaga krótkich mostków przewodowych; nie jest sama w
   sobie gotowym rozdzielaczem. Cztery wyjścia zasilają po jednej nodze. Główne
   przewody i złącza muszą być przeznaczone do prądów napędu; nie używamy
   płytki stykowej ani przewodów DuPont.
4. Bus Servo Adapter (A) jest konwerterem USB-UART dla półdupleksowej
   magistrali TTL używanej przez ST3215. Przekazuje z Raspberry Pi polecenia
   ruchu do serw, rozróżnia je po unikalnych ID i zwraca telemetrię, m.in.
   pozycję, prędkość, obciążenie oraz napięcie. Nie steruje chodem samodzielnie
   i nie jest głównym rozdzielaczem prądu napędu. Zasilanie serw jest
   wstrzykiwane poza torem 5 A adaptera, a z komputerem wspólne pozostają sygnał
   magistrali i masa.
5. Raspberry Pi jest zasilane z osobnej przetwornicy Pololu D24V90F5 5 V / 9 A
   (Botland PLL-02580). Do płytki lutujemy dołączone zaciski śrubowe ARK.
   Gałąź ma zapas pod Pi 5 + AI HAT+; sposób podania 5 A do Pi 5 i ustawienie
   `PSU_MAX_CURRENT=5000` wymagają testu przed montażem końcowym.
6. Mikroserwa i audio otrzymają osobną gałąź step-down 5-6 V.
7. Prototyp używa przewodów XT60, oprawek bezpieczników i złączy śrubowych.
   Cztery rozłączne wiązki nóg muszą wstrzykiwać zasilanie poza adapterem i
   zachować wspólny sygnał oraz masę magistrali na złączu 5264-3P. Nie znaleziono
   ich jako gotowego produktu w Botlandzie, dlatego lutujemy je samodzielnie po
   ustaleniu długości w CAD-zie. Połączenia izolujemy termokurczkami NSZ-05375.
   Końce przewodów w listwie zaciskamy w tulejkach.
   Zasilanie każdej nogi odłączamy parą XT30U (wtyk + gniazdo): razem cztery
   pary. Sygnał TTL biegnie osobno. Fabryczne przewody 5264-3P serw nie
   zastępują złącza odłączającego zasilanie całej nogi od korpusu.
   Wybrana pozycja: [Kamami 581960](https://kamami.pl/zlacza-adaptery/581960-xt30u-zlacze-wysokopradowe-wtyk-gniazdo-5906623459131.html),
   5,13 zł za parę, 20,52 zł za cztery (sprawdzone 2026-09-03).
8. Na początku stosujemy prostą dystrybucję, bez rozbudowanego filtra LC i bez
   arbitralnie dobranego ogranicznika przepięć. Zostawiamy miejsce na
   kondensator zbiorczy, a dalszą filtrację dobieramy po pomiarach spadków i
   przepięć podczas testu jednej nogi oraz całego napędu.
9. Raspberry Pi 4B i Pi 5 korzystają z Raspberry Pi OS 64-bit, wymiennej tacki,
   odłączanych wiązek i wspólnego interfejsu USB do magistrali. Konstrukcja
   rezerwuje przestrzeń na AI HAT+ oraz chłodzenie Pi 5.
10. Plan zakupowy jest jednym kompletnym BOM-em i nie narzuca kolejności
    zakupów. Jedyna zapisana kolejność dotyczy komputera: posiadane Pi 4B na
    początku, a Pi 5 z AI HAT+ jako późniejsza wymiana.

## Minimalny prototyp

```text
LiPo 3S
  -> bezpiecznik + wyłącznik
  -> rozdzielacz wysokoprądowy
       -> cztery gałęzie nóg -> 12 x ST3215
       -> Pololu D24V90F5 5 V -> Raspberry Pi 4B

Raspberry Pi 4B
  -> USB -> Bus Servo Adapter (A)
  -> TTL + masa -> magistrala ST3215
```

## Konsekwencje

- Przejście z Pi 4B na Pi 5 nie zmienia magistrali serw ani zasilania napędu.
- Adapter magistrali nie pełni funkcji wysokoprądowego rozdzielacza.
- Prototyp wymaga kilku lutowanych połączeń wysokoprądowych, ale nie wymaga
  projektowania własnej płytki drukowanej.
- BOM obejmuje wszystkie 12 serw; moment zakupu poszczególnych elementów nie
  jest decyzją architektoniczną.
- Plan zakupowy musi zawierać dystrybucję na zaciskach śrubowych, bezpieczniki,
  wyłącznik, lutowane wiązki oraz przetwornicę 5 V.
- Oficjalne pozycje Botland dla zasilania prototypowego to PLL-02580,
  KAB-06897, KAB-05473, JUS-22264, KAB-07515 i NSZ-05375. Nie zamykają one
  całej wiązki: główny wyłącznik z oprawką 30 A oraz cztery wiązki wtrysku
  5264-3P pozostają obowiązkowymi pozycjami do dobrania i wykonania.

## Odrzucone warianty

- Zasilanie 12 serw przez Bus Servo Adapter (A): odrzucone z powodu limitu 5 A.
- Jeden ciężki pakiet 5000 mAh: odrzucony dla prototypu ze względu na masę.
- Przetwornica 5 V bez odpowiedniego zapasu prądowego: odrzucona ze względu na
  późniejsze Raspberry Pi 5 z AI HAT+.

## Co lutujemy, a co łączymy bez lutowania

Obowiązujący wariant montażu (2026-09-03):

| Element | Decyzja |
|---|---|
| Pololu D24V90F5 | Lutujemy dwa dołączone zaciski ARK do płytki. Przewody mocujemy w nich śrubami, nie lutujemy ich na stałe do płytki. |
| Cztery pary XT30U | Lutujemy przewody do obu połówek każdej pary. Każdy styk izolujemy termokurczką; wiązkę mocujemy, aby lut nie pracował na zginanie. |
| Rozgałęzienia wiązek nóg | Lutujemy połączenia przewód-przewód i doprowadzenia zasilania do gotowych przewodów 5264-3P. Nie lutujemy do samych serw ani nie wykonujemy ręcznie styków 5264. |
| BNO085, VL53L5CX, moduł audio | Złącza goldpin/ARK dostarczone luzem wlutowujemy raz. Złącza już zamontowane zostają bez zmian; przewody mają być odłączane. Ostateczna liczba lutów zależy od wariantu zakupionej płytki. |
| XT60 i pakiet LiPo | Bez lutowania: przewód XT60 KAB-07515 oraz fabryczne złącze pakietu. Nie rozcinamy ani nie przerabiamy przewodów baterii. |
| Listwa i oprawki bezpieczników | Bez lutowania: gotowe oprawki z przewodami, końcówki zaciskane i zaciski śrubowe. Mostki listwy wykonujemy z przewodu, nie z cyny. |
| Wyłącznik główny | Dobieramy wykonanie z zaciskami śrubowymi lub konektorami zaciskanymi, odpowiednio dobrane do prądu DC. Nie wybieramy wersji wymagającej lutowania przewodów. |
| Druga przetwornica 5 V | Dobieramy moduł z fabrycznie zamontowanymi zaciskami śrubowymi. |
| Raspberry Pi, HAT, kamera, USB, mikroserwa i Grove | Bez lutowania: gotowe przewody i złącza. Nie lutujemy wiązki bezpośrednio do Pi; komputer pozostaje wymienny. |
| Głośnik i doświetlacz | Dobieramy wersje z przewodem lub złączem. Ewentualne przedłużenie przewodu lutujemy w wiązce, nie na elemencie. |

Pod zaciski stosujemy końcówki odpowiednie dla danego zacisku i przekroju
przewodu; linek pod śrubą nie pobielamy cyną. Tulejki i konektory zaciskamy
właściwą zaciskarką, nie kombinerkami. Rozgałęzienia mocujemy poza miejscami
zginania nogi. Każde serwo ma otrzymać zasilanie z wiązki nogi; nie zakładamy,
że pojedynczy cienki przewód 5264 może przenieść sumę prądów trzech serw.
Przed podłączeniem pakietu sprawdzamy ciągłość, polaryzację i brak zwarć.
Pinout 5264 weryfikujemy względem dokumentacji, nie tylko koloru przewodów.

Ten podział nie zmienia doboru serw, pakietu, Pololu ani liczby XT30U.
Przewody, końcówki, zaciskarka i konkretny wyłącznik nadal wymagają doboru
i wyceny; dotychczasowa suma BOM-u nie jest ceną kompletnej instalacji.

Źródło montażu zacisków Pololu: [D24V90F5, Connections](https://www.pololu.com/product/2866).

## Narzędzia i materiały do lutowania

Jeśli nie ma ich już w warsztacie, plan zakupowy wskazuje stację Zhaoxin 936DH
75 W (LUT-06271), zestaw grotów 900M (LUT-09601), cynę Cynel LC60 Sn60Pb40
1,0 mm (NSZ-03249) i topnik RMA w żelu (TRP-16727). Do przewodów i XT30U używamy
grota dłutowego dopasowanego do pola, zwykle 2-3 mm; do goldpinów mniejszego.
Temperatura początkowa dla Sn60Pb40 to około 340-360°C. Nie kompensujemy
zbyt małego grota długim grzaniem złącza. Potrzebne są też ściągacz izolacji,
zaciskarka do wybranych końcówek, multimetr i źródło gorącego powietrza.

Pakiet LiPo podczas lutowania musi być odłączony. Termokurczki obkurczamy
gorącym powietrzem, bez otwartego płomienia przy akumulatorze. Stanowisko musi
być wentylowane; przy cynie ołowiowej nie jemy podczas pracy i myjemy ręce po
jej zakończeniu.

## Do zweryfikowania pomiarami

- spadek napięcia przy jednoczesnym ruchu trzech i dwunastu serw,
- prąd szczytowy każdej nogi i całego napędu,
- przepięcia podczas hamowania serw,
- stabilność 5 V oraz ostrzeżenia undervoltage Raspberry Pi,
- realny czas pracy pakietu 2200 mAh,
- złącze i sposób zasilenia przyszłego Pi 5 pełnym prądem 5 A.
