# Wejście baterii i montaż S0 — bieżąca wersja20H

To pakiet do przymiarki bez zasilania. **Najpierw [FIT_S0](FIT_S0.md), pomiar
baterii oraz całych F0/MTA; dopiero potem duże części.** Poprawiona tylna
podstawa jest warunkowa. Nie używaj starej C20_RearBase ani E19_RearBase
wraz z nowym kandydatem. Jedyny dobór wydruków: [PRINT.csv](PRINT.csv).

Instalacyjna połówka AMASS XT60H-M, F0 i POST_F0 pozostają nieruchome.
Rozłącza się wyłącznie fabryczną połówkę pakietu o14mm w osiX, przy podpartej
baterii. Kupiona połówkaF z zestawu jest zapasem; nie jest trzecim złączem.
Nie skracaj ani nie wymieniaj fabrycznych przewodów i wtyku baterii.

## Całe jednostki i ich odniesienia

| Jednostka | Bieżący plan do porównania z egzemplarzem |
|---|---|
| Fabryczna dodatnia żyła baterii | Około135mm od wyjścia izolacji z pakietu do wejścia w sztywną odgiętkę. W tym już8mm na ułożenie. Osobno zachować cały wtyk i odgiętkę. |
| Fabryczna ujemna żyła baterii | Około132mm przy tych samych odniesieniach; własny zapas8mm już wliczony. Obie długości dostawy pozostają nieznane. |
| W075 — robotowa żyła wejściowaF0 | Oryginalna pomarańczowa żyła FHAC0002. Projekt37,34mm zawiera5mm na kielich XT60H-M i mieści się w limicie50mm przed bezpiecznikiem. Przygotowanie dopiero po przymiarce; bez dodatkowego połączenia przedF0. |
| W076/factory | Całe fabryczne wyjście F0→POST_F0.1. Regulacja portuPOST wY−34…−20mm przewiduje92,42–106,42mm wraz z projektowymi11mm wWAGO. Dostawa i obie odgiętki wymagają pomiaru. |
| W001 | Ciągły LAPP0107001 Ø3,1mm od instalacyjnej połówki XT60.minus do G1.2; plan89mm z końcami i jednym zapasem ułożenia. Przewód podparty i stacjonarny. |
| W076/custom | Ciągły HELU23802 Ø4,2mm POST_F0.2→S0.in. Warunkowy plan389mm z końcami i zapasem ułożenia. |
| W066 | Ciągły HELU23802 Ø4,2mm S0.out→P_SYS.1. Warunkowy plan260mm z końcami i zapasem ułożenia. |

Dla obu zmienionych odcinków HELU zachowano źródłowy promień instalacji stałej
25,2mm. Dojście IN sprawdzono przy promieniu wewnętrznym29,33mm. Wartości
projektowe zawierają już zapasy i zakończenia; nie doliczaj ich drugi raz.
**To nie lista wykonanych cięć.** Ułóż rzeczywiste jednostki przed ustaleniem
cięć, z zachowaniem wymaganych promieni, końców i odciążenia. W077 to odrębny
krótki przewód F_PI.out→SPLICE_PI.16 — nie przewód wyjściowyS0.
[Bieżący bilans](BODY_FEED_UNITS.json) · [Mapa160połączeń](source/POLACZENIA.csv)

Wybrany nominalny zapas K3/r4 wynosi3mLAPP0107001 i9mHELU23802.
Dostarczone ilości są niepotwierdzone. Nie łącz resztek różnych fizycznych
jednostek w hipotetyczny wspólny zapas. Nie dodawaj przedłużki baterii.

## Co przymierzyć przed dużą podstawą

1. **S0:** [kupon56×57×3mm](sample/FIT_S0_coupon.stl) ma przejścieØ24 i dwa
   otworyØ6,5 w rozstawie38mm, tak jak kandydacka podstawa. Użyj rzeczywistego
   wyłącznika, klucza, obu kompletnych oczekM10 i całego kompletuM6.
   Sprawdź oparcie, zazębienie, narzędzia i klucz podczas wkładania, obrotu
   oraz wyjmowania. Modelowy zielony walec to rezerwa obsługi, nie dokładny
   kształt klucza. Szczegóły i kryteria: [FIT_S0.md](FIT_S0.md).
