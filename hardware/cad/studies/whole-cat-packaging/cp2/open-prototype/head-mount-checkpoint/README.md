# Aktualna głowa i szyja CP2, zakres M2

Jeden nominalny zestaw przygotowania mechanicznego, nie fizyczny PASS.
Model bieżący: `HeadNeckCurrent.FCStd`. Głowa przesunięta jako cały moduł
42mm do przodu i25mm w górę. Zachowano wklęsłe uszy E6 i wymienne
prowizoryczne drukowane adaptery MG92B. Nie przeprojektowano produktu kupnego.

19 dotychczasowych części głowy, dwa adaptery i dwie podpory szyi:
23 wydruki/22 geometrie; jeden z trzech adapterów należy już do ogona M3.
Nie drukować starego FixedDeckTie dla wiązki jako części M2.
Wszystkie eksporty z marginesem5mm na stronę mieszczą się w256³.
Slicer, materiał, docisk i przymiarki pozostają w fazie2.

## Kolejność montażu

1. Przy niepodłączonym zasilaniu przygotować gołą ramę P0. Dolne cztery
   M2x10 wprowadzić od spodu, z podkładką pod łbem i pod nakrętką.
   To istniejące cztery przednie śruby, nie drugi zestaw ramy.
2. Osadzić obie podpory. Górne cztery M2x12 i nakrętki wprowadzić przed
   zamontowaniem zespołu yaw; po dwie podkładki na śrubę. Łącznie szyja:
   16podkładek, z czego8 dolnych istniejących P0 i8 górnych nowych.
   Boczny dostęp zgodnie z zachowanym dowodem
   neck-support/mount-check-corrected.json. Stare górne M2x14 pominąć.
3. MAIN osadzić na lewym wsporniku zgodnie z dotychczasową kolejnością,
   oddzielnymi2M2x12/2nakrętkami/4podkładkami. Zachować worldZ46,52.
4. Głowę budować na stole zgodnie z12 zachowanymi grupami nominalnego kitu
   head-fastener-kit-r1. Nos/czop, połówki przodu, wkładki i uszy E6 przed
   zamknięciem tyłu. Klatkę pitch z serwem i adapterem, nośnik z widłami,
   następnie yaw z łożyskiem i adapterem; szczęki współobracają się z yaw.
   Retainery zamknąć po wprowadzeniu elementów, nie zakładać dostępu do
   zasłoniętych nakrętek po pełnym montażu.
5. Cały moduł umieścić na przygotowanej szyi. Ruch nominalny yaw±15°,
   pitch−10..+5° jest zakresem próbek CAD, nie zatwierdzonym ruchem sprzętu.
   Wymiar i śruba osi MG92B wymagają przymiarki. Nie włączać napędów.
6. Demontaż mechaniki w kolejności odwrotnej; podtrzymać głowę przed
   rozłączeniem górnych śrub. Obsługa połączeń przewodowych nie jest
   dowiedziona przez tę instrukcję: W2/W3/W5 pozostają otwarte.

## Dowody i uczenie podejścia

Wspólne położenie:9 próbek/72 rzeczywiste bliskie pary,0kontaktów.
Nie powtarzano starych prób wnętrza; zachowano przypięte wyniki i sprawdzono
tylko aktualny interfejs. Native części drukowanych pozostają edytowalne,
referencje kupne zachowują zapisane bryły. Wszystkie linki mają lokalne cele.
Niezależnie otwarta przeniesiona kopia sprawdza parametry głowy i MAIN4→5→4.

Nieudane próby narzędzia nie oznaczały kolizji CAD: struktura Body/Group,
zły master szyi, dokument niezapisany przed kopiowaniem, przebudowa krzywych
serwa i porównanie pointerów zamiast geometrii. Izolowany test kupnej
referencji przed ponowną budową ograniczył koszt. Nie przebudowywać kupnych
referencji tylko w celu relokacji; nie uznawać identyczności bbox za dowód.
Rzeczywiste czasy procesów i początek pracy zapisano w selection.json;
bieżący score, odrzucenia i decyzje w HOBBY_COMPLETION_PLAN.md.
