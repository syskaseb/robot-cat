# Dobór części i źródła CAD - 2026-09-22

Branch `codex/robot-cat-mechanical`, model odniesienia v25. **Dobór i pomiary
części handlowych, nie nowa rewizja kota ani zatwierdzenie do druku.** Nie
zmieniono złożenia, mocowań, jointów ani oryginalnych PDF-ów zakupowych.
Nic nie zamówiono i nie wysłano zapytań do sklepów.

## Termin i sklepy

Użytkownik dopuszcza maksymalnie 10 dni oczekiwania. Na dzień 22.09.2026
oznacza to granicę 02.10.2026, jeżeli zamówienie jest składane dzisiaj.
Botland ma pierwszeństwo, Kamami jest alternatywą. Stan poniżej odczytano
bezpośrednio ze stron 22.09, około 00:05-00:13 Europe/Warsaw. Indeksowane
wyniki wyszukiwarki bywały nieaktualne. Termin wysyłki nie jest gwarancją
doręczenia; dostawa planowana nie oznacza stanu magazynowego.

## Konkretne propozycje

| Zastosowanie | Model / zakup | Stan i cena przy sprawdzaniu | Decyzja robocza |
|---|---|---|---|
| Dwie osie głowy + jedna ogona | [3 x TowerPro MG92B pozycyjne, DNG-24409](https://botland.com.pl/serwa-typu-standard/24409-towerpro-mg92b-serwomechanizm-cyfrowy-z-metalowa-przekladnia.html) | Botland: 61 szt., wysyłka 24 h, 89,90 zł/szt. | Kandydat bazowy; nie wersja 360 stopni DNG-24410. Trzy serwa, nie cztery. |
| AUX, osobno od zasilania Raspberry Pi | [Pololu D24V90F5, PLL-02580](https://botland.com.pl/przetwornice-step-down/2580-d24v90f5-przetwornica-step-down-5v-9a-pololu-2866-5904422372118.html) | Botland: 17 szt., wysyłka 24 h, 149 zł | Proponowana druga sztuka tego regulatora, zamiast nieokreślonego 5 V/3 A. |
| Czujnik ToF, bez zmiany wersji wskazanej w dokumentacji | [VL53L5CX Pololu 3417, PLL-21487](https://botland.com.pl/czujniki-time-of-flight/21487-vl53l5cx-time-of-flight-czujnik-odleglosci-8x8-i2c-400cm-pololu-3417.html) | Botland: 0 szt., planowane 50 szt. około 30.09 | Warunkowo mieści się w limicie; ponowna kontrola terminu przed zakupem. |
| IMU, model już wskazany w lokalnej dokumentacji | [BNO085 Adafruit 4754, ADA-22113](https://botland.com.pl/czujniki-9dof-imu/22113-bno085-9-dof-imu-fusion-breakout-3-osiowy-akcelerometr-zyroskop-i-magnetometr-adafruit-4754.html) | Botland: 93 szt., wysyłka 24 h | Nie jest już nieokreślonym wariantem BNO085. |

Nowe propozycje serw i AUX kosztują łącznie **418,70 zł**, bez wysyłki i bez
pozostałych pozycji listy. To nie jest dotychczasowa cena trzech tanich
mikroserw z szacunkowego BOM-u. Regulator AUX nie zastępuje regulatora Pi;
wyjść dwóch przetwornic nie łączymy równolegle.

### MG92B: co wiadomo, a czego nie wolno założyć

[TowerPro](https://towerpro.com.tw/product/mg92b/) podaje 3,1 kgf cm przy 5 V,
3,5 kgf cm przy 6 V, masę 13,8 g i metalową przekładnię. To **moment
zatrzymania**, nie dopuszczalny moment pracy ciągłej. Producent nie podaje
na tej karcie prądu zatrzymania. Nie wpisujemy do bilansu znalezionych na
forach prądów jako danych gwarantowanych.

Karta załączona do konkretnego produktu Botland ma tabelę A=35, B=22,6,
C=31, D=12, E=31,5, F=22,8 mm. Według jej rysunku A to całkowita wysokość
z wałkiem, C wysokość bez wystającego wałka, E długość z uszami. Opis
22,8 x 12 x 31 mm **nie jest pełną obwiednią montażową**.

Model Adafruit 2307 jest opisany w ich repo jako `MicroServo MG923B`;
[strona produktu 2307](https://www.adafruit.com/product/2307) identyfikuje
go jako MG92B. Nie jest to fabryczny STEP TowerPro ani dowód zgodności
każdej rewizji serwa. Import ma długość z uszami 31,5 mm, szerokość 12 mm,
ale całkowitą wysokość **36,8 mm**, wobec A=35 mm w karcie TowerPro.
Zostawić większą przestrzeń; nie skalować modelu, żeby wymusić zgodność.

Z modelu: otwory uszu Ø2 mm, rozstaw 27,5 mm; oś wałka jest odsunięta
o 8,5 mm od bliższego otworu i 19 mm od dalszego. Są to **pomiary STEP**,
nie uzupełnienie fabrycznej specyfikacji tolerancji. W modelu brak pełnego
przewodu, wtyku i zamontowanego orczyka. Mechanizm powinien korzystać z
dołączonego orczyka, z osobnym podparciem osi i wymiennym adapterem PETG,
nie z drukowanego na zgadywany wymiar wieloklinu. Mocowania i ruch wymagają
testu obciążenia oraz kalibracji zakresów przed zatwierdzeniem mechanizmu do druku.

Adafruit ostrzega też o wymaganym sygnale sterującym 5 V. Przy integracji z Pi
i [Grove PCA9685](https://wiki.seeedstudio.com/Grove-16-Channel_PWM_Driver-PCA9685/)
trzeba rozdzielić zasilanie serw od poziomu logicznego PWM i sprawdzić potrzebę
bufora/konwersji poziomów. Nie podawać 5 V na GPIO Raspberry Pi. Ten dobór
nie zatwierdza jeszcze schematu połączeń ani obciążalności ścieżek Grove.

### AUX: dlaczego większy regulator

Nie ma podstaw do zatwierdzenia nieokreślonego 3 A dla trzech cyfrowych serw
i audio bez znajomości prądów rozruchowych. D24V90F5 to propozycja z większą
rezerwą i kompletną dokumentacją. Jest droższa od szacunku 49 zł i wymaga
**wlutowania dołączonych złączy śrubowych**: nie spełnia dosłownie wcześniejszego
opisu "gotowe zaciski". Ta zmiana BOM-u jest jawna, nie została wdrożona w CAD.

[Pololu](https://www.pololu.com/product/2866) uzależnia wydajność od napięcia,
chłodzenia i temperatury; nazwa "9 A" nie gwarantuje 9 A ciągłego prądu w
zamkniętej obudowie. Należy sprawdzić spadki napięcia na przewodach, minimalne
napięcie MG92B (5 V) wobec tolerancji regulatora i próbę jednoczesnego ruchu.
Wymagane są również zabezpieczenia gałęzi, kondensatory przy odbiornikach,
odciążenie przewodów i odstęp cieplny od PETG. Regulator nie jest układem
ochrony przed nadmiernym rozładowaniem pakietu 3S.

## Akumulator: ustalony kandydat, brak zamkniętego zakupu

W preferowanych sklepach nie potwierdzono odpowiedniego dostępnego pakietu
3S 2200 mAh >=30C z terminem do 10 dni. Przykłady odrzuconych ofert:
[GPX 2200/30C Botland](https://botland.com.pl/produkty-wycofane/8413-pakiet-li-pol-gpx-extreme-2200mah-30c-3s-111v-5902230132603.html),
[Dualsky 2200/25C Botland](https://botland.com.pl/produkty-wycofane/2789-pakiet-li-pol-dualsky-2200mah-25c-3s-111v-eco-s-6941047104709.html),
[Turnigy 1800 Kamami](https://kamami.pl/wycofane-z-oferty/220652-akumulator-li-pol-3s-1800mah-65130c-turnigy-nano-tech.html)
są wycofane; dwa ostatnie nie spełniają też wszystkich założeń bazowego pakietu.

Kandydat techniczny: **Gens Ace G-Tech Soaring GEA223S30X6GT**, 3S/11,1 V,
2200 mAh, 30C, XT60. [Producent](https://gensace.de/products/gens-ace-g-tech-soaring-2200mah-11-1v-30c-3s1p-lipo-battery-pack-with-xt60-plug)
podaje około **106,5 x 35 x 21,5 mm, 174 g**. Wiele polskich ofert kopiuje
mniejsze 106 x 34 x 21 mm / 168 g, prawdopodobnie ze starszej wersji;
nie przyjmować ich jako obwiedni aktualnego G-Tech. Nie znaleziono w tej
kwerendzie potwierdzonego STEP konkretnej rewizji. Do CAD wystarczy obwiednia
według większych wymiarów producenta, uzupełniona o przewody, wtyki, luz
montażowy i łagodną wyściółkę - nie zacisk sztywno ściskający miękki pakiet.
Uszkodzonego lub spuchniętego pakietu nie używać.

[Qiktech](https://qiktech.pl/pl/p/Akumulator-GENS-ACE-G-Tech-Soaring-2200mAh-11%2C1V-3S1P-XT60/29393)
deklaruje "duża ilość", wysyłkę 24 godziny i 118,99 zł. To **oferta poza
preferowanymi sklepami**, nie zatwierdzony zakup; wysłano użytkownikowi pytanie
o dopuszczenie wyjątku. Nie kontaktowano sklepu. [Drukmistrz](https://drukmistrz.pl/47626-gens-ace-g-tech-soaring-2200mah-111v-30c-3s1p-lipo-batte-gea223s30x6gt.html)
pokazuje 5+ szt. w magazynie zewnętrznym, ale bieżąca strona nie potwierdza
jednoznacznie wcześniejszego terminu 48 h z wyszukiwarki; nie kwalifikujemy
jej jako potwierdzonej dostawy <=10 dni.

Względem zastępczej bryły 90 x 43 x 19 mm w kocie, pakiet G-Tech jest
o 16,5 mm dłuższy i 2,5 mm grubszy. **Dotychczasowa tacka nie jest zatwierdzona
dla tego pakietu.** Potrzebna jest także ponowna kontrola drogi wyjmowania.

## Pobrane modele i rzeczywiste wymiary importu

| Plik STEP | Wymiary XYZ importu [mm] | Bryły | isValid |
|---|---|---:|---|
| `mg92b-adafruit-2307.step` | 12 x 31,5 x 36,8 | 6 | true |
| `bno085-adafruit-4754.step` | 25,4 x 22,86 x 4,53 | 55 | true |
| `vl53l5cx-pololu-3417.step` | 12,7 x 17,78 x 2,566 | 1 | true |
| `d24v90f5-pololu.step` | 40,64 x 20,32 x 7,6748 | 1 | true |

Pomiar przez FreeCAD 1.1.3, bez otwierania i modyfikacji kota. `isValid`
potwierdza geometrię importu, nie zgodność egzemplarza, brak kolizji ani
wytrzymałość mocowania. Modele nie obejmują wszystkich podłączonych przewodów.
STEP regulatora nie obejmuje dołączonych złączy śrubowych.

Źródła montażowe:

- BNO085: model otworów Ø2,5 mm, raster 20,32 x 17,78 mm. [Strona Adafruit](https://www.adafruit.com/product/4754)
  podaje nominalnie 25,6 x 22,7 x 4,6 mm, nieco inaczej niż STEP. Zachować
  tolerancję i porównać rewizję PCB z aktualną sztuką.
- VL53L5CX: dwa otwory Ø2,18 mm pod M2, rozstaw 12,7 mm. Ich środki w STEP:
  (10,16; 2,54) i (10,16; 15,24). Rysunek producenta toleruje lokalizację
  wiercenia ±0,1 mm i krawędzi płytki ±0,3 mm.
- D24V90F5: cztery **narożne** otwory Ø2,18 mm pod M2, raster
  35,56 x 15,24 mm. Nie mylić ich z otworami złączy o podobnej średnicy.
  Rysunek podaje te same tolerancje wiercenia i krawędzi co wyżej.

## Oryginały i odtworzenie

`sources.zip` zachowuje 10 oryginalnych plików bez zmian. Rozpakowane
STEP/PDF/DXF/JPG są ignorowane przez Git, żeby pliki STEP nie generowały
setek tysięcy wierszy diffu. Suma archiwum jest w `sources.sha256`.
Licencje i prawa należą do dostawców; nie deklarujemy tych modeli jako
własnego projektu ani zweryfikowanych części do produkcji.

- [STEP MG92B w bibliotece Adafruit](https://github.com/adafruit/Adafruit_CAD_Parts/tree/6f52ee4d48df0e7118d2d82f485cb572051a24fe/2307%20MicroServo%20MG923B).
- [STEP BNO085 w bibliotece Adafruit](https://github.com/adafruit/Adafruit_CAD_Parts/tree/6f52ee4d48df0e7118d2d82f485cb572051a24fe/4754%20BNO085%20STEMMA%20QT).
- [Pololu 3417: STEP, rysunek PDF i drill DXF](https://www.pololu.com/product/3417/resources):
  pliki 0J1874, 0J1873 i 0J1997.
- [Pololu 2866: STEP, rysunek PDF i drill DXF](https://www.pololu.com/product/2866/resources):
  pliki 0J1582, 0J1581 i 0J915.
- [Karta MG92B z Botlandu](https://botland.com.pl/index.php?controller=attachment&id_attachment=5094).
- [Legenda wymiarów TowerPro](https://towerpro.com.tw/wp-content/uploads/2014/07/小馬達尺寸標示圖B.jpg).

Z katalogu niniejszego pliku, jeśli oryginały nie są jeszcze rozpakowane:

```powershell
Expand-Archive -LiteralPath sources.zip -DestinationPath .
& 'C:/Users/Sysq/Downloads/FreeCAD_1.1.3-Windows-x86_64-py311/bin/python.exe' probe.py
```

`probe.py` odtwarza `step-inspection.json`. Nie uruchamia solvera kota ani GUI.
Następny etap to zaprojektowanie rzeczywistych mocowań i test ich dopasowania,
nie ogłaszanie zakończenia prac na podstawie dostępności modeli w Internecie.
