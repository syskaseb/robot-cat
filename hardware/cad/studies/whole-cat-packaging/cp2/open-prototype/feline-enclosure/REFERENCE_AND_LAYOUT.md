# Sylwetka Oli i wspólny układ

## Aktualny wspólny plan17.10,05:11Warszawy

Poprzedni bank90° odrzucony354par/150kontaktów/95,141s. Nie budowany
natywnie. Wspólny plan50grup499brył przechodzi na dwa rzędy po6oprawek,
RX−60/+60, środki(4,+30,70)/(16,−30,70), ATO na zewnątrz. Prawy rząd
ma nowy Pitch30 zamiast32, rozstaw rzędów wX12mm: zachowane kupne
12oprawek/24TE/12ATO, ale stare prawe mocowanieR47 nie jest nowym wyborem.
Wszystkie nowe końce/mocowania/stock wymagają aktualnego natywnego wyniku.

Pi4/BUS/MAIN otrzymują górną wspólną półkę, PWM9685 przednią górną strefę,
U1/PWM1608 i AUX dolny przedział, cztery MTA pod ramą. MAIN nominalne
Z96,52: stary adapterP0/świat46,52 nie został zachowany jako zaliczony
interfejs nowego zakresu. Tułów325×196×160, bez przekroczenia200mm.
Górny przekrój p4 ma17węzłów zamiast9: poprzednia rzadka wielolinia
niepotrzebnie ścinała wolne naroża. Dolna połowa płaska z narożamiR12.
Natywny nowy obrys jeszcze nie został przebudowany; to jawna propozycja.

Cała głowa/szyja−40X/−90Z. S0 centrumKORPUSU(−115,−6,78),RX90;
S1 centrumKORPUSU(−105,45,65),RZ90. Lugi S0 i czteryS1 obrócone wokół
rzeczywistych cylindrycznych osi otworów z BRep, nie wokół bbox ani innych
śrub. Trzeba zbudować ich nowe osłonięte przewody i sprawdzić cały ruch głowy.
S0 przekracza przedni obrys tułowia o2mm: wymaga wspólnej osłony szyi,
a kluczS0 i sterowanieS1 celowych klapek w łącznym limicie szerokości200.

Odbiór worker8969/PID18356:76rzeczywistych par/3kontakty/0błędów,
65,719s, dwa położenia nóg. Wszystkie trzy dotyczą jednego dolnego stosu
PWM968518/S0; inne sprawdzone pary brył bez kontaktów. To nie odbiór
całych kabli/skorupy ani fizycznego ruchu. Następna zmiana obejmie CAŁĄ
PCB PWM wraz z15referencjami, a nie tylko nakrętkę/washer. Niezmieniony
zakres odzyskać po porównaniu recept i pinów; nie liczyć76par ponownie.

F_PI jest ustawioneRX90, centrum(−105,0,−32), więc długie końce wychodzą
wY przed kolumnami podpór. F0RZ45°,centrum(68,0,−13,75), AUX przesunięte
do przodu pod ramę, XT60 pod tylnym przedziałem(143,0,−35), a nie w serwie.
Osiem łączników ma centraX−45/5/30/89,Y+/−35/47,Z−35,75; nie przecinają
już czterech kolumn podpór. Cztery MTA centraX−40/65,Y+/−15,Z−34.

WAGO: dwa wewnętrzne pionowe rzędyY+/−40,5, porty nominalnie kuZ,
górna płaszczyzna−4; dwa zewnętrzne płaskie rzędyY+/−67,spód35,5,
porty do środka. Ich nominalne strony źródłowe rekonstruowane z aktualnych
punktów końców; brakujące W1/G_AUX pozostają jawnie niezweryfikowane.
Kolejny właściwy wynik: wspólny wybór kierunków52prefiksów9mm+łuk
z kilku domen na koniec, bez seryjnych prób jednego arbitralnego kierunku.
Następnie pełne80sieci orazW1/W3/W4, nowe odciążenia/loadpaths i panele.

## Następna wspólna hipoteza,04:03Warszawy, jeszcze BEZ CAD