2. **Bateria:** zmierz osobno obie żyły między wskazanymi odniesieniami oraz
   pełne odgiętki i wtyk. [Zdjęcie producenta wybranego SKU](https://gensace.de/products/gens-ace-g-tech-soaring-2200mah-11-1v-30c-3s1p-lipo-battery-pack-with-xt60-plug) wskazuje wyjście
   przy krótkim końcu; dokładna pozycja i sztywny początek pozostają do pomiaru.
   Uwzględnij dodatkowy mały fabryczny wtyk i jego odłożenie. Projektowa
   rezerwa tego wtyku24×12×14mm nie jest pomiarem. Nie ustalaj pinów po kolorze.
3. **F0/FHAC0002:** przymierz korpus, zamkniętą i otwartą klapkę, uwięź,
   obie pełne żyły i odgiętki. Przyjęta wysokość21,5mm jest założeniem do
   przymiarki, a nie deklaracją dokładnego wymiaru dostawy.
4. **Cztery MTA0100335:** przymierz każdą pełną oprawę z klapką i obiema żyłami
   do jej małego uchwytu. Próbka32×18×18mm oraz oknoFR35mm nie gwarantują
   wymiarów rzeczywistych czterech sztuk. Dopasuj mały uchwyt przed ramą.

## Kolejność dwóch osób

1. OsobaA składa otwartą ramę, zachowując8oryginalnych kotew M2,5×16 i ich
   osprzęt. OsobaB oznacza jednostki i oba końce według mapy.
2. Po FIT_S0 przygotuj na stole pełny S0 z oboma oczkami, nakrętkami,
   podkładkami i luźno ułożonymi odcinkami W076/custom oraz W066. Odniesienia
   modelu to obrót całego oczkaIN o−30° iOUT o−105,522° wokół osiY własnych
   trzpieni. Zweryfikuj je na rzeczywistym gnieździe i izolacji; nie obracaj
   samego punktu przewodu. Ułóż odcinki próbnie przed wykonaniem zakończeń.
3. Osadź tak przygotowane S0 przez otwartą górę i zamocuj je przedE1.
   Dopiero później montuj cały lutowany zespółE1, banki i odległe końce
   w odpowiednich WAGO. Rzadka naprawa może wymagać demontażuE1; nie trzeba
   zapewniać dostępu nasadką przez kompletnie zabudowaną elektronikę.
4. Zamocuj trzy małe adaptery: D20_XT60_Axial_Adapter na istniejącym gnieździe,
   D20_F0_Open_Adapter na dodatnim żebrze oraz D20_POST_Aft_Slotted na narożniku
   ramy. Przy F0 pozostaw klapkę i uwięź wolne. POST ustaw po pomiarze całej
   fabrycznej żyły, z dostępną dźwignią i odciążeniem na zdrowej izolacji.
5. OsobaA podpiera baterię poziomo. OsobaB trzyma obie obudowyXT60, rozłącza
   je wX i przejmuje fabryczną połówkę oraz mały wtyk. Po zdjęciu drzwi
   i górnego mostka poprowadź końcówki przez otwartą gardziel, ręcznie
   zmieniając ułożenie elastycznych żył. Nie ciągnij za przewody. Sprawdź
   wkładanie w odwrotnej kolejności i powrót mostka na oba oparcia banków.
6. Ułóż pozostałe grupy według [montażu elektrycznego](ELECTRICAL_ASSEMBLY.md),
   sprawdź potrzebny luz przy ruchach głowy i ogona oraz chłodzenie. Pokrywy
   zamykaj na końcu, obserwując wiązki przy krawędziach. Alarm pozostaje
   zamocowany i odłączony, dopóki nie ma identyfikacji rzeczywistych komór.

## Mocowanie tej części zestawu

| Rola | Nominalny zestaw, dostępność do potwierdzenia |
|---|---|
| S0 | 2×DIN912M6×20,4×podkładka6,4×12×1,6mm,2×nakrętkaM6AF10h5 |
| Mostek baterii | 2×M3×12 z2nakrętkamiM3 |
| POST | 1×M3×12 z1nakrętkąM3 |
| Opaski wejścia i4MTA | 19w tych rolach: MTA12,F0 3,XT60 2,POST2; nie jest to całkowita liczba opasek robota |

Sprawdź rzeczywistą szerokość i grubość opasek: szczelina adapteraF0 ma
3,4×2,2mm. Plastikowy nadmiar opaski można obciąć po jej prawidłowym zamknięciu;
nie oznacza to skracania przewodów fabrycznych. Pozostała stal mechanizmów
i podstawy pozostaje według modelu oraz [montażu całego robota](MONTAZ.md).

Kandydat20H zastępuje C20_RearBase/E19_RearBase. Zachowane są C20_FrontFrame,
mostek baterii, cztery małe uchwytyMTA i trzy adapteryD20. Nie drukuj równolegle
starszych C20_F0_OpenMount i C20_Post_OpenSlottedMount.

Dopasowanie, długości cięć, luzy, masa fizyczna, nośność i chód pozostają
niepotwierdzone. Pakiet kończy się na pierwszej przymiarce bez zasilania.
