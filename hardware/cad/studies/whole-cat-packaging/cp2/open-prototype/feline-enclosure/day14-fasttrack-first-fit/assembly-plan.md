# WAVEGO + kot Oli — jeden układ do oceny przymiarki

**Wynik:** zapisany cały układ, bez skalowania bazy i bez dawnych chwytów N01. To koncepcja do jednej oceny całego montażu, nie gotowy wydruk ani fizyczny PASS. Płyta 265 × 164 mm dzieli się na 135 i 130 mm; dwie listwy korzystają z ośmiu istniejących pionowych otworów. Obrys grzbietu ma około 285 × 180 mm. Głowa, uszy i ogon nawiązują do zdjęcia Oli; nogi pozostają widoczne.

Na dole są 16 WAGO danych i 4 WAGO zasilania, głośnik oraz zdejmowana tacka baterii 106,5 × 35 × 21,5 mm z dwiema opaskami. Po bokach stoją dwa otwarte banki po sześć kompletnych oprawek silników z TE IN/OUT i ATO. Cztery niezależne zabezpieczone przewody 220 mm pozostają całe. Z przodu osobno F0; z tyłu pełny S0 na wspólnym panelu, S1, monitor i pięć oprawek pomocniczych. Pi/BUS, właściwy Adafruit815, E1 i oba Pololu mają wspólną górną ramę. ReSpeaker jest na zdejmowanym grzbiecie, kamera/ToF w głowie, BNO/amp/touch we wskazanych miejscach.

## Składanie przez dwie osoby

1. A: zgodność ośmiu mocowań WAVEGO, dwie listwy i dwie połówki płyty. B: przygotowanie istniejącej wiązki na stole, bez nowych cięć, lutowania na PETG lub zmian zabezpieczeń.
2. Przy otwartej górze: dolne WAGO, pełne oprawki/końcówki, głośnik i czujnik. Dostęp do dźwigni przed tacką baterii.
3. Wspólna rama/półki, izolowane mocowania PCB, Pi i pozostałe płytki. Założyć złącza i odciążenia przed zamknięciem sąsiednich warstw. Pełny USB500 z wybranym Delockiem, fabryczne końce GPIO/MTA i właściwe przydziały K1474 zostają.
4. Panel S0, terminale i osłona elektryczna, S1, bezpieczniki i monitor. Obciążenia na panel/ramę, nie na przewody. Potem tacka, paski i odłączona bateria.
5. Wsporniki głowy/ogona, trzy MG92B, trzy 608 i jeden 688. Ułożyć przewody i pętle ruchowe w otwartych regionach; sprawdzić na prawdziwych złączach i ruchu, nie sztywnych ilustracjach każdej żyły.
6. Osłony kosmetyczne na końcu. Do baterii zdejmujemy grzbiet z mikrofonem i odpinamy XT60/balance; do rzadkiej naprawy dopuszczamy zdjęcie tacki/półki. Brak wymogu szybkiego serwisu.

## Niezbędne proste druki i łączniki — jeszcze do dopracowania

Dwie listwy źródłowych mocowań, dwie połówki płyty z prostym łączeniem, dwa wspólne boczne stelaże/półki, tacka baterii z dwoma poprzeczkami, otwarte wspólne mocowania obu banków, tylny panel ochrony i proste wsporniki głowy/ogona. Docelowo osobne osłony głowy, grzbietu i ogona. Otwory PCB/oporów, osłony terminali i sprzęgła osi są nieukończone. M2.5 do istniejących ośmiu otworów oraz M3/nakrętki/dystanse do nowych druków są planem montażowym: rzeczywiste gwinty, długości i liczba ze stosu do potwierdzenia; bez deklaracji zapasu ani zakupu.

## Trzy próby, które rozstrzygną układ

1. **Baza i obciążenie:** wzornik ośmiu otworów/mała próbka korzenia, zważenie kompletnego zestawu, ręczny ruch wszystkich nóg z płytą. Źródłowo płyta zaczyna się 6 mm nad najwyższym punktem pozycji neutralnej; to nie dowód ruchu ani nośności. Masa dodana 0,9–1,4 kg jest tylko szacunkiem ryzyka, nie obliczoną wartością.
2. **Złącza i ochrona:** przymiarka pełnych banków, WAGO, pięciu par fabrycznych przewodów FHAC≥84,5 mm, czterech osobnych 220 mm, Pi/USB/GPIO, XT60/balance i rozdzielonych przydziałów 210 MAIN/350 Pi. Sprawdzić odciążenia, izolację, R/OD, długości i luzy w otwartych polach. Zapisane oprawki/inne niepełne modele są opisanymi rezerwami instalacji, nie dostarczonym materiałem. Brak wartości cut/installed-fit/slack do czasu próby.
3. **Głowa i wygląd:** jeden otwarty model z prawdziwymi MG92B/łożyskami, ważenie głowy i dźwigni, obrót z CSI oraz wzornik sylwetki. Rewizje modułów audio/czujników i rzeczywiste przyłącza wymagają tej samej lokalnej przymiarki; nie rozpoczynamy audytu katalogu.

Dokładny dobór 57 pozycji CSV jest zachowany w `selected-parts-allocation.csv` i `layout.json`; drobne elementy E1, bezpieczniki, pierścienie, złącza i rezystory przy końcach są rozliczone funkcjonalnie, bez fikcyjnych dodatkowych modułów. Kamera/audio/czujniki to jawne rozszerzenie użytkownika poza obecną listą elektryczną; integracja pozostaje otwarta. Stare badania i negatywy pozostają historią, bez przenoszenia flag PASS do nowych pozycji.
