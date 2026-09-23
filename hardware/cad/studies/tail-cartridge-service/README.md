# Adapter ogona: serwis i natywne połączenia, R2

23.09.2026. **Osobna koncepcja, NIE zainstalowana i NIE do druku.**
Zachowano [R1](../tail-cartridge/README.md) i wszystkie dziewięć plików robota.
[Model](TailCartridgeService.FCStd), [kanał nakrętki](service-channel.png).

## Zmiana mechaniczna

Dodano do historii nasady szkic i kieszeń serwisową skierowaną w **+Y**:
X167,7…174,3, Y−6…8, Z95,9…98,4 mm. Pozwala wyprowadzić nakrętkę M3
obok czopa zamiast w stronę widelca segmentów ogona. Próbę dłuższego wyjścia
ku +X odrzucono, bo dalsza prosta droga wpadała w widelec.

Szerokość kanału 6,6 obejmuje narożniki nominalnej nakrętki w jej zachowanej
orientacji; nie obracano nakrętki tylko po to, by zmieściła się w węższej szczelinie.
Sam kanał usuwa 141,282 mm³. Zachowano oparcie nakrętki 17,118 mm² na Z98,4,
ale **ubytek materiału osłabia kołnierz**; zachowana powierzchnia nie dowodzi
zachowanej wytrzymałości. Nominalne M2×10 pozostały jak w R1.

Próba opuszczania wykryła zahaczanie o wspornik przy wysokościach +3…+12 mm,
mimo braku kolizji w spoczynku. Dlatego wszystkie trzy części PETG dostały
płaskie podcięcie do X159,3, z nominalnym odstępem 0,3 od ściany X159.
Oś, otwory mocujące, orczyk i łożyska nie zostały przesunięte. Każda bryła
jest porównywana z dokładnie tym zamierzonym podcięciem, a nie z niezmienionym R1.

Szkice i kieszenie powstały przez MCP. Jest 21 w pełni związanych szkiców.
Ścisłe BOP, jedna bryła na część, niezależna oczekiwana różnica brył i otwarcie
w nowym katalogu są sprawdzane w [audycie serwisu](service-audit.json).

## Dostęp i kolejność montażu

- Wyjmowanie nakrętki: 73 pozycje co 0,25 mm, od Y12 do Y−6, bez wykrytych
  przecięć, po wyjęciu śruby osi `SpindleBolt34`. Pozostałe nominalne części
  uwzględniono. To nie model palców, chwytaka ani ciągła obwiednia nakrętki.
- Wkrętak: cylindryczna obwiednia grotu Ø2,5 / Ø3 przechodzi osiowo przy
  usuniętej śrubie i nakrętce osi; minimalny luz przy czopie 0,45 / 0,20 mm.
  Dla Ø6 są kolizje, więc poprzedni negatywny wynik pozostaje prawdziwy.
- Wymiary nie są zgadywane: [Wera 2050 PH](https://www.wera.de/en/tools/2050-ph-screwdriver-for-phillips-screws-for-electronic-applications)
  podaje 05118020001: PH00, trzpień Ø2,5, długość 60; 05118022001: PH0,
  Ø3, długość 60 (PH0 zmodyfikowany wg JCIS0). Sprawdzono 23.09.2026.
  **Nie znamy gniazda śruby konkretnego orczyka**, więc to kandydaci do testu
  przestrzeni, nie zatwierdzony dobór końcówki. Nie modelowano uchwytu ani dłoni.
- Dostęp od spodu do wszystkich czterech łbów M2 po założeniu adaptera jest
  blokowany przez serwo i wspornik. Nie oznaczono tych prób jako zaliczone.
- Kandydat kolejności: skręcić adapter z orczykiem na stole, poza serwem;
  śrubę fabrycznego orczyka włożyć wcześniej, jeśli jej łeb nie przechodzi przez
  otwór czopa; nasunąć gotowy adapter przed górnym blokiem łożysk; dokręcić
  orczyk przez czop; dopiero potem zamontować nakrętkę/śrubę osi i resztę ogona.

[Próba nasuwania](installation-audit.json) sprawdza 13 wysokości od +36 do
0 mm co 3 mm: po podcięciu bez wykrytych kolizji. Kontrole dodatnie na
geometrii sprzed podcięcia wykrywają zahaczanie o wspornik. Jawnie wyłączony
jest górny blok i jego potomkowie. Wałek serwa
pozostaje na miejscu mimo starego TEMP łączącego go logicznie z ogonem.
Pominięta jest wyłącznie para referencyjny orczyk–wałek: model społecznościowy
nie zawiera otworu wieloklinu i nie może dowieść pasowania. Wynik tej próby
nie zatwierdza wkładania rzeczywistej śruby ani montażu górnego bloku.

## Natywne połączenia

`CartridgeBenchAssembly` ma 11 części, 10 **Fixed** i jedną część uziemioną.
Kontener powstał narzędziem MCP. Natywne jointy korzystają z jawnych ramek
odniesienia przez wersjonowane API, ponieważ narzędzie MCP do parowania ścian
nie pozwala zachować takich ramek bez przestawiania części.

[Audyt solvera](joint-audit.json): każdy z 10 elementów kolejno przesuwano
o (0,8; −0,5; 0,6) mm i obracano o 3°. Solver odtworzył położenia, sprawdzono
szczeliny i orientacje wszystkich połączeń oraz powrót geometrii. To natywny
test utrzymania skręcanego stosu, **nie symulacja napędu ogona**. Orczyk jest
niepołączoną referencją poza złożeniem; nie dodano fałszywego sprzęgła do serwa.

## Pozostało

Cienkie ścianki R1 (0,8/0,9 mm i dach 1,65 mm) nadal wymagają dopracowania;
nie pogrubiano ich bez sprawdzenia miejsca na sąsiednie części. Nowy kanał
wymaga osobnej oceny nośności. Rzeczywisty orczyk i śruba, tolerancje,
PETG/profil, uchwyt narzędzia, przewód, dalsze trajektorie montażowe, integracja
i ruch całego ogona pozostają otwarte. Wyniki Gazebo nie zostały zmienione.

Model referencyjny orczyka zachowuje pochodzenie Alberto / otrebla333, Dtto
v2.0.1 i CC BY-SA 4.0; [licencja i opis zmian](../tail-cartridge/README.md#referencja-orczyka-i-licencja).
Nie zmieniono pozostałej geometrii orczyka ani źródłowego projektu Dtto.