Nie wykonywać trzeciego częściowego wariantu180° banku. Jego końce
skierowane w górę potrzebują jeszcze prostych9mm i pełnego łuku kabla;
samo zmieszczenieTE nie rezerwuje tej przestrzeni. Następny układ obraca
CAŁY zachowany bankR47 o90°X: dwa rzędy są na wysokości około94 i−30,
wszystkie wejścia skierowane ku+Y, ATO wyjmowane ku−Y. Pełny gabaryt
banku po obrocie188X×71,43Y×148,24Z. OśZ nadal32, maksimum tułowia
325×196×158; nie ścinać terminali ani zmniejszać promieni.

Plan pozycji do TANIEJ wspólnej bramki, nie wybór ani dowód zmieszczenia:

| Cały podzespół | Orientacja | Docelowy środek / datum [mm] |
| --- | --- | --- |
| Bank12/24 | RX90° | pełny bbox:17,0,32 |
| Głowa/E6 i oryginalnyYawcore | bez zmiany względnej | cały mechanizm−90Z |
| S0 z kluczem/osprzętem | RX90° | ŚRODEK KORPUSU:−110,0,78 |
| S1 z pokrętłem/osprzętem | bez obrotu | ŚRODEK KORPUSU:−105,57,58 |
| MTA FL/FR | bez obrotu | pełny bbox:−40,+/−50,73,5 |
| MTA RL/RR | bez obrotu | pełny bbox:65,+/−50,73,5 |
| 8łączników przedłużeń | oś35,5mm wX | paryX−60/−15/30/75,Y+/−30,Z70,5 |
| F_PI | RY90° | pełny bbox:−98,−30,−13 |
| F0 | bez obrotu | pełny bbox:156,0,43,5 |
| F_AUX | RZ90° | pełny bbox:143,0,−15 |
| XT60 | bez obrotu | pełny bbox:143,−35,20 |
| POST_F0 | bez obrotu | pełny bbox:143,−35,42 |
| JPWM | bez obrotu | pełny bbox:25,−44,50 |
| XP01/02/03 | od obecnych całych złączy | rezerwacjaX−20/10/40,Y−44,Z35 |

MAIN/Pi/BUS/PWM/U1/AUX bez dalszych nowych mikroprzesunięć. Przed akceptacją
rozliczyć również wybrane przewody/fusy sygnałoweW1/W3/W4;178rekordów
korpusu nie jest całym robotem.8łączników otrzymuje właściwe strony
factory/custom od dotychczasowych ról, nie zgadniętego centrum złącza.
Oba wyjścia każdegoMTA mają początkowe proste9mm i pełny promień;
rozstaw front/tył105mm pozostawia70mm pomiędzy obudowami, zamiast
stawiać cztery oprawki w rzędzie z przecinającymi się wyjściami.

WAGO rozdziału:10normalnych415 w dolnych bocznych rzędach, centraX
−50/−15/20/55/90,Y+/−50,spódZ−43,5. Pozostałe6normalnych+4large615
w dwóch wyższych rzędachY+/−38,spódZ−17; każdy rząd ma w kolejności
large/normal/large/normal/normal, centraX−46,5/−12/22,5/57/88.
Górne porty kierować do środka, dolne na zewnątrz, aby wachlarze nie
przecinały dolnego rzędu banku. Dolna szyna po stronie−Y ma zarezerwowany
serwisowy ruch12mm w dół po zdjęciu panelu, bez rozpinaniaWAGO;
pełne kable/odciążenia muszą mieć tę drogę i zapas. Nie uznać tego za
zbudowany mechanizm ani deklarować dostępuATO bez rzeczywistego narzędzia.

Przedni tułów może mieć pełniejsze barki, nadal maks196mm: przekroje
X/W/H:−141,5/100/158;−112/196/158;−65/196/158;10/180/158;
55/166/156;112/188/156;158/132/158;183,5/40/100.
Górna połowa pozostaje łagodnie zaokrąglona(p4); dolna połowa wymaga
płaskiego brzucha z narożamiR12, nie dalszego zgadywania wykładnika.
To odrębna hipoteza przestrzeni z pełnymi źródłami/wyjściami, nie zaliczona
skorupa. Sprawdzić wszystkie początkowe odcinki/łuki, głowę/ogon i ruch
nóg przed nowym detalowaniem. Cztery podpory i ich36pozycji bez zmiany.

