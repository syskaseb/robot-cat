# Jedna próbka panelu MTA0300330

**Tylko beznapięciowa przymiarka na stole.** Nie jest to mocowanie banku do ramy ani odbiór całego kota. Bieżący carrier pozostaje4f9ce00a; stopaMAIN/AUXce9a55c1 jest odłożonymHOLD i nie została włączona do tego modelu.

## Co wydano

1×`MTA0300330_PANEL2_REFERENCE_COUPON.stl`, PETG,44×30×2mm, płasko/Z0, zamknięty i dodatni. Otwór **22,2×11,3mm** jest nominalny dla panelu2mm z rysunkuMTA B0-100.E10A; b ma tolerancję+0,3/−0. Nie dodano ukrytego luzu drukowego. Zmierzyć rzeczywisty otwór i grubość próbki, nie wciskać na siłę. Brak nowych śrub/adapteraDIN/zakupów. Nie wykonywano druku ani slicingu.

`panel-template-1to1.svg` drukować100%, bez dopasowania do strony; najpierw sprawdzić odcinek50mm. Kontur44×30 to próbka,22,2×11,3 to otwór, przerywany28×15 to nominalny kołnierz, nie linia cięcia. Tylko jeden rozmiar, nie siatka wariantów.

## Co rzeczywiście wiemy o oprawce

W obecnym CAD plastikMTA jest pudełkiem28×15×28,5mm o6ścianach. **Nie zawiera rzeczywistego kołnierza ani sprężystych zaczepów.** Zespół obejmuje też osobno pełne polaTEIN/TEOUT iATO; jego71,43mm nie jest wysokością plastikowego korpusu. Nie wolno przyjmować BBox całego zespołu jako płaszczyzny panelu. Rysunek producenta jestONLY FOR REFERENCE, nie certyfikatem pasowania dostarczonej części.

Powiązanie nominalne:28,5mm od góry kołnierza do spodu plastiku; kołnierz2mm, panel2mm — spod panelu plastik schodzi24,5mm. W bieżącym źródle jest to odpowiednioZ104,63/102,63/100,63; są to datums referencyjne przyłożone do pudełka, NIE wykryte w CAD powierzchnie zatrzasków. Na osobnej prezentacji stołowej panelZ100..102, kołnierzpodstawa102/góra104. Transformacja i4pełne źródłowe części zapisane wJSON.

Nominalny kołnierz28×15 daje przy otworze22,2×11,3 szerokości oparcia2,9 i1,85mm oraz planarea169,14mm². Rzeczywiste stykanie, zatrzask, tolerancje i siła zacisku pozostają do sprawdzenia. Wspólny materiał pudełka i próbki338,28mm³ to nadmiar uproszczonego coveru, **nie dowód kolizji prawdziwego plastiku**. Nie wycięto oprawki ani nie udawano dokładnych zaczepów.

## Kolejność dwóch osób — jeden rzeczywisty wariant

1. Pracować na odłączonym komplecie, bez źródła zasilania. Pierwsza osoba trzyma próbkę za zewnętrzny brzeg, pozostawiając cały spód i oba końce zaczepów dostępne. Druga ma MTA0300330 z jego dwoma fabrycznymi stykami wewnętrznymi. Niczego z oprawki nie wypinać.
2. **Początkowo osadzić samą oprawkę w panelu od strony kołnierza.** Sprawdzić przyleganie całego kołnierza i oba sprężyste zaczepy od spodu. Bez wymuszania/ściskania izolatorów. Na wolnym kuponie nie ma ramy/banku zasłaniającego oględziny i dojście do zaczepów; ich dokładna geometria/releaseforce jest fizycznymFIT, nie zamodelowanymPASS.
3. Dopiero po osadzeniu oprawki nasunąć od spodu **obie kompletne żeńskie końcówkiTE**, każdą z zachowanym przewodem i przeciwległym końcem. Nie chodzi o wpychanie żeńskichTE do wnętrzaPA66 ani wyjmowanie stykówMTA. Źródła identyfikująMTA0300330 ze stykami oraz osobneTE6,35×0,81female; to początkowe zestawienie rzeczywistych części, nie fikcyjne odłączenie gotowej wiązki. Głębokośćnasunięciae i wzajemne dopasowanie izolatorów trzeba zmierzyć na1komplecie. Jeżeli rzeczywisty dostarczony komplet jest już trwale okablowany i ta kolejność jest niemożliwa, **STOP: zapisać konkretny wymiar/ograniczenie**; nie przeciągać go na siłę i nie rozcinać przewodów.
4. Przewody ułożyć swobodnie pod próbką; drugi człowiek podtrzymuje cały połączony kit. INLAPP0107001 ma projektowyOD3,1/R12,4 i max100mm, a nie potwierdzony factoryblank. OUT ma rzeczywisty przewód serwa z zachowanym końcem; jego przekrój/długość wymagają właściwegoFIT. Niczego nie ciąć/przedłużać ani nie zmieniać procesu zacisku. Cztery chronione niezależne220 i wszystkie końce pozostają bez zmian.
5. WkładkęATO4A wkładać na końcu od góry, obejrzeć osadzenie i dostęp. To nadal przymiarka mechaniczna bez zasilania, bez odbioru styków/ochrony/siły wyrywania.

Nie deklarujemy, że cały sztywny zespół71,43mm przechodzi otworem. Projekcja dwóch zmontowanychTE ma21,8486mm w krótkim kierunku przy otworze11,3mm — prosty wspólny dropin nie jest przyjęty. Poszczególne nominalne polaTE są mniejsze od otworu, ale to nie dowód dowolnej ścieżki/manualnej próby; wybrana kolejność w ogóle nie wymaga przeciskania razem nasuniętychTE.

## Pliki i granice wyniku

`mta-panel-trial.FCStd`: currentcarrier/sourcepełne12oprawek w2rzędach po6 bez zmian, plus jedna jawna kopia tej samej oprawki przy próbce NA STOLE, nie13. pozycjaBOM. AUXpełne9,5 zaznaczone jakoOPENcontext, nie potwierdzenie starej płytki. `whole-current-context-and-bench.png` i `actual-whole-unit-interface.png` są rzeczywistymi widokami CAD. Magenta to nominalne płaszczyzny kołnierza, przezroczysty korpus to sourceallocation, nie dokładny zakupiony plastik. `actual-unit-and-panel-section.png`/JSON pokazują rzeczywiste zachowane bryły i jedno źródłowe okno.

Źródła/sha w `source-pins.json`, części/ilości w `parts.csv`. Rootbanku i retencja wszystkich12 oprawek nie są w tym zadaniu kwalifikowane. PhysicalPASSfalse, wholekitfalse, actualfit/cut/slackNULL. Dalej tylko odbiór i konsolidacja plików przez parenta — bez kolejnej rodzinyCAD tej nocy.
