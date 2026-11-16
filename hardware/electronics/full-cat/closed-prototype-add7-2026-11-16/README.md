# Głowa, czujniki i audio — dodatek do mapy połączeń

To **proponowany plan funkcjonalny siedmiu już wybranych modułów**, do wspólnego układania z zamkniętą obudową. Czytać go razem z `hardware/electronics/kicad-current/design.json`; tamte 134 połączenia, PCA/U1, trzy MG92B, ochrona i fabryczne jednostki są zachowane. `connections.json` zawiera 26 par A/B, w tym całe interfejsy USB/CSI i dwa lokalne połączenia trybu IMU. To nie jest 26 osobnych kupowanych kabli ani pełna netlista pinów USB/CSI.

| Moduł | Przypisanie i wspólna jednostka przewodu |
|---|---|
| BNO085 Adafruit4754 | SPI0: BCM11/10/9/8, INT BCM23, RST BCM24; VIN3V3/GND. Osiem żył jednej wiązki oraz dwa lokalne połączenia P0/P1 do VIN dla trybu SPI. [Nazwy padów producenta](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts). |
| ToF Pololu3417 | VIN3V3/GND i I2C1 SDA/SCL wspólne z PCA; cztery żyły przez pracujące połączenie głowy. VIN3V3 utrzymuje podciąganie I2C do3V3. [Źródło](https://www.pololu.com/product/3417). |
| Grove TTP223 | VCC3V3/GND/SIG; nowy wybór projektu BCM27, fizyczny H13. Zachować cały koniec Grove; nie kopiować starego BCM17, zajętego przez U1 /OE. [Źródło](https://wiki.seeedstudio.com/Grove-Touch_Sensor/). |
| MAX98357A Adafruit3006 | Zasilanie z istniejącej funkcji MAIN5V1, nie AUX6V; osobna para. I2S BCM18/19/21 — trzy sygnały we wspólnej wiązce. [Zasilanie i BTL](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts), [przypisanie I2S](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-wiring). |
| Głośnik4Ω/5W | Para z OUT+ i OUT− wzmacniacza. Żaden koniec BTL nie jest masą. |
| ReSpeaker Lite | Osobny cały kabel danych USB-A→USB-C z górnego czarnego USB2 Pi. Dolny USB2 i istniejący USB500/Delock zostają dla BUS. Mikrofon przez USB, jego EXT5V i wyjścia głośnikowe nieużywane. [Źródło właściwego Lite](https://wiki.seeedstudio.com/reSpeaker_usb_v3/). |
| Camera Module3 NoIR Wide | Cała taśma CSI15↔15 dla Pi4; bez osobnego zasilania GPIO. Nie ciąć i nie brać kabla22↔15 przeznaczonego do innych Pi. [Źródło](https://www.raspberrypi.com/documentation/accessories/camera.html#pinout-information). |

Numery H oznaczają fizyczne piny nagłówka40-pin, a BCM — numery GPIO. Nowy dodatek jawnie zastępuje tylko fragment dawnego kontraktu „pozostałe35 pozycji NC”: nowe H12/13/16/18/19/21/23/24/35/40 są przypisane. H2/H4 nadal NC; Pi nadal zasilany fabryczną parą K1474 przez USB-C. Dotychczasowe H1/H3/H5/H6/H11 nie zmieniają funkcji. Lokalne LOGIC3V3/GND to istniejące funkcje sieci, nie wymyślone dodatkowe piny złącza.

Do związania przed wykonaniem instalacji:

- Rzeczywiste rewizje i końce: przewód USB_AUDIO, długość/strona styków CSI, złącza Grove/headerów oraz gabaryty wtyków. USB_AUDIO nie otrzymuje drugiego kredytu USB500 dla BUS.
- Sposób odgałęzienia MAIN do AMP i rozprowadzenia3V3/GND: fizyczne zakończenia, przekrój, izolacja i odciążenie. Nie wybrano nowej złączki ani dodatkowego splicu. Istniejące W079/W080/K1474 pozostają całe.
- Zapas prądu MAIN dla Pi/BUS/mikrofonu/kamery/AMP oraz Pi3V3 dla IMU/ToF/dotyku. Producent AMP zaleca około800mA zapasu zasilania przy pełnym wyjściu. Wartość F_PI na wejściu MAIN nie jest limitem prądu wyjściowego5V. Pobór, spadki i temperatury nie zostały zmierzone.
- Dostępne regiony i rzeczywista długość/luz w nowym układzie. Stałe IMU/AMP układać przed zamknięciem szyn; CSI+ToF przez yaw/pitch z kotwami i ochroną krawędzi; MIC+TTP pozostają dołączone przy podnoszeniu ramki. Ręczne układanie przed osłonami, bez produkcyjnych osi każdej żyły.

Wszystkie installed_length/cut/slack pozostają NULL. Zachowane MG92B250 i wybrane JR300, cztery niezależne przewody E2/JPWM225 (konserwatywnie220 każdy)/wszystkie fabryczne końce, FHAC, K1474 i BUSUSB500 nie dostają kredytu ze starych krzywych CAD. Plan nie upoważnia do zasilania ani nie potwierdza fizycznego dopasowania.

Tożsamości części: archiwalny wybór17Oct SHA839a080f94dc0de310d1d2b21b0f2803b36b500e9a4752591942bef60b92097f; przeniesiono tożsamości/interfejsy, nie historyczne przypisania/długości. Aktualny bazowy JSON SHA7be7baa6913fdfa7fe306ef5c33cb3185efd2628ed4001a85acf352ab651ff01. Odczyty Lorentza1b4/1b9 i kontrola primary przez mastera16Nov; bez nowej recenzji CAD.

Korekta nazwy jednostek16Nov: cztery225/min220 to precrimped przewody E2/JPWM: XP02.source 2147612113, XP02.module 2147632113, XP03.source 2147611113, XP03.module 2147631113. Nie są czterema wiązkami nóg ani odcinkami czterech MTA0100335. Oprawki MTA i ich fabryczne odcinki są osobnymi jednostkami. Osiem wybranych WAGO221-2411 już ma odniesienia w bazowym grafie; zachować je we wspólnych dostępnych regionach, bez nowych ośmiu indywidualnych obudów. Przeniesiono tylko tożsamości, nie dawne pozycje/długości.