## Bieżący odbiór17.10,03:54Warszawy

Pierwszy natywny układ odrzucony262par/184kontaktów. Drugi wspólny
podział warstw:67par/27kontaktów/0błędów,247,922s; parametr całej
głowy80→81→80 i świeże otwarcie potwierdzone. To nadal NIE WYBRANY
układ, bez nowych mocowań i bez pełnych przewodów. Nie interpretować
mniejszej liczby par jako mniejszego zakresu: broadphase pomija wyłącznie
rozłączne bbox rzeczywistych części, a nie uznaje nakładania za kolizję.
Bank nie styka się z nogami w dwóch sprawdzonych pozycjach nowego układu;
pełny zmieniony ruch banku/modułów nie jest jeszcze potwierdzony.

Niezmienione cztery kolumny podpór pozwalają zachować2750par/36pozycji
P0/nóg/baterii/podpór (dowód ponownego użycia0,719s). Nie obejmuje to
nowej skorupy, wiązek, ograniczeń serw ani nowych mocowań.
Kandydackie końcowe przyrosty kątów względem obecnego spoczynku:

| Kod historyczny | Hip | Knee | Ankle |
| --- | ---: | ---: | ---: |
| FL | +10,097° | +56,928° | +74,211° |
| FR | −10,097° | −56,928° | −74,211° |
| RL | −10,097° | +56,928° | +74,211° |
| RR | +10,097° | −56,928° | −74,211° |

To nie kalibracja serw ani polecenia ROS. Fizyczne strony są opisane
w motion-layout.json; nazwy historyczne nie odpowiadają przodowi/tyłowi.
Opuszczenie94,792mm, przestawienie łap29,167mm; powrót po tym samym
torze jest odwróceniem geometrii, nie dowodem zdolności udźwigu.

`endpoint-layout.json` obejmuje178rekordów granic/końców80sieci korpusu:
120przeniesionych tożsamości położeń,58wymagających nowych kotew lub
alokacji brakujących modułów. Nie zastępuje całych przewodów głowy/ogona.
Do wspólnego układu trzeba jawnie dodać8rzeczywistych łączników przedłużeń,
F0/F_AUX/XT60/POST_F0 i złącza sygnałowe, obie strony4MTA i ich chwyty.
Stare920mm źródła nie są automatycznie aktualnym wyborem.

`tail-core-subset.json`: oryginalny edytowalny ServoSupport34+15mmZ
jest podzbiorem aktualnego rozbudowanego mocowania ogona, dodano0mm³,
usunięte stare galerie6829,300mm³,3,234s. Pozwala to planować rezygnację
ze starych ramion przewodów bez przesuwania napędu ani wycinania jego
rdzenia. Nadal wymagane nowe niezależne odciążenie i natywne złożenie.
Nie zastępować tym dowodem sprawdzenia nowej wiązki ani skorupy.

NEXT przed trzecim detalowaniem: pełna alokacja brakujących części,
obu wyjśćMTA i obsługiS0/S1 względem RZECZYWISTYCH korpusów, nie środka
bbox obejmującego wysunięty klucz. Rozpatrzyć wspólnie przednią strefę
sterowania, centralny bezpiecznik pod baterią, kompletne dolne listwyWAGO
i nowe zwarte mocowanie przewodu ogona. Dopiero po taniej bramce całej
przestrzeni wykonać następną kontrolę zmienionych brył i szczegółowe uchwyty.
Obrys p4 wciąż nie mieści narożnikówTE i dwóch przednich dolnychWAGO:
następny przekrój musi wynikać z całej zajętości, nie seryjnego zgadywania
wykładnika/obniżania banku z powrotem w nogi. Maksymalna szerokość200mm.

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
