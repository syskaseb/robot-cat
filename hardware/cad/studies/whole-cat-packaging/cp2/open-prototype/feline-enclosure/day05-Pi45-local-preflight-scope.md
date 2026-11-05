# Pi45 — zakres pierwszej lokalnej bramki (tylko dokument)
**Decyzja: odrzucona obecna alokacja T_EP; bramka kotwy Pi zablokowana. N01 0/10.** Bez CAD/native/testów, nowego wariantu, recenzji lub aktywacji hooka.

**Materiał podpory.** Konstruktor `feline_shared_pi_carrier.py:86,198` wiąże dawny `CurrentFoundation:RetainedPWMCarrier` z `ShelfPWM:carrier` (źródłowa kontrola różnicy objętości <1e-5). Dawna kotwa [-32.678718,-65.882055,88.939048], common18.692074mm³ dotyczy poprzedniego ramienia. `build-underdeck.py:38–39` tworzy natomiast `Underdeck:RestoredBank` z **BankBedCurrent:-1**; późniejszy OpenSupport go wycina/uzupełnia. Metadane nie dowodzą tożsamości ani zachowania materiału dawnej kotwy. **Nie budować nowych wsporników przed ustaleniem rzeczywistego rodzica i obu połączeń szyn.**

**North.** Bieżący aktor `CurrentNorth:Common:print` pochodzi z NorthOpenEntry. Historyczny dolny most [-7,91.35,76.95]..[5,93.35,78.95] nie dowodzi nowego połączenia; actualface ROI X32..48/Y86..96/Z72..100=[] pozostaje negatywem. Dokładne archiwa, wpisy i SHA poniżej/w JSON.

**T_EP — statyczny kontrprzykład rodzica.** Pięć Ø1.4, gap.2/edge.4: szerokość8.6; pitch1.6; przesunięcia środków [-3.2,-1.6,0,1.6,3.2]. R środka13 daje R żył [9.8,11.4,13,14.6,16.2]: 9.8<10 o.2mm. Pełna rezerwa portali: Xmax111.3>111 i Ymin−49.3<−49 o.3mm. To błąd przyjętej pojemności/marginesu, **nie kontakt żył**. Odrzucony tylko ten płaski pięciożyłowy zakrętR13, nie każda możliwość Pi45. Bez proponowania korekty kształtu.

**Minimalne wejścia i sąsiedzi.** Pełny kupny Pi+porty/mating/hardware po [0,−45,0], yaw0; current1292 z override/retire-list; rzeczywisty materiał banku/North i obu nowych szyn (mapowanie/połączenia brak); pełne connector/tool sweeps; North12+GPIO/SOURCE/head stock/końce; BodyOuter/MAIN46.52 i zapisane wymagane pozy. Z pełnej sceny wybrać wszystkie całe aktory o bbox-distance≤1.25 od sumy tych obszarów, także w wymaganych pozach; rodziców/fastenery/końce i obsadę zawsze. Bbox to filtr, nie kontakt; brak wymiarów uniemożliwia kompletną ekstrakcję.

**Przyszłe kryteria.** Foreign: valid operands, common0 i gap≥1.25; obrys≥3.25. Kotwy: nazwany rzeczywisty rodzic, dodatnie połączenia (>1e-6mm³ tylko próg numeryczny), ciągły materiał i pełna powierzchnia nośna; wymagany przekrój/nośność nieustalone→HOLD. Pełny profil i R każdej żyły zgodne z kontraktem; zachowane factory/stock/real9, długości i luz. Pełne dojście montażowe bez kontaktu i cyklu zależności. Nie jest to odbiór N03/N08/N09.

**Balance.** Cztery logiczne BAT.B0..B3→P309 poza123; N01 potrzebuje wymiarów złącza/modułu, izolowanej drogi, retencji i długości. Cavity/pinout/polaryzacja to nierozstrzygnięta faza2; ID nie identyfikuje fizycznej komory. Brak dostawczych wymiarów nadal blokuje zajętość mechaniczną; bez prac zasilania.

- `Underdeck:RestoredBank`: `day30-astra-open-support-bank.breps.zip::open-bank/changed-bank.brep`; archive SHA `e21a7337a6d15f36f15f3c4ed09976fa30079c0459c2a91818f1abb20182180c`; member SHA `4a19b9f1c1a70238a19bb293e60db6ca1dfd425caab6a454a28406c88473a888`.

- `CurrentNorth:Common:print`: `day31-astra-north-open-entry.breps.zip::0.brep`; archive SHA `62b3598df7562284af55193a170c27d1ffa69b340ee2b0d95f1256d1ebb7efa4`; member SHA `25850bd705cc467b3559baa045c3963dce66e53a97f638e6046867a26918b18e`.
