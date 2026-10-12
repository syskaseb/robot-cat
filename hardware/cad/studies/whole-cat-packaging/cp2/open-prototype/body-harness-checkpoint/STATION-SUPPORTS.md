# Wspólne podparcie 12 stacji, kandydat do pełnej wiązki

Jeden model `StationFramesCurrent.FCStd`: cztery wymienne ramki oraz jedna
Foundation z integralnymi krótkimi podporami FL D/G. Zachowano wszystkie
pozycje i sieci 12 złączek. To nie jest wybór całej wiązki ani ukończenie W5.

Ramki mają rzeczywiste oparcie po 95,015 mm² na spodzie istniejących bossów
P0, Z=-2 mm. Cztery M3x16, cztery nakrętki i cztery podkładki; nakrętki w
istniejących górnych kieszeniach włożyć przed dolnym nośnikiem i przewodami.
Nie wiercić P0. Foundation zachowuje cały poprzedni materiał; tylko nowe
podpory są tu natywnie edytowalne, odziedziczona baza jest jawnie snapshotem.

Próba ruchu odrzuciła poprzednie dolne ramię FR_G: zahaczało o kolano.
Nowa wspólna droga korzysta ze wschodniego ramienia FR_P i powrotu po stronie
zewnętrznej. Nie wycięto nogi, przewodu ani miejscowego obejścia świadka.

Dowody: `data-ground-mounts-plan.json`, `station-frames-motion.json` oraz
`station-frames-native.json`. Pełne identyczne BRep pozwoliły zachować wyniki
40 niezmienionych brył; 63 zmienione pary statyczne bez kontaktów/błędów.
108 pozycji nóg i dziewięć pozycji głowy bez kontaktów z nowymi mocowaniami.
Próbki nie są dowodem ciągłego sweepu. Odrzucona rodzina kabli przegubowych
nie jest wybrana ani kwalifikowana przez ten wynik.

Pięć brył, 103 związane szkice, parametr tylnej ścianki 5,5 -> 5,7 -> 5,5 mm,
przeniesione ponowne otwarcie i pięć zamkniętych, jednoskładnikowych STL.
Każdy eksport mieści się w 256³ mm z brimem 5 mm po każdej stronie.
Obliczenia kompletu ruch/CAD/eksport: 640,922 s. Trzy testy styku: 0,023 s.

Obecne cztery stare mocowania P są NIE WYBRANE i nie zapewniały górnego
oparcia na rzeczywistej krawędzi P0. Ten zestaw zastępuje ich rolę, nie dodaje
drugiego kompletu. Aktualnego wybranego Foundation jeszcze nie podmieniono.

Otwarte: niezależne chwyty izolacji i pełne wachlarze przewodów, rzeczywiste
dźwignie, wspólny montaż i stock. Retencja złączek pozostaje prowizorycznym
klejeniem dolnej/tylnej obudowy; nie jest odciążeniem kabla. Próba dostarczonych
złączek, adhezji/odklejania, obrotu stopy, sztywności i pełzania PETG należy do
fazy 2. Nominalny osprzęt nie zastępuje doboru SKU w K2. Bez slicera, druku,
zakupów, zasilania ani fizycznego PASS. Wynik całej fazy nadal 12/20 = 60%.
