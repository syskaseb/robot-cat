# Sylwetka Oli i wspólny układ

Zatwierdzony obraz: `hardware/reference/appearance/ola-cat-reference.jpg`,
SHA256 `b113caadd9079a4dc4bd60dfa4bbec3af0490dffa867d006d9e730ffe7d5c941`.
Baza konstrukcji: tag `phase1-open-prototype-100-2026-10-17`, commit `9bf50a5`.
To nowy zakres zatwierdzony17.10, po nominalnym wydaniu otwartego prototypu.

## Co buduje podobieństwo

Obraz jest pojedynczą perspektywą. Nie daje wiarygodnych rzeczywistych rozstawów,
grubości ścian, szerokości ani zakresów osi. Widoczne cechy można jednak
przenieść do konstrukcji:

1. Głowa jest przed przednimi biodrami. Pysk nie wystaje z wysokiej prostokątnej
   wieży elektroniki; krótka osłonięta szyja łączy go z obniżonym przodem grzbietu.
2. Grzbiet tworzy jeden łagodny łuk. Klatka i zad mają objętość, między nimi
   jest lekkie zwężenie. Dolny obrys podnosi się przy końcach; boki nie otaczają
   dalekich wsporników jako prostokątne pudło.
3. Duża zaokrąglona głowa, wydzielone policzki/pyszczek, złote obrzeża oczu
   i szerokie trójkątne wklęsłe uszy dają rozpoznawalny charakter. Zachować
   aktualną głowę/E6; zmiany szyi i pozycji muszą uwzględnić oba napędy.
4. Kończyny są wyraźnie oddzielone od tułowia. Stawy i przerwy między sztywnymi
   segmentami pozostają czytelne. Nasz uzgodniony zakres zachowuje widoczną
   mechanikę nóg; obudowane łapy z ilustracji nie są gotowym mechanizmem.
5. Ogon wychodzi wysoko z tylnej części i unosi się łukiem. Zachować istniejący
   moduł oraz jego napęd; skorupa nie może otaczać go nieruchomym kołnierzem
   przecinającym ruch ani tworzyć półki za zadem.
6. Grafitowe powierzchnie i celowe linie podziału wzmacniają wygląd. Kolor
   i render nie mogą ukrywać wsporników, przewodów ani niedokończonych mocowań.

## Wspólne ograniczenia

Tułów startowy325×200×160mm; szerokość≤200mm. Każda drukowana część PETG
mieści się w256³ z marginesem. Cztery niewielkie podpory brzucha przenoszą
ciężar do ramy podczas leżenia. Miejsce podpór i wysokość kontaktu wynikają
z aktualnego ruchu, baterii i nóg; nie z pozowania ilustracji.

Najpierw sprawdzić razem: wszystkie człony nóg, podłogę, aktualną głowę/ogon,
rzeczywiste moduły i oba wyjścia4MTA, bankR47, pełne przekroje wiązek,
narzędzia oraz skorupę. Przenoszenie położeń modułów unieważnia odpowiednie
mocowania/końce/odciążenia, lecz nie wymaga ponownego testowania niezmienionych
wnętrz podzespołów. Trasy grupować w dwa przebiegi przy ramie i lokalne sekcje
zginania przy osiach; zachować rzeczywiste promienie i wymagane długości.

## Kolejność i kryterium pierwszego wyniku

Odtworzyć aktualne12osi i cztery fizyczne strony; historyczneFL/FR nie znaczą
przodu robota. Wyznaczyć tor obniżenia tułowia z kontaktem podpór i ruch
odwrotny, potem krótki krok przód/tył/skręt. Samo rozwiązanieIK nie wystarcza:
sprawdzić całą geometrię członów i zmienionych podpór/wiązki.

Wynik pierwszego checkpointu: jeden wspólny wykonalny układ, widoki
przód/bok/góra, tabela kątów/prześwitów, jawny wykaz relokacji. Dopiero potem
szczegółowe uchwyty i cztery główne części tułowia oraz osłony szyi.
Nie wybierać skorupy obejmującej stare wystające galerie tylko dla zachowania
ich współrzędnych. Rozstrzygnąć je jako cały związany interfejs.

`motion-layout.json` jest wynikiem taniego planowania ruchu z aktualnych osi
i zapisanej tessellacji. Ma jawne bramki dalszej kontroli; nie jest odbiorem
ciągłego ruchu, pełnych wiązek ani fizyczną próbą.

## Wspólny rozkład do sprawdzenia

Zachować nisko baterię, Pi, BUS i MAIN. U1 przesuwać razem z PWM1608,
z zachowaniem całej płytki/adaptera i połączeń lokalnych.12oprawek traktować
razem z24końcamiTE: całość ma około71,43mm wysokości, same obudowy28,5mm
zaniżały wymaganą przestrzeń. Cztery MTA otrzymują miejsca w środkowej
strefie, z rezerwacją obu fabrycznych wyjść.20WAGO lokować na dwóch
dolnych listwach, z wejściami do wspólnej strefy przewodów pod ramą.
Konkretne przekształcenia i części zapisuje `module-layout.json`.

Pierwszy rozkład z eliptycznymi przekrojami odrzucony przed detalami:
pełneTE wystają, pionowy kluczS0 ma zbyt duży zasięg, sterowanieS1 przekracza
tył obrysu. Nie przesuwać dalej pojedynczych śrub/końcówek. Zmiana rodziny:
zaokrąglone przekroje o pełniejszych narożach, nadal196×158mm, oraz obrót
CAŁYCH S0/S1 wraz z kluczem/sterowaniem/osprzętem. Docelowo dojście do
elementów obsługowych przez przewidziane klapki; ich położenie wymaga
sprawdzenia razem z bankiem i narzędziem/ręką.

Zidentyfikowano dwie kontekstowe referencje W1Ref_P_AUX_CP2 i W1Ref_G2_CP2
w tych samych położeniach co ich bieżące obudowy. Nie dodają dwóch kupnych
WAGO do liczby20. Stare wysokie osprzętyBUS są mocowaniami do zastąpienia,
nie gabarytem kupnej płytki. Listy grup nie zastępują kompletu wiązek,
podpór i osprzętu w przyszłym złożeniu.
